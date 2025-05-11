from typing import Any, Dict, List, Optional
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import pandas as pd
import tensorflow_text


class DataPipeline:
    def __init__(self, model_url: str = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3",
                 batch_size: int = 64) -> None:
        """
        Initialize the data pipeline with a TensorFlow Hub model and batch size.

        Args:
            model_url (str, optional): URL to the TensorFlow Hub model. Defaults to the multilingual USE.
            batch_size (int, optional): Batch size for dataset processing. Defaults to 64.
        """
        self._batch_size = batch_size
        self._model = hub.load(model_url)
        self._dataset = None  # type: Optional[tf.data.Dataset]
        self._embeddings = None  # type: Optional[np.ndarray]
        self._metadata = None  # type: Optional[pd.DataFrame]
        self._texts = None  # type: Optional[List[str]]

    @property
    def embeddings(self) -> Optional[np.ndarray]:
        """
        Get the computed embeddings.

        Returns:
            Optional[np.ndarray]: The embeddings array.
        """
        return self._embeddings

    @property
    def metadata(self) -> Optional[pd.DataFrame]:
        """
        Get the metadata associated with the texts.

        Returns:
            Optional[pd.DataFrame]: The metadata.
        """
        return self._metadata

    @property
    def texts(self) -> Optional[List[str]]:
        """
        Get the list of texts.

        Returns:
            Optional[List[str]]: The texts.
        """
        return self._texts

    def load_tsv(self, file_path: str, text_column: str = "Lyrics", metadata_columns: Optional[List[str]] = None) -> tf.data.Dataset:
        """
        Load data from a TSV file and create a TensorFlow dataset.

        Args:
            file_path (str): Path to the TSV file.
            text_column (str, optional): Column name for text. Defaults to "Lyrics".
            metadata_columns (Optional[List[str]], optional): List of metadata column names. Defaults to None.

        Returns:
            tf.data.Dataset: The resulting TensorFlow dataset.
        """
        if metadata_columns is None:
            metadata_columns = []

        columns_to_use = [text_column] + metadata_columns
        df = pd.read_csv(file_path, sep="\t", usecols=columns_to_use, encoding="utf-8")
        self._texts = df[text_column].astype(str).tolist()

        if metadata_columns:
            self._metadata = df[metadata_columns]
        else:
            self._metadata = pd.DataFrame({'index': range(len(self._texts))})

        self._dataset = tf.data.Dataset.from_tensor_slices(self._texts)
        self._dataset = self._dataset.batch(self._batch_size).prefetch(tf.data.AUTOTUNE)
        return self._dataset

    def compute_embeddings(self, dataset: Optional[tf.data.Dataset] = None, normalize: bool = True) -> np.ndarray:
        """
        Compute embeddings for the dataset using the loaded model.

        Args:
            dataset (Optional[tf.data.Dataset], optional): Dataset to compute embeddings from. Defaults to None.
            normalize (bool, optional): Whether to L2 normalize the embeddings. Defaults to True.

        Returns:
            np.ndarray: Array of computed embeddings.
        """
        if dataset is None:
            dataset = self._dataset
        all_embeddings = []
        for batch in dataset:
            embeddings = self._model(batch)
            if normalize:
                embeddings = tf.nn.l2_normalize(embeddings, axis=1)
            all_embeddings.append(embeddings)
        self._embeddings = tf.concat(all_embeddings, axis=0).numpy()
        return self._embeddings

    def save_embeddings(self, file_path: str) -> None:
        """
        Save the computed embeddings to a TFRecord file along with a schema.

        Args:
            file_path (str): Path to save the TFRecord file.
        """
        if self._embeddings is None:
            raise ValueError("No embeddings to write")
        if self._texts is None:
            raise ValueError("No text data available")

        import os
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)

        with tf.io.TFRecordWriter(file_path) as writer:
            for i, (text, embedding) in enumerate(zip(self._texts, self._embeddings)):
                if self._metadata is not None:
                    metadata_row = self._metadata.iloc[i]
                else:
                    metadata_row = pd.Series({'index': i})

                example = self._create_example(text, embedding, metadata_row)
                writer.write(example)

        schema = {
            'embedding_size': self._embeddings.shape[1],
            'has_text': True
        }
        if self._metadata is not None:
            schema['metadata_columns'] = list(self._metadata.columns)
            for col in self._metadata.columns:
                dtype = self._metadata[col].dtype
                if np.issubdtype(dtype, np.integer):
                    schema[f'dtype_{col}'] = 'int'
                elif np.issubdtype(dtype, np.floating):
                    schema[f'dtype_{col}'] = 'float'
                else:
                    schema[f'dtype_{col}'] = 'string'

        schema_path = file_path + '.schema.json'
        import json
        with open(schema_path, 'w') as f:
            json.dump(schema, f)

        print(f"Saved embedding to {file_path} in TFRecord format")
        print(f"Saved schema to {schema_path}")

    def load_embeddings(self, file_path: str) -> np.ndarray:
        """
        Load embeddings and metadata from a TFRecord file using the associated schema.

        Args:
            file_path (str): Path to the TFRecord file.

        Returns:
            np.ndarray: The loaded embeddings array.
        """
        import json
        schema_path = file_path + '.schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        embedding_size = schema['embedding_size']
        metadata_columns = schema.get('metadata_columns', ['index'])
        has_text = schema.get('has_text', False)

        def _parse_function(example_proto: tf.Tensor) -> Dict[str, tf.Tensor]:
            feature_description = {
                'embedding': tf.io.FixedLenFeature([embedding_size], tf.float32)
            }
            if has_text:
                feature_description['text'] = tf.io.FixedLenFeature([], tf.string)
            for col in metadata_columns:
                dtype = schema.get(f'dtype_{col}', 'string')
                if dtype == 'int':
                    feature_description[col] = tf.io.FixedLenFeature([], tf.int64)
                elif dtype == 'float':
                    feature_description[col] = tf.io.FixedLenFeature([], tf.float32)
                else:
                    feature_description[col] = tf.io.FixedLenFeature([], tf.string)
            return tf.io.parse_single_example(example_proto, feature_description)

        raw_dataset = tf.data.TFRecordDataset(file_path)
        parsed_dataset = raw_dataset.map(_parse_function)

        all_embeddings = []
        metadata_data = {col: [] for col in metadata_columns}
        all_texts = []

        for example in parsed_dataset:
            all_embeddings.append(example['embedding'].numpy())
            if has_text:
                text = example['text'].numpy().decode()
                all_texts.append(text)
            for col in metadata_columns:
                val = example[col].numpy()
                if isinstance(val, bytes):
                    val = val.decode()
                metadata_data[col].append(val)

        self._embeddings = np.array(all_embeddings)
        self._metadata = pd.DataFrame(metadata_data)

        if has_text:
            self._texts = all_texts
            print(f"Loaded {len(self._texts)} texts and embeddings of shape: {self._embeddings.shape}")
        else:
            print(f"Loaded embeddings of shape: {self._embeddings.shape}")

        return self._embeddings

    def _create_example(self, text: str, embedding: np.ndarray, metadata_row: Any) -> bytes:
        """
        Create a serialized tf.Example for a single record.

        Args:
            text (str): The text value.
            embedding (np.ndarray): Embedding vector.
            metadata_row (Any): A row from the metadata DataFrame.

        Returns:
            bytes: Serialized tf.Example.
        """
        feature = {
            'text': tf.train.Feature(
                bytes_list=tf.train.BytesList(value=[text.encode()])
            ),
            'embedding': tf.train.Feature(
                float_list=tf.train.FloatList(value=embedding)
            )
        }

        for col in metadata_row.index:
            val = metadata_row[col]
            if isinstance(val, (int, np.int64, np.int32)):
                feature[col] = tf.train.Feature(
                    int64_list=tf.train.Int64List(value=[val])
                )
            elif isinstance(val, (float, np.float64, np.float32)):
                feature[col] = tf.train.Feature(
                    float_list=tf.train.FloatList(value=[val])
                )
            else:
                feature[col] = tf.train.Feature(
                    bytes_list=tf.train.BytesList(value=[str(val).encode()])
                )

        return tf.train.Example(
            features=tf.train.Features(feature=feature)
        ).SerializeToString(deterministic=True)

from typing import Any, Dict, List
from annoy import AnnoyIndex
import tensorflow as tf
from search_engine import DataPipeline
import pickle

def _parse_example(example: tf.Tensor) -> Dict[str, tf.Tensor]:
    """
    Parse a serialized tf.Example into a dictionary of tensors.

    Args:
        example (tf.Tensor): A serialized tf.Example.

    Returns:
        Dict[str, tf.Tensor]: A dictionary mapping feature names to tensors.
    """
    feature_description = {
        'text': tf.io.FixedLenFeature([], tf.string),
        'embedding': tf.io.FixedLenFeature([512], tf.float32)
    }
    return tf.io.parse_single_example(example, feature_description)

class IndexBuilder:
    def __init__(self, n_trees: int = 100, n_dims: int = 512) -> None:
        """
        Initialize an IndexBuilder for building an Annoy index.

        Args:
            n_trees (int, optional): Number of trees to use in the Annoy index. Defaults to 100.
            n_dims (int, optional): Dimensionality of the embeddings. Defaults to 512.
        """
        self._n_trees = n_trees
        self._n_dims = n_dims
        self._index = AnnoyIndex(self._n_dims, "angular")

    @property
    def annoy_index(self) -> AnnoyIndex:
        """
        Get the underlying Annoy index.

        Returns:
            AnnoyIndex: The Annoy index.
        """
        return self._index

    def build_index_from_files(self, embed_files_paths: List[str]) -> None:
        """
        Build the Annoy index from TFRecord files containing embeddings.

        Args:
            embed_files_paths (List[str]): List of file paths to TFRecord files.
        """
        item_counter = 0
        for i, embed_file in enumerate(embed_files_paths):
            print('Loading embeddings in file {} of {}...'.format(i + 1, len(embed_files_paths)))
            dataset = tf.data.TFRecordDataset(embed_file)
            for record in dataset.map(_parse_example):
                text = record['text'].numpy().decode("utf-8")
                embedding = record['embedding'].numpy()
                self._index.add_item(item_counter, embedding)
                item_counter += 1
        print(f"A total of {item_counter} items added to the index")
        self._index.build(self._n_trees)

    def save_to_file(self, file_path: str) -> None:
        """
        Save the Annoy index to a file.

        Args:
            file_path (str): Path to the file where the index will be saved.
        """
        self._index.save(file_path)


    def load_from_file(self, file_path: str) -> AnnoyIndex:
        """
        Load the Annoy index from a file.

        Args:
            file_path (str): Path to the file from which to load the index.

        Returns:
            AnnoyIndex: The loaded Annoy index.
        """
        self._index.load(file_path)
        return self._index

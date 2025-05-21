import unittest
from unittest.mock import patch, MagicMock, mock_open, ANY
import numpy as np
import pandas as pd
import tensorflow as tf
import os
import json
import tempfile
from pathlib import Path

from search_engine.data_pipeline import DataPipeline

class TestDataPipeline(unittest.TestCase):
    
    @patch('search_engine.data_pipeline.hub')
    def setUp(self, mock_hub):
        self.mock_model = MagicMock()
        mock_hub.load.return_value = self.mock_model

        self.data_pipeline = DataPipeline(batch_size=32)

        mock_hub.load.assert_called_once()
        
    def test_init(self):
        self.assertEqual(self.data_pipeline._batch_size, 32)
        self.assertIsNotNone(self.data_pipeline._model)
        self.assertIsNone(self.data_pipeline._dataset)
        self.assertIsNone(self.data_pipeline._embeddings)
        self.assertIsNone(self.data_pipeline._metadata)
        self.assertIsNone(self.data_pipeline._texts)
        
    def test_properties(self):
        self.data_pipeline._embeddings = np.array([[1.0, 2.0], [3.0, 4.0]])
        self.assertTrue(np.array_equal(self.data_pipeline.embeddings, np.array([[1.0, 2.0], [3.0, 4.0]])))

        metadata = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        self.data_pipeline._metadata = metadata
        pd.testing.assert_frame_equal(self.data_pipeline.metadata, metadata)

        self.data_pipeline._texts = ['test1', 'test2']
        self.assertEqual(self.data_pipeline.texts, ['test1', 'test2'])

    @patch('search_engine.data_pipeline.pd.read_csv')
    def test_load_tsv(self, mock_read_csv):
        mock_df = pd.DataFrame({
            'Lyrics': ['text1', 'text2', 'text3'],
            'Artist': ['artist1', 'artist2', 'artist3'],
            'Song': ['song1', 'song2', 'song3']
        })
        mock_read_csv.return_value = mock_df

        dataset = self.data_pipeline.load_tsv('test.tsv', metadata_columns=['Artist', 'Song'])

        mock_read_csv.assert_called_once_with('test.tsv', sep='\t', 
                                             usecols=['Lyrics', 'Artist', 'Song'], 
                                             encoding='utf-8')

        self.assertEqual(self.data_pipeline._texts, ['text1', 'text2', 'text3'])
        pd.testing.assert_frame_equal(self.data_pipeline._metadata, 
                                      mock_df[['Artist', 'Song']])

        self.assertIsNotNone(self.data_pipeline._dataset)
        self.assertIsInstance(dataset, tf.data.Dataset)
        
    def test_load_tsv_no_metadata(self):
        with tempfile.NamedTemporaryFile(suffix='.tsv', delete=False, mode='w') as f:
            f.write("Lyrics\tArtist\ntext1\tartist1\ntext2\tartist2\n")
        
        try:
            dataset = self.data_pipeline.load_tsv(f.name)

            self.assertEqual(self.data_pipeline._texts, ['text1', 'text2'])
            self.assertIsNotNone(self.data_pipeline._metadata)
            self.assertEqual(len(self.data_pipeline._metadata), 2)
            self.assertTrue('index' in self.data_pipeline._metadata.columns)
            self.assertIsNotNone(dataset)
        finally:
            os.unlink(f.name)
    
    @patch('search_engine.data_pipeline.tf.nn.l2_normalize')
    def test_compute_embeddings_with_normalization(self, mock_normalize):
        texts = ['sample text 1', 'sample text 2']
        dataset = tf.data.Dataset.from_tensor_slices(texts).batch(2)
        self.data_pipeline._dataset = dataset
        self.data_pipeline._texts = texts

        embeddings = tf.constant([[0.1, 0.2], [0.3, 0.4]])
        self.mock_model.return_value = embeddings
        mock_normalize.return_value = tf.constant([[0.5, 0.5], [0.6, 0.6]])

        result = self.data_pipeline.compute_embeddings(normalize=True)

        mock_normalize.assert_called_once_with(embeddings, axis=1)
        self.assertTrue(np.allclose(result, np.array([[0.5, 0.5], [0.6, 0.6]])))

    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_embeddings(self, mock_json_load, mock_open):
        mock_json_load.return_value = {
            'embedding_size': 2,
            'metadata_columns': ['Artist', 'Song'],
            'has_text': True,
            'dtype_Artist': 'string',
            'dtype_Song': 'string'
        }

        expected_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
        expected_texts = ['text1', 'text2']
        expected_metadata = pd.DataFrame({
            'Artist': ['artist1', 'artist2'],
            'Song': ['song1', 'song2']
        })

        parsed_examples = []
        for i in range(2):
            example = {}
            example['embedding'] = tf.constant(expected_embeddings[i], dtype=tf.float32)
            example['text'] = tf.constant(expected_texts[i].encode())
            example['Artist'] = tf.constant(expected_metadata['Artist'][i].encode())
            example['Song'] = tf.constant(expected_metadata['Song'][i].encode())
            parsed_examples.append(example)

        mock_dataset = MagicMock()
        mock_dataset_instance = MagicMock()
        mock_dataset.return_value = mock_dataset_instance
        mock_dataset_instance.map.return_value = parsed_examples
        
        with patch('tensorflow.data.TFRecordDataset', mock_dataset):
            result = self.data_pipeline.load_embeddings('input.tfrecord')

            mock_open.assert_called_once_with('input.tfrecord.schema.json', 'r')
            mock_json_load.assert_called_once()

            mock_dataset.assert_called_once_with('input.tfrecord')
            mock_dataset_instance.map.assert_called_once()

            self.assertTrue(np.allclose(result, expected_embeddings))
            self.assertTrue(np.allclose(self.data_pipeline._embeddings, expected_embeddings))

            for i, text in enumerate(expected_texts):
                self.assertEqual(self.data_pipeline._texts[i], text)

            for col in expected_metadata.columns:
                self.assertIn(col, self.data_pipeline._metadata.columns)
    
    def test_create_example(self):
        text = "sample text"
        embedding = np.array([0.1, 0.2, 0.3])
        metadata_row = pd.Series({
            'Artist': 'Test Artist',
            'Year': 2020,
            'Rating': 4.5
        })

        example = self.data_pipeline._create_example(text, embedding, metadata_row)
        

        self.assertIsInstance(example, bytes)

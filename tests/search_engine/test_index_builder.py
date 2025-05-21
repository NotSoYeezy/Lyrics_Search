import unittest
from unittest.mock import patch, MagicMock, call
from search_engine.index_builder import IndexBuilder

class TestIndexBuilder(unittest.TestCase):
    @patch("search_engine.index_builder.AnnoyIndex")
    def test_init_sets_params_and_creates_annoy_index(self, mock_annoy):
        builder = IndexBuilder(n_trees=10, n_dims=256)
        self.assertEqual(builder._n_trees, 10)
        self.assertEqual(builder._n_dims, 256)
        mock_annoy.assert_called_once_with(256, "angular")
        self.assertIs(builder.annoy_index, mock_annoy.return_value)

    @patch("search_engine.index_builder.tf")
    @patch("search_engine.index_builder.AnnoyIndex")
    def test_build_index_from_files_adds_items_and_builds(self, mock_annoy, mock_tf):
        mock_dataset = MagicMock()
        mock_record = {
            'text': MagicMock(),
            'embedding': MagicMock()
        }
        mock_record['text'].numpy.return_value = b"test"
        mock_record['embedding'].numpy.return_value = [0.1] * 512
        mock_dataset.map.return_value = [mock_record, mock_record]
        mock_tf.data.TFRecordDataset.return_value = mock_dataset

        builder = IndexBuilder()
        builder._index = MagicMock()
        builder.build_index_from_files(['file1.tfrecord'])

        calls = [call(0, [0.1]*512), call(1, [0.1]*512)]
        builder._index.add_item.assert_has_calls(calls)
        builder._index.build.assert_called_once_with(builder._n_trees)

    @patch("search_engine.index_builder.AnnoyIndex")
    def test_save_to_file_calls_save(self, mock_annoy):
        builder = IndexBuilder()
        builder._index = MagicMock()
        builder.save_to_file("somefile.ann")
        builder._index.save.assert_called_once_with("somefile.ann")

    @patch("search_engine.index_builder.AnnoyIndex")
    def test_load_from_file_calls_load_and_returns_index(self, mock_annoy):
        builder = IndexBuilder()
        builder._index = MagicMock()
        result = builder.load_from_file("somefile.ann")
        builder._index.load.assert_called_once_with("somefile.ann")
        self.assertIs(result, builder._index)

if __name__ == "__main__":
    unittest.main()

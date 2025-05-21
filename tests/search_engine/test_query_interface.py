import unittest
from unittest.mock import MagicMock, patch
from search_engine.query_interface import QueryInterface

class DummyModel:
    def __call__(self, inputs):
        return [0.1, 0.2, 0.3]

class TestQueryInterface(unittest.TestCase):
    def setUp(self):
        self.annoy_index_mock = MagicMock()
        self.annoy_index_mock.get_nns_by_vector.return_value = [1, 2, 3]
        self.model_mock = MagicMock()
        self.model_mock.return_value = [0.1, 0.2, 0.3]

    def test_init_sets_attributes(self):
        qi = QueryInterface(self.annoy_index_mock, self.model_mock)
        self.assertEqual(qi.annoy_index, self.annoy_index_mock)
        self.assertEqual(qi.model, self.model_mock)

    @patch("tensorflow.squeeze", lambda x: x)
    def test_query_calls_model_and_annoy_index(self):
        qi = QueryInterface(self.annoy_index_mock, self.model_mock)
        result = qi.query("test query", n_items=3)
        self.model_mock.assert_called_once_with(["test query"])
        self.annoy_index_mock.get_nns_by_vector.assert_called_once_with([0.1, 0.2, 0.3], n=3)
        self.assertEqual(result, [1, 2, 3])

    @patch("tensorflow.squeeze", lambda x: x)
    def test_query_default_n_items(self):
        annoy_index = MagicMock()
        annoy_index.get_nns_by_vector.return_value = [4, 5, 6, 7, 8]
        model = DummyModel()
        qi = QueryInterface(annoy_index, model)
        result = qi.query("abc")
        annoy_index.get_nns_by_vector.assert_called_once_with([0.1, 0.2, 0.3], n=5)
        self.assertEqual(result, [4, 5, 6, 7, 8])

if __name__ == "__main__":
    unittest.main()

from typing import List, Any
from annoy import AnnoyIndex
import tensorflow as tf

class QueryInterface:
    def __init__(self, annoy_index: AnnoyIndex, model: Any) -> None:
        """
        Initialize the QueryInterface with an Annoy index and a model for generating embeddings.

        Args:
            annoy_index (AnnoyIndex): The prebuilt Annoy index.
            model (Any): The model used to compute embeddings for queries.
        """
        self._model = model
        self._annoy_index = annoy_index

    @property
    def annoy_index(self) -> AnnoyIndex:
        """
        Get the Annoy index.

        Returns:
            AnnoyIndex: The Annoy index.
        """
        return self._annoy_index

    @property
    def model(self) -> Any:
        """
        Get the model.

        Returns:
            Any: The model used for embedding computation.
        """
        return self._model

    def query(self, query: str, n_items: int = 5) -> List[int]:
        """
        Query the Annoy index based on the input string and return the indices of nearest neighbors.

        Args:
            query (str): The input query text.
            n_items (int, optional): Number of nearest items to return. Defaults to 5.

        Returns:
            List[int]: List of indices of the nearest neighbors.
        """
        query_embedding = self._model([query])
        return self._annoy_index.get_nns_by_vector(tf.squeeze(query_embedding), n=n_items)

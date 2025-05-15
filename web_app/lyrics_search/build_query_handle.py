import os
import tensorflow_hub as hub
from search_engine import IndexBuilder, QueryInterface

def create_query_interface(model_url: str="https://tfhub.dev/google/universal-sentence-encoder-multilingual/3",
                           index_file_path: str="index/index.ann"):
    """
    Args:
        model_url (str) : Link to tf hub embedding model.
        index_file_path (str) : Path to .ann file containing annoy index
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_full_path = os.path.join(os.path.dirname(script_dir), "lyrics_search" ,index_file_path)
    print(index_full_path)
    index = IndexBuilder().load_from_file(index_full_path)
    embedding_model = hub.load(model_url)
    query_interface = QueryInterface(annoy_index=index, model=embedding_model)
    return query_interface
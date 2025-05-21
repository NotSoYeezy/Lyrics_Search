import unittest
from unittest.mock import patch, MagicMock, mock_open
from data_gathering.lyrics_fetcher import LyricsFetcher
import json

class TestLyricsFetcher(unittest.TestCase):

    def setUp(self):
        self.api_token = "fake_api_token"
        self.artists = ["Artist1", "Artist2"]
        self.fetcher = LyricsFetcher(self.api_token, self.artists)

    def test_clean_lyrics(self):
        raw_lyrics = "[Verse 1]\nThis is a line\n[Chorus]\nAnother line\n\n[Outro]\n"
        expected_cleaned = "This is a line\nAnother line"
        result = self.fetcher._clean_lyrics(raw_lyrics)
        self.assertEqual(result, expected_cleaned)

    @patch("builtins.open", new_callable=mock_open, read_data="Artist1\nArtist2")
    def test_from_text_file(self, mock_file):
        fetcher = LyricsFetcher.from_text_file("fake_path.txt", self.api_token)
        self.assertEqual(fetcher._artists, ["Artist1", "Artist2"])
        mock_file.assert_called_once_with("fake_path.txt", "r", encoding='utf-8')

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("data_gathering.lyrics_fetcher.Genius.search_artist")
    def test_fetch_songs(self, mock_search_artist, mock_open_file, mock_makedirs):
        mock_song = MagicMock()
        mock_song.title = "SongTitle"
        mock_song.lyrics = "[Intro]\nLyrics line 1\nLyrics line 2"
        mock_artist_query = MagicMock()
        mock_artist_query.songs = [mock_song]
        mock_search_artist.side_effect = [mock_artist_query, None]
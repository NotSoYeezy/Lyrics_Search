import json
from typing import List
from lyricsgenius import Genius
import re
import os

class LyricsFetcher:
    def __init__(self, api_token:str, artists: None|List[str]) -> None:
        self._artists = artists or []
        self._api_token = api_token

        self._genius = self._set_up()

    def _set_up(self):
        genius = Genius(self._api_token,
                        verbose=True,
                        timeout=30,
                        retries=3)
        return genius

    def _clean_lyrics(self, lyrics: str) -> str:
        cleaned_lines = [line for line in lyrics.split("\n") if not re.match(r"^\[.*\]", line) and line.strip()]
        return "\n".join(cleaned_lines)

    @classmethod
    def from_text_file(cls, file_location: str, api_token: str):
        try:
            with open(file_location, "r", encoding='utf-8') as f:
                artists = f.read().split("\n")
                return cls(api_token, artists)
        except FileNotFoundError:
            print(f"File not found: {file_location}")
            return cls(api_token, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return cls(api_token, None)

    def fetch_songs(self, songs_per_artist: int=10, sort_by: str="popularity"):
        for artist in self._artists:
            artist_query = self._genius.search_artist(
                artist_name=artist,
                max_songs=songs_per_artist,
                sort=sort_by,
            )
            if not artist_query:
                continue  # Skip if no artist data is found
            try:
                for song in artist_query.songs:
                    if not song.lyrics:
                        continue  # Skip if lyrics are missing
                    cleaned_lyrics = self._clean_lyrics(song.lyrics)
                    os.makedirs(f'lyrics/{artist}', exist_ok=True)
                    file_path = f"lyrics/{artist}/{song.title}.json"
                    song_dict = {
                        "title": song.title,
                        "lyrics": cleaned_lyrics
                    }
                    with open(file_path, "w", encoding='utf-8') as f:
                        json.dump(song_dict, f, indent=4, ensure_ascii=False)
            except Exception as e:  # Log the error for debugging
                print(f"Error processing artist {artist}: {e}")
                continue

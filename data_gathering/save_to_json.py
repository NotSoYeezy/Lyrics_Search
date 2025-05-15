"""
This script saves lyrics data to a single JSON file.
Then the script will be used to populate the database. I am using indexing here, which is 
the same as in the dataset used for creating ANNOY index.
"""
import os
import glob
import json


def save_to_json(lyrics_path: str):
    """
    Saves lyrics data do one json file.

    Args:
        lyrics_path (str): Path where folder with lyrics, divided into artists subfolder is stored.
    """
    artists_paths = [x[0] for x in os.walk(lyrics_path)]
    data = []
    i = 0
    for path in artists_paths:
        for song_file in glob.glob(os.path.join(path, "*.json")):
            with open(song_file, "r", encoding="utf-8") as f:
                song_data = json.load(f)
                artist = os.path.basename(path)
                title = song_data["title"]
                data.append(
                    {
                        "artist": artist,
                        "title": title,
                        "lyrics": song_data["lyrics"],
                        "index": i,
                    }
                )
                i += 1
    with open("lyrics.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

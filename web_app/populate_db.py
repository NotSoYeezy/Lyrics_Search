"""
This script populates the database with lyrics data, so then
when similarity will be calculated we can retrieve full lyrics data
from postgresql database.
"""
# from lyrics_search.models import Song
import json
import os
from web_app.lyrics_search.models import Song
from web_app.lyrics_search.extensions import db
from web_app.lyrics_search import create_app

def populate_db_from_json(app, json_path: str):
    """
    Populates Database with data from json file.
    Json structure:
    [
        {
        "artist": "Artist",
        "title": "Title",
        "lyrics": ".....",
        "index": 1,
        }
    ]

    Args:
        app: Flask application instance
        json_path (str): Path do json file.
    """
    with app.app_context():
        with open(json_path, "r") as handle:
            data = json.load(handle)
        for song_data in data:
            artist = song_data["artist"]
            title = song_data["title"]
            lyrics = song_data["lyrics"]
            index = song_data["index"]
            song = Song(
                title=title,
                author=artist,
                lyrics=lyrics,
                index=index,
            )
            db.session.add(song)
            db.session.commit()
            print(f"Added: {song}")
    print("Finished adding to database")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(os.path.dirname(script_dir), "web_app/data_for_population", "lyrics.json")
    app = create_app()
    populate_db_from_json(app, json_path)
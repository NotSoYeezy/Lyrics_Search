import os
import json
import tempfile
import shutil
from data_gathering.save_to_json import save_to_json


def test_save_to_json():
    temp_dir = tempfile.mkdtemp()
    artist_dir = os.path.join(temp_dir, "artist1")
    os.makedirs(artist_dir)
    
    song_data = {
        "title": "Test Song",
        "lyrics": "These are the test lyrics."
    }
    with open(os.path.join(artist_dir, "song1.json"), "w", encoding="utf-8") as f:
        json.dump(song_data, f)

    output_file = os.path.join(temp_dir, "lyrics.json")
    save_to_json(temp_dir, output_file=output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["artist"] == "artist1"
        assert data[0]["title"] == "Test Song"
        assert data[0]["lyrics"] == "These are the test lyrics."
        assert data[0]["index"] == 0

    shutil.rmtree(temp_dir)


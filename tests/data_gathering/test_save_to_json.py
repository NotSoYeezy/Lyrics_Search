import os
import json
import tempfile
import shutil
import unittest
from data_gathering.save_to_json import save_to_json


class TestSaveToJson(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.artist_dir = os.path.join(self.temp_dir, "artist1")
        os.makedirs(self.artist_dir)

        self.song_data = {
            "title": "Test Song",
            "lyrics": "These are the test lyrics."
        }
        with open(os.path.join(self.artist_dir, "song1.json"), "w", encoding="utf-8") as f:
            json.dump(self.song_data, f)

        self.output_file = os.path.join(self.temp_dir, "lyrics.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_save_to_json(self):
        save_to_json(self.temp_dir, output_file=self.output_file)

        self.assertTrue(os.path.exists(self.output_file))

        with open(self.output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["artist"], "artist1")
            self.assertEqual(data[0]["title"], "Test Song")
            self.assertEqual(data[0]["lyrics"], "These are the test lyrics.")
            self.assertEqual(data[0]["index"], 0)

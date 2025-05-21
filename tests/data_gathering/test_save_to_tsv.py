import os
import json
import csv
import shutil
import unittest
from data_gathering.save_to_tsv import save_to_tsv


class TestSaveToTsv(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath("test_env")
        self.lyrics_dir = os.path.join(self.test_dir, "lyrics")
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.lyrics_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        artist_dir = os.path.join(self.lyrics_dir, "TestArtist")
        os.makedirs(artist_dir, exist_ok=True)

        valid_file = os.path.join(artist_dir, "valid.json")
        invalid_file = os.path.join(artist_dir, "invalid.json")
        missing_data_file = os.path.join(artist_dir, "missing_data.json")

        valid_data = {"title": "Test Song", "lyrics": "These are the test lyrics."}
        invalid_data = "{invalid json}"
        missing_data = {"title": "Incomplete Song"}

        with open(valid_file, "w", encoding="utf-8") as f:
            json.dump(valid_data, f)
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write(invalid_data)
        with open(missing_data_file, "w", encoding="utf-8") as f:
            json.dump(missing_data, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_to_tsv_success(self):
        output_tsv = os.path.join(self.output_dir, "all_lyrics.tsv")
        save_to_tsv(file_path=output_tsv, lyrics_dir=self.lyrics_dir)

        self.assertTrue(os.path.exists(output_tsv))

        with open(output_tsv, newline='', encoding='utf-8') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["Artist"], "TestArtist")
            self.assertEqual(rows[0]["Title"], "Test Song")
            self.assertEqual(rows[0]["Lyrics"], "These are the test lyrics.")

    def test_save_to_tsv_handles_invalid_json(self):
        output_tsv = os.path.join(self.output_dir, "all_lyrics.tsv")
        with self.assertLogs(level="ERROR") as log:
            save_to_tsv(file_path=output_tsv, lyrics_dir=self.lyrics_dir)
            self.assertTrue(any("Error: Could not decode JSON" in message for message in log.output))

    def test_save_to_tsv_handles_missing_data(self):
        output_tsv = os.path.join(self.output_dir, "all_lyrics.tsv")
        with self.assertLogs(level="WARNING") as log:
            save_to_tsv(file_path=output_tsv, lyrics_dir=self.lyrics_dir)
            self.assertTrue(any("Warning: Missing 'title' or 'lyrics' key" in message for message in log.output))

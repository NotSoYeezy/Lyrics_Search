import os
import json
import csv
import shutil
import pytest
from data_gathering.save_to_tsv import save_to_tsv

@pytest.fixture
def setup_test_environment(tmp_path):
    # Tworzenie tymczasowego katalogu lyrics
    lyrics_dir = tmp_path / "lyrics"
    lyrics_dir.mkdir()

    artist_dir = lyrics_dir / "TestArtist"
    artist_dir.mkdir()

    valid_file = artist_dir / "valid.json"
    invalid_file = artist_dir / "invalid.json"
    missing_data_file = artist_dir / "missing_data.json"

    valid_data = {"title": "Test Song", "lyrics": "These are the test lyrics."}
    invalid_data = "{invalid json}"
    missing_data = {"title": "Incomplete Song"}

    valid_file.write_text(json.dumps(valid_data), encoding="utf-8")
    invalid_file.write_text(invalid_data, encoding="utf-8")
    missing_data_file.write_text(json.dumps(missing_data), encoding="utf-8")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    return lyrics_dir, output_dir

def test_save_to_tsv_success(setup_test_environment):
    lyrics_dir, output_dir = setup_test_environment
    output_tsv = output_dir / "all_lyrics.tsv"

    # Ustawienie tymczasowego katalogu jako głównego katalogu lyrics
    os.chdir(lyrics_dir.parent)

    save_to_tsv(file_path=str(output_tsv))

    # Sprawdzenie, czy plik TSV został utworzony
    assert output_tsv.exists()

    # Weryfikacja zawartości pliku TSV
    with open(output_tsv, newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Artist"] == "TestArtist"
        assert rows[0]["Title"] == "Test Song"
        assert rows[0]["Lyrics"] == "These are the test lyrics."

def test_save_to_tsv_handles_invalid_json(setup_test_environment, capsys):
    lyrics_dir, output_dir = setup_test_environment
    output_tsv = output_dir / "all_lyrics.tsv"

    # Ustawienie tymczasowego katalogu jako głównego katalogu lyrics
    os.chdir(lyrics_dir.parent)

    save_to_tsv(file_path=str(output_tsv))

    # Sprawdzenie, czy odpowiedni komunikat o błędzie został wyświetlony
    captured = capsys.readouterr()
    assert "Error: Could not decode JSON" in captured.out

def test_save_to_tsv_handles_missing_data(setup_test_environment, capsys):
    lyrics_dir, output_dir = setup_test_environment
    output_tsv = output_dir / "all_lyrics.tsv"

    # Ustawienie tymczasowego katalogu jako głównego katalogu lyrics
    os.chdir(lyrics_dir.parent)

    save_to_tsv(file_path=str(output_tsv))

    # Sprawdzenie, czy odpowiedni komunikat o brakujących danych został wyświetlony
    captured = capsys.readouterr()
    assert "Warning: Missing 'title' or 'lyrics' key" in captured.out


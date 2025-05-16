from data_gathering import LyricsFetcher
import os
import json
import csv
import io


def save_to_tsv(file_path: str = "all_lyrics.tsv"):
    lyrics_dir = 'lyrics'

    if not os.path.exists(lyrics_dir):
        print(f"Error: Directory '{lyrics_dir}' does not exist. Please ensure the directory is present.")
        return

    all_lyrics_data = []

    print(f"Starting to process files in '{lyrics_dir}'...")

    for artist_name in os.listdir(lyrics_dir):
        artist_dir = os.path.join(lyrics_dir, artist_name)
        if os.path.isdir(artist_dir):
            print(f"Processing artist: {artist_name}")
            for filename in os.listdir(artist_dir):
                if filename.endswith('.json'):
                    json_file_path = os.path.join(artist_dir, filename)  # Poprawiona zmienna
                    print(f"  Processing file: {filename}")
                    try:
                        with io.open(json_file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'title' in data and 'lyrics' in data:
                                title = data['title']
                                lyrics = data['lyrics']
                                all_lyrics_data.append({
                                    'Artist': artist_name,
                                    'Title': title,
                                    'Lyrics': lyrics
                                })
                            else:
                                print(f"    Warning: Missing 'title' or 'lyrics' key in {filename}. Skipping.")
                    except json.JSONDecodeError:
                        print(f"    Error: Could not decode JSON from {filename}. Skipping.")
                    except Exception as e:
                        print(f"    Error processing file {filename}: {e}. Skipping.")

    print(f"\nWriting data to '{file_path}'...")
    try:
        with io.open(file_path, 'w', newline='', encoding='utf-8') as tsvfile:
            fieldnames = ['Artist', 'Title', 'Lyrics']
            writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(all_lyrics_data)
        print(f"\nSuccessfully created '{file_path}' with {len(all_lyrics_data)} entries.")
    except Exception as e:
        print(f"\nError writing to TSV file: {e}")


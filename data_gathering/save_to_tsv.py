import os
import json
import csv
import logging


def save_to_tsv(file_path: str, lyrics_dir: str = "lyrics"):
    logging.basicConfig(level=logging.INFO)
    fieldnames = ["Artist", "Title", "Lyrics"]

    if not os.path.exists(lyrics_dir):
        logging.error(f"Error: Directory '{lyrics_dir}' does not exist. Please ensure the directory is present.")
        return

    all_lyrics_data = []

    for artist_name in os.listdir(lyrics_dir):
        artist_dir = os.path.join(lyrics_dir, artist_name)
        if not os.path.isdir(artist_dir):
            continue

        for filename in os.listdir(artist_dir):
            if filename.endswith('.json'):
                json_file_path = os.path.join(artist_dir, filename)
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'title' in data and 'lyrics' in data:
                            all_lyrics_data.append({
                                'Artist': artist_name,
                                'Title': data['title'],
                                'Lyrics': data['lyrics']
                            })
                        else:
                            logging.warning(f"Warning: Missing 'title' or 'lyrics' key in {filename}. Skipping.")
                except json.JSONDecodeError:
                    logging.error(f"Error: Could not decode JSON from {filename}. Skipping.")
                except Exception as e:
                    logging.error(f"Error processing file {filename}: {e}. Skipping.")

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as tsvfile:
            writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(all_lyrics_data)
        logging.info(f"Successfully created '{file_path}' with {len(all_lyrics_data)} entries.")
    except Exception as e:
        logging.error(f"Error writing to TSV file: {e}")

# Polish Lyrics Search Engine

A full-stack application for semantic search of Polish song lyrics using natural language processing and machine learning.

## Overview

This project implements a lyrics search engine that allows users to find Polish songs based on semantic meaning rather than just keyword matching. By leveraging machine learning embeddings, the application can understand the meaning behind search queries and return relevant song lyrics even when exact terms aren't matched.

## Features

* Semantic search for Polish song lyrics
* Web-based user interface with responsive design
* Artist data collection from MusicBrainz and Wikipedia
* Lyrics fetching from Genius API
* Embedding generation using Universal Sentence Encoder
* Fast nearest neighbors search with Annoy indexing
* PostgreSQL database for song metadata storage
* Dockerized deployment for easy setup

## Architecture

The project consists of several key components:

### Data Collection Pipeline

* **ArtistsFetcherMB**: Collects Polish artist data from MusicBrainz API
* **ArtistFetcherWiki**: Extracts artist names from Wikipedia category pages
* **LyricsFetcher**: Retrieves lyrics from Genius API

### Search Engine

* **DataPipeline**: Manages text data processing and embedding computation
* **IndexBuilder**: Creates and manages Annoy vector indices
* **QueryInterface**: Handles search queries and returns relevant results

### Web Application

* Flask backend with SQLAlchemy ORM
* Responsive frontend with Tailwind CSS
* RESTful API endpoints for search functionality

## Technical Stack

* **Backend**: Python, Flask, SQLAlchemy
* **Database**: PostgreSQL
* **Machine Learning**: TensorFlow, TensorFlow Hub, Universal Sentence Encoder
* **Vector Search**: Annoy (Approximate Nearest Neighbors)
* **Frontend**: HTML, JavaScript, Tailwind CSS
* **Containerization**: Docker, Docker Compose

## Setup and Installation

### Prerequisites

* Docker and Docker Compose
* Genius API token (for lyrics fetching)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NotSoYeezy/Lyrics_Search
   cd Lyrics_Search
   ```

2. Configure environment variables:
   * Create a file with your Genius API token and other configurations

3. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Upgrade the database
    ```bash
    docker-compose exec web flask db upgrade --directory="web_app/migrations"
    ```

5. If you want, you can populate the database from provided sample of lyrics
    ```bash
    docker-compose exec web python web_app/populate_db.py
    ```
   * If not, you have to also rebuild the annoy index from scratch when using custom data.

6. Access the web application at http://127.0.0.1:5000

## Data Collection Workflow

1. Fetch Polish artists from MusicBrainz API or Wikipedia
2. Retrieve lyrics for these artists from Genius API
3. Clean and process the lyrics data
4. Convert lyrics to embeddings using Universal Sentence Encoder
5. Build an Annoy index for efficient similarity search
6. Populate PostgreSQL database with lyrics metadata

## Development

### Project Structure
```
├── data_gathering/              # Data collection modules
│   ├── artists_fetcher_mb.py    # MusicBrainz API integration
│   ├── artists_fetcher_wiki.py  # Wikipedia scraping logic
│   ├── descriptors.py           # Property descriptors
│   ├── lyrics_fetcher.py        # Genius API integration
│   ├── save_to_json.py          # JSON serialization utilities
│   └── save_to_tsv.py           # TSV export utilities
├── search_engine/               # Search engine components
│   ├── data_pipeline.py         # Text processing pipeline
│   ├── index_builder.py         # Vector index management
│   └── query_interface.py       # Search API interface
├── web_app/                     # Flask web application
│   ├── lyrics_search/           # Core application code
│   │   ├── static/              # JS, CSS assets
│   │   ├── templates/           # HTML templates
│   │   ├── models.py            # SQLAlchemy models
│   │   └── routes.py            # API endpoints
│   ├── main.py                  # Application entry point
│   └── populate_db.py           # Database initialization
├── tests/                       # Unit tests
├── Dockerfile                   # Docker configuration
├── docker-compose.yaml          # Container orchestration
└── requirements.txt             # Python dependencies
```

### Running Tests

```bash
python -m unittest discover tests
```

### SSH Access

The container exposes SSH access on port 2222 for development purposes:

* Username: root
* Password: Docker!

## Acknowledgments

* MusicBrainz API for artist data
* Genius API for lyrics data
* TensorFlow Hub for the Universal Sentence Encoder model

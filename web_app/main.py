import os

from flask import Flask
from web_app import create_app
from web_app.lyrics_search import extensions

if __name__ == '__main__':
    app = create_app()

    app.run(host='0.0.0.0', port=5000, debug=os.environ.get("DEBUG"))

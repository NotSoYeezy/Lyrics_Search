from flask import render_template, Blueprint, request, jsonify
from .build_query_handle import create_query_interface
from web_app.lyrics_search.models import Song

query_interface = create_query_interface()
bp = Blueprint('routes', __name__, url_prefix="/")

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/query_lyrics", methods=["POST"])
def query_lyrics():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify(error="Missing 'query' in request body"), 400 # Bad request
    query = data["query"]
    try:
        results = []
        result_indexes = query_interface.query(query, n_items=5)
        for i in result_indexes:
            song = Song.query.filter_by(index=i).first()
            if song:
                results.append({
                    "title": song.title.title(),
                    "artist": song.author.title(),
                    "lyrics": song.lyrics,
                })
        return jsonify(results=results)
    except Exception as e:
        print(str(e))
        return jsonify(error=str(e)), 500 # Internal server error

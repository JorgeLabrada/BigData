"""
Music Search Engine – Flask Web Server
Author: Jorge Alfonso Labrada Ramos (vape)
"""

from flask import Flask, render_template, request, jsonify
from search_engine import MusicSearchEngine

app = Flask(__name__)
engine = MusicSearchEngine(corpus_path="corpus.json")


@app.route("/")
def index():
    return render_template("index.html", stats=engine.stats())


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    top_k = int(request.args.get("top_k", 10))
    if not query:
        return render_template("index.html", stats=engine.stats())
    results = engine.search(query, top_k=top_k)
    return render_template("results.html", **results)


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    top_k = int(request.args.get("top_k", 10))
    return jsonify(engine.search(query, top_k=top_k))


@app.route("/api/autocomplete")
def api_autocomplete():
    prefix = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 8))
    suggestions = engine.suggest(prefix, limit=limit)
    return jsonify({"prefix": prefix, "suggestions": suggestions})


@app.route("/index-view")
def index_view():
    data = engine.get_index_data()
    stats = engine.stats()
    return render_template("index_view.html", data=data, stats=stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)

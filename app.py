# app.py
from flask import Flask, request, jsonify, render_template, abort
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh import scoring
import os

# Configuration
INDEX_DIR = os.environ.get("WOLF_INDEX_DIR", "indexdir")
MAX_RESULTS = 50

app = Flask(__name__, template_folder="templates", static_folder="static")

# Privacy-first: disable session cookies and minimize server-side logging
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Strict",
)

def set_privacy_headers(resp):
    # Basic security & privacy headers
    resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    # Explicitly say we don't track
    resp.headers["X-WolfSearch-Privacy"] = "no-collection; no-profiling; no-sales"
    return resp

@app.after_request
def apply_headers(resp):
    return set_privacy_headers(resp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": [], "query": ""})

    if not os.path.exists(INDEX_DIR):
        abort(500, description="Index does not exist. Run the indexer first.")

    ix = open_dir(INDEX_DIR)
    qp = MultifieldParser(["title", "content"], schema=ix.schema)
    parsed = qp.parse(q)

    results = []
    with ix.searcher(weighting=scoring.TF_IDF()) as s:
        hits = s.search(parsed, limit=MAX_RESULTS)
        for h in hits:
            results.append({
                "title": h.get("title") or h.get("path"),
                "snippet": h.get("content")[:400] + ("…" if len(h.get("content", "")) > 400 else ""),
                "path": h.get("path"),
                "score": float(h.score)
            })
    # do not log the query anywhere beyond this response
    return jsonify({"query": q, "results": results})

if __name__ == "__main__":
    # Don't enable debug or extra logs in production — privacy by default
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

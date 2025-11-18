# Wolf Search

Privacy-first, self-hosted search.

## Quick start
1. Put files to index under `docs/` (plain text or HTML).
2. Build index: `python indexer.py`
3. Run server: `python app.py` (or `docker build -t wolf-search . && docker run -p 8080:8080 wolf-search`)
4. Open `http://localhost:8080`

## Notes
- No analytics. No tracking. No data sales.
- To scale, swap Whoosh for Elasticsearch/OpenSearch (see elastic.co). :contentReference[oaicite:3]{index=3}

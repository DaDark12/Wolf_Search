#!/usr/bin/env python3
# scripts/build_index.py
"""
Build documents.json for Wolf Search (client-side).
Usage:
  1. Put HTML/text files under `docs/` (relative to repo root).
  2. Run: python3 scripts/build_index.py
  3. Commit the generated docs/documents.json and push to GitHub.
"""

import os
import json
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(__file__))
DOCS_DIR = os.path.join(ROOT, "docs")
OUTPUT = os.path.join(DOCS_DIR, "documents.json")

def extract_text(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        return None, None

    if "<html" in text.lower() or text.strip().startswith("<!doctype html".lower()):
        soup = BeautifulSoup(text, "html.parser")
        title = (soup.title.string.strip() if soup.title and soup.title.string else os.path.basename(path))
        # get main textual content
        content = soup.get_text(separator="\n").strip()
        # optional: find canonical link or use file path as URL
        url_tag = soup.find("link", rel="canonical")
        url = url_tag['href'] if url_tag and url_tag.get('href') else None
    else:
        title = os.path.basename(path)
        content = text
        url = None
    return title, content, url

def build():
    docs = []
    for root, _, files in os.walk(DOCS_DIR):
        for fn in files:
            if fn.lower() == "documents.json":
                continue
            if not (fn.lower().endswith(".html") or fn.lower().endswith(".htm") or fn.lower().endswith(".txt")):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, DOCS_DIR)
            title, content, url = extract_text(path)
            if content is None:
                print("Skipping (can't read):", path)
                continue
            entry = {
                "title": title,
                "path": rel.replace(os.path.sep, "/"),
                "url": url or ("./" + rel.replace(os.path.sep, "/")),
                "content": content
            }
            docs.append(entry)
            print("Indexed:", entry["path"])
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Written {len(docs)} documents to {OUTPUT}")

if __name__ == "__main__":
    build()

# indexer.py
import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, exists_in, open_dir
from whoosh.analysis import StemmingAnalyzer
from bs4 import BeautifulSoup

INDEX_DIR = os.environ.get("WOLF_INDEX_DIR", "indexdir")
DOCS_DIR = os.environ.get("WOLF_DOCS_DIR", "docs")  # put files to index here

schema = Schema(
    title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    path=ID(stored=True, unique=True)
)

def extract_text_from_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8", errors="ignore")
    except:
        text = str(raw)
    # if HTML, strip tags
    if "<html" in text.lower():
        soup = BeautifulSoup(text, "html.parser")
        title = soup.title.string if soup.title else os.path.basename(path)
        content = soup.get_text(separator="\n")
    else:
        title = os.path.basename(path)
        content = text
    return title, content

def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)
    if not exists_in(INDEX_DIR):
        ix = create_in(INDEX_DIR, schema)
    else:
        ix = open_dir(INDEX_DIR)

    writer = ix.writer()
    count = 0
    for root, _, files in os.walk(DOCS_DIR):
        for fname in files:
            p = os.path.join(root, fname)
            title, content = extract_text_from_file(p)
            writer.update_document(title=title, content=content, path=p)
            count += 1
    writer.commit()
    print(f"Indexed {count} documents to {INDEX_DIR}")

if __name__ == "__main__":
    build_index()

// assets/js/search.js
// Wolf Search — client-side Lunr-based search with URL redirect support
// No analytics. No cookies. All local to the browser.

const qInput = document.getElementById("q");
const resultsEl = document.getElementById("results");
const searchBtn = document.getElementById("searchBtn");
const clearBtn = document.getElementById("clearBtn");

let idx = null;
let docs = [];

// Utility: is the query a URL/domain? returns normalized URL or null
function parsePotentialUrl(q) {
  if (!q) return null;
  q = q.trim();
  // quick tests:
  // contains spaces -> not a URL
  if (/\s/.test(q)) return null;
  // if it already has a scheme
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(q)) return q;
  // domain-like: contains at least one dot and no spaces, no slashes or only path allowed
  // allow: example.com, mail.google.com, example.com/path
  if (/^[^\/\s]+\.[^\s\/]+(\/.*)?$/.test(q)) {
    return 'https://' + q;
  }
  return null;
}

// Escape HTML safe
function esc(s) {
  if (!s) return "";
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// Render results
function renderResults(results, q) {
  if (!results || results.length === 0) {
    resultsEl.innerHTML = `<div class="result">No results for <strong>${esc(q)}</strong>.</div>`;
    return;
  }
  const html = results.map(r => {
    const doc = docs[r.ref];
    const snippet = (doc.content || "").slice(0, 400) + ((doc.content || "").length > 400 ? "…" : "");
    const title = doc.title || doc.path || `Document ${r.ref}`;
    const link = doc.url || doc.path || "#";
    return `
      <div class="result">
        <div><a href="${esc(link)}" target="_blank" rel="noreferrer noopener">${esc(title)}</a></div>
        <div class="meta">${esc(link)}</div>
        <p>${esc(snippet)}</p>
      </div>
    `;
  }).join("");
  resultsEl.innerHTML = html;
}

// perform search with Lunr
function doSearch(q) {
  if (!idx) {
    resultsEl.innerHTML = `<div class="result">Index not loaded yet. Reload the page if this persists.</div>`;
    return;
  }
  const parsed = q.trim();
  if (!parsed) { resultsEl.innerHTML = ""; return; }

  // URL redirect behavior
  const maybeUrl = parsePotentialUrl(parsed);
  if (maybeUrl) {
    // redirect the browser
    window.location.href = maybeUrl;
    return;
  }

  // normal textual search
  try {
    const res = idx.search(parsed + '*'); // basic wildcard to broaden results
    renderResults(res, parsed);
  } catch (e) {
    // sometimes Lunr throws parse errors for special chars: fallback to basic token search
    try {
      const fallback = idx.search(parsed.replace(/[^a-zA-Z0-9\s]/g, ' '));
      renderResults(fallback, parsed);
    } catch (err) {
      resultsEl.innerHTML = `<div class="result">Search error: ${esc(err.message)}</div>`;
    }
  }
}

// input handlers
let timer;
qInput.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    doSearch(qInput.value);
  }, 200);
});
searchBtn.addEventListener("click", () => doSearch(qInput.value));
clearBtn.addEventListener("click", () => { qInput.value=''; resultsEl.innerHTML=''; qInput.focus(); });

// Load the documents and build Lunr index
(async function init() {
  try {
    const r = await fetch('/docs/documents.json', { cache: 'no-store' });
    if (!r.ok) throw new Error('Failed to fetch documents.json');
    docs = await r.json();
    // build lunr index
    idx = lunr(function () {
      this.ref('id');
      this.field('title', { boost: 10 });
      this.field('content');
      // add docs
      for (let i = 0; i < docs.length; i++) {
        // ensure each doc has an id that matches position for rendering convenience
        docs[i].id = i.toString();
        this.add({
          id: i.toString(),
          title: docs[i].title || '',
          content: docs[i].content || ''
        });
      }
    });
    resultsEl.innerHTML = `<div class="result">Index loaded — ${docs.length} documents ready.</div>`;
  } catch (err) {
    resultsEl.innerHTML = `<div class="result">Error loading index: ${esc(err.message)}</div>`;
    console.error('Wolf Search init error', err);
  }
})();

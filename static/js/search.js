// static/js/search.js
const qInput = document.getElementById("q");
const resultsDiv = document.getElementById("results");

let timer;
qInput.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    doSearch(qInput.value.trim());
  }, 250);
});

async function doSearch(query) {
  if (!query) { resultsDiv.innerHTML = ""; return; }
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
      method: "GET",
      credentials: "omit", // no cookies
      headers: { "Accept": "application/json" }
    });
    const json = await res.json();
    renderResults(json.results, json.query);
  } catch (err) {
    resultsDiv.innerHTML = `<div class="result">Error: ${err.message}</div>`;
  }
}

function renderResults(results, q) {
  if (!results || results.length === 0) {
    resultsDiv.innerHTML = `<div class="result">No results for <strong>${escapeHtml(q)}</strong>.</div>`;
    return;
  }
  resultsDiv.innerHTML = results.map(r => `
    <div class="result">
      <div><a href="file://${r.path}" target="_blank" rel="noreferrer">${escapeHtml(r.title)}</a></div>
      <div class="meta">${escapeHtml(r.path)} — score: ${Number(r.score).toFixed(2)}</div>
      <p>${escapeHtml(r.snippet)}</p>
    </div>
  `).join("");
}

function escapeHtml(s){ return (s||"").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

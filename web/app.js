const form = document.querySelector('#analysis-form');
const result = document.querySelector('#result');
const status = document.querySelector('#status');
let latestAnalysis = null;

function columnsFromInput(value) {
  return value.split(/[\n,]/).map(item => item.trim()).filter(Boolean);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

function renderAnalysis(analysis) {
  const sections = Object.entries(analysis.questions).map(([category, questions]) => `
    <section class="section"><h3>${escapeHtml(category)}</h3>${questions.map((item, index) => `
      <article class="question"><h4>${index + 1}. ${escapeHtml(item.question)}</h4><p><strong>Why it matters</strong><br>${escapeHtml(item.why)}</p><p><strong>How to compute</strong><br>${escapeHtml(item.how)}</p><p><strong>What to visualize</strong><br>${escapeHtml(item.what)}</p></article>`).join('')}</section>`).join('');
  result.className = 'panel result-panel';
  result.innerHTML = `<div class="result-header"><span class="badge">ANALYSIS READY</span><h2>${escapeHtml(analysis.domain)}</h2><p class="meta"><strong>Entities:</strong> ${analysis.entities.map(escapeHtml).join(', ')}</p><p class="meta"><strong>Relationships:</strong> ${analysis.relationships.map(escapeHtml).join(' · ')}</p></div>${sections}<button class="publish" id="publish-button">Publish this case to GitHub <span>→</span></button>`;
  document.querySelector('#publish-button').addEventListener('click', publishCase);
}

async function analyzeCase(event) {
  event.preventDefault();
  const button = document.querySelector('#analyze-button');
  const request = {case_title: document.querySelector('#case-title').value, columns: columnsFromInput(document.querySelector('#columns').value), sample_data: document.querySelector('#sample-data').value};
  button.disabled = true; status.textContent = 'Mapping the data...';
  try { const response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(request)}); const payload = await response.json(); if (!response.ok) throw new Error(payload.error); latestAnalysis = payload; renderAnalysis(payload); status.textContent = 'Review the analysis, then publish the case.'; } catch (error) { status.textContent = error.message; } finally { button.disabled = false; }
}

async function publishCase() {
  const button = document.querySelector('#publish-button');
  const request = {case_title: document.querySelector('#case-title').value, columns: columnsFromInput(document.querySelector('#columns').value), sample_data: document.querySelector('#sample-data').value, analysis: latestAnalysis};
  button.disabled = true; status.textContent = 'Writing and pushing the case...';
  try { const response = await fetch('/api/publish', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(request)}); const payload = await response.json(); if (!response.ok) throw new Error(payload.error); status.textContent = `Case ${payload.action}: ${payload.path}`; } catch (error) { status.textContent = error.message; button.disabled = false; }
}

form.addEventListener('submit', analyzeCase);

const form = document.querySelector('#analysis-form');
const result = document.querySelector('#result');
const status = document.querySelector('#status');
let latestAnalysis = null;
let questionHistory = [];

document.querySelector('#case-title').addEventListener('input', event => {
  document.querySelector('#case-chip').textContent = event.target.value.trim() || 'Untitled Case';
});

function parsePastedGrid(text) {
  return text.trim().split(/\r?\n/).filter(Boolean).map(row => row.split(/\t|,/).map(value => value.trim()));
}

function requestFromForm() {
  const rows = parsePastedGrid(document.querySelector('#reference-data').value);
  const columns = rows.shift() || [];
  const sampleData = rows.length
    ? [columns, ...rows].map(row => row.join('\t')).join('\n')
    : columns.join('\t');
  return {case_title: document.querySelector('#case-title').value, columns: columns.filter(Boolean), sample_data: sampleData};
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

function formatBriefing(value) {
  return escapeHtml(value).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

function renderBriefing(overview) {
  const points = overview.briefing_points || [];
  if (points.length) return `<ul class="briefing-list">${points.map(point => `<li>${formatBriefing(point.replace(/^-\s*/, ''))}</li>`).join('')}</ul>`;
  return `<p class="overview-profile">${formatBriefing(overview.profile || overview.summary || 'The dataset overview is inferred from the supplied schema.')}</p>`;
}

function renderQuestionCards(analysis) {
  return Object.entries(analysis.questions).map(([category, questions]) => `
    <section class="section"><h3>${escapeHtml(category)}</h3>${questions.map((item, index) => `
      <article class="question"><h4>${index + 1}. ${escapeHtml(item.question)}</h4><p><strong>Why it matters</strong><br>${escapeHtml(item.why)}</p><p><strong>How to compute</strong><br>${escapeHtml(item.how)}</p><p><strong>What to visualize</strong><br>${escapeHtml(item.what)}</p></article>`).join('')}</section>`).join('');
}

function renderAnalysis(analysis) {
  const overview = analysis.overview || {};
  const sections = renderQuestionCards(analysis);
  result.className = 'panel result-panel';
  result.innerHTML = `<div class="result-header"><span class="badge">ANALYSIS READY</span><h2>${escapeHtml(analysis.domain)}</h2><p class="meta"><strong>Entities:</strong> ${analysis.entities.map(escapeHtml).join(', ')}</p><p class="meta"><strong>Relationships:</strong> ${analysis.relationships.map(escapeHtml).join(' · ')}</p></div><nav class="tabs" aria-label="Analysis stages"><button type="button" class="tab active" data-tab="overview">Overview</button><button type="button" class="tab" data-tab="questions">Ask questions</button><button type="button" class="tab" data-tab="commit">Commit</button></nav><div class="tab-panel active" data-panel="overview"><section class="overview-block"><h3>Dataset briefing</h3>${renderBriefing(overview)}</section></div><div class="tab-panel" data-panel="questions"><div class="starter-questions"><h3>Starter business questions</h3>${sections}</div><div id="conversation" class="conversation"><div class="conversation-empty">Ask about a metric, segment, assumption, or next analysis step.</div></div><form id="question-form" class="question-form"><textarea id="question-input" placeholder="e.g. Which fields should I use to measure customer retention?" required></textarea><button type="submit" id="ask-button">Ask the agent <span>→</span></button></form></div><div class="tab-panel" data-panel="commit"><div class="commit-panel"><span class="badge">FINAL STEP</span><h3>Commit this case when you are satisfied</h3><p>Review the overview and ask follow-up questions first. The commit will create or update one Markdown file for this case in GitHub.</p><button class="publish" id="publish-button" type="button">Commit case to GitHub <span>→</span></button></div></div>`;
  result.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => switchTab(tab.dataset.tab)));
  result.querySelector('#question-form').addEventListener('submit', askQuestion);
  result.querySelector('#publish-button').addEventListener('click', publishCase);
}

function switchTab(name) {
  result.querySelectorAll('.tab').forEach(tab => tab.classList.toggle('active', tab.dataset.tab === name));
  result.querySelectorAll('.tab-panel').forEach(panel => panel.classList.toggle('active', panel.dataset.panel === name));
}

function appendConversation(role, text) {
  const conversation = result.querySelector('#conversation');
  const empty = conversation.querySelector('.conversation-empty');
  if (empty) empty.remove();
  const message = document.createElement('article');
  message.className = `message ${role}`;
  message.innerHTML = `<span class="message-label">${role === 'user' ? 'YOU' : 'TOWARDS INSIGHTS'}</span><p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>`;
  conversation.appendChild(message);
  conversation.scrollTop = conversation.scrollHeight;
}

async function askQuestion(event) {
  event.preventDefault();
  const input = result.querySelector('#question-input');
  const button = result.querySelector('#ask-button');
  const question = input.value.trim();
  if (!question) return;
  appendConversation('user', question);
  questionHistory.push({role: 'user', content: question});
  input.value = '';
  button.disabled = true;
  status.textContent = 'Thinking through the question...';
  try {
    const response = await fetch('/api/question', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({...requestFromForm(), analysis: latestAnalysis, question, history: questionHistory})});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error);
    appendConversation('assistant', payload.answer);
    questionHistory.push({role: 'assistant', content: payload.answer});
    status.textContent = 'Keep exploring, or move to Commit when you are satisfied.';
  } catch (error) {
    appendConversation('assistant', `I could not retrieve an answer: ${error.message}`);
    status.textContent = 'The question request failed. Check the message in the conversation and try again.';
  } finally { button.disabled = false; }
}

async function analyzeCase(event) {
  event.preventDefault();
  const button = document.querySelector('#analyze-button');
  const request = requestFromForm();
  button.disabled = true; status.textContent = 'Mapping the data...';
  try { const response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(request)}); const payload = await response.json(); if (!response.ok) throw new Error(payload.error); latestAnalysis = payload; renderAnalysis(payload); status.textContent = 'Review the analysis, then publish the case.'; } catch (error) { status.textContent = error.message; } finally { button.disabled = false; }
}

async function publishCase() {
  const button = document.querySelector('#publish-button');
  const request = {...requestFromForm(), analysis: latestAnalysis};
  button.disabled = true; status.textContent = 'Writing and pushing the case...';
  try { const response = await fetch('/api/publish', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(request)}); const payload = await response.json(); if (!response.ok) throw new Error(payload.error); status.textContent = `Case ${payload.action}: ${payload.path}`; } catch (error) { status.textContent = error.message; button.disabled = false; }
}

form.addEventListener('submit', analyzeCase);

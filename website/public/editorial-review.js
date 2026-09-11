/* Private data is fetched only after server authentication; never use localStorage for it. */
(() => {
  const $ = id => document.getElementById(id);
  const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const labels = { selected: 'Selected for analysis', rejected: 'Rejected', needs_review: 'Needs review' };
  let board, runs = [], nextOffset = 0, loading = 0, saving = false;
  const message = (text, error = false) => { $('message').textContent = text; $('message').className = error ? 'error' : 'notice'; };
  async function api(path, value) {
    const r = await fetch('/api/news/review/' + path, { method: value === undefined ? 'GET' : 'POST', credentials: 'same-origin', cache: 'no-store', headers: { 'Content-Type': 'application/json' }, body: value === undefined ? undefined : JSON.stringify(value) });
    const data = await r.json();
    if (!r.ok) { if (r.status === 401 && !$('login')) { board = null; $('shortlist').replaceChildren(); $('lower').replaceChildren(); location.replace('/editorial/review'); } throw new Error(data.error || 'Unable to load review.'); }
    return data;
  }
  function date(value) { const d = new Date(value); return Number.isNaN(d.valueOf()) ? 'Date unconfirmed' : d.toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Europe/London' }) + ' UK'; }
  function decision(item) { return board.decisions.find(d => d.item_id === item.item_id); }
  function state(item) { const d = decision(item); return d && d.version_id === item.version_id ? d.status : 'needs_review'; }
  function sourceLink(item) {
    const a = el('a', 'Read original source ↗');
    try { const u = new URL(item.canonical_url); if (!['https:', 'http:'].includes(u.protocol) || u.username || u.password) throw Error(); a.href = u.href; a.target = '_blank'; a.rel = 'noopener noreferrer'; } catch { a.removeAttribute('href'); a.textContent = 'Source link unavailable'; }
    return a;
  }
  function card(item, relation) {
    const article = el('article', undefined, 'candidate'); article.id = 'item-' + item.item_id;
    const top = el('div', undefined, 'card-top'); top.append(el('p', item.source_name + ' · ' + (item.published_at ? 'Published ' + date(item.published_at) : 'Publication date unconfirmed'), 'source'), el('span', item.score + ' / 100', 'score')); article.append(top);
    article.append(el('h3', item.title));
    if (relation) article.append(el('p', relation, 'related-note'));
    const d = decision(item), stale = d && d.version_id !== item.version_id;
    const badges = el('div', undefined, 'badges'); badges.append(el('span', item.provenance), el('span', labels[state(item)], state(item)));
    if (item.corroboration_needed) badges.append(el('span', 'Independent corroboration needed', 'caution'));
    article.append(badges);
    if (stale) article.append(el('p', 'Evidence version differs from your saved decision (' + labels[d.status] + '). Review this version before selecting it.', 'warning'));
    article.append(el('p', 'What the source says', 'small-label'), el('p', item.summary, 'excerpt'), el('p', 'Why it may matter to DAL', 'small-label'), el('p', item.relevance));
    article.append(sourceLink(item));
    const detail = el('details', undefined, 'factors'); detail.append(el('summary', 'Explain score · ' + item.ranking_version));
    const table = el('table'), caption = el('caption', 'Reading-priority factors, based only on the collected title and excerpt'); table.append(caption);
    const head = el('thead'), row = el('tr'); for (const label of ['Factor', 'Points', 'Reason']) { const th = el('th', label); th.scope = 'col'; row.append(th); } head.append(row); table.append(head);
    const body = el('tbody'); for (const f of item.factors) { const tr = el('tr'); tr.append(el('td', f.label), el('td', String(f.points) + (f.max ? ' / ' + f.max : '')), el('td', f.reason)); body.append(tr); } table.append(body); detail.append(table); article.append(detail);
    const noteLabel = el('label', 'Review note (optional)'); noteLabel.htmlFor = 'note-' + item.item_id;
    const note = el('textarea'); note.id = noteLabel.htmlFor; note.maxLength = 1500; note.rows = 2; note.value = d?.note || ''; note.placeholder = 'What needs checking? Saved when you choose a decision.'; article.append(noteLabel, note);
    const actions = el('div', undefined, 'decisions');
    for (const [status, label] of Object.entries(labels)) {
      const button = el('button', label, status === 'selected' ? 'select' : 'quiet'); button.type = 'button'; button.dataset.status = status; button.setAttribute('aria-pressed', String(!!d && !stale && d.status === status));
      button.addEventListener('click', async () => {
        if (saving) return; saving = true; lock(true); message('Saving decision…');
        try {
          const saved = await api('decision', { run_id: board.summary.run_id, item_id: item.item_id, version_id: item.version_id, expected_revision: d?.revision || 0, status, note: note.value });
          board.decisions = [...board.decisions.filter(v => v.item_id !== item.item_id), saved];
          renderCandidates(); message(label + ' — saved. No analysis or publication was triggered.');
          document.querySelector('#item-' + CSS.escape(item.item_id) + ' [data-status="' + status + '"]')?.focus();
        } catch (error) { message(error.message + ' Your note is still on this card. Copy it before refreshing.', true); }
        finally { saving = false; lock(false); }
      }); actions.append(button);
    }
    article.append(actions, el('p', d ? 'Saved ' + date(d.updated_at) + ' · revision ' + d.revision : 'No decision saved yet.', 'saved'));
    const history = el('details', undefined, 'history'); history.append(el('summary', 'Decision history')); const entries = el('div'); history.append(entries);
    history.addEventListener('toggle', async () => { if (!history.open || entries.childNodes.length) return; try { const data = await api('history?item=' + encodeURIComponent(item.item_id)); entries.append(el('p', 'Most recent 20 changes.')); for (const h of data.events) entries.append(el('p', date(h.updated_at) + ' · ' + labels[h.status] + ' · revision ' + h.revision + (h.note ? ' — ' + h.note : ''))); if (!data.events.length) entries.append(el('p', 'No saved decisions.')); } catch (error) { entries.append(el('p', error.message)); } }); article.append(history);
    return article;
  }
  function lock(value) { for (const input of document.querySelectorAll('button,select,textarea,input')) input.disabled = value; }
  function renderCandidates() {
    const query = $('search').value.trim().toLowerCase(), filter = $('filter').value;
    const matches = c => (filter === 'all' || state(c) === filter) && (!query || (c.title + ' ' + c.source_name + ' ' + c.summary).toLowerCase().includes(query));
    const top = $('shortlist'), low = $('lower'); top.replaceChildren(el('h2', 'Priority shortlist')); low.replaceChildren(); let topCount = 0, lowCount = 0;
    for (const g of board.groups) {
      if (![g.lead, ...g.related.map(r => r.candidate)].some(matches)) continue;
      const group = el('section', undefined, 'story-group'); group.append(card(g.lead));
      if (g.related.length) { const related = el('details', undefined, 'related'); related.append(el('summary', g.related.length + ' related candidate(s) · decisions stay separate')); for (const r of g.related) related.append(card(r.candidate, r.reason)); group.append(related); }
      if (g.shortlisted) { top.append(group); topCount++; } else { low.append(group); lowCount++; }
    }
    if (!topCount) top.append(el('p', 'No shortlist candidates match this view. Check the remaining candidates or change the filter.', 'empty'));
    $('remaining-label').textContent = 'Remaining candidates · ' + lowCount + ' story groups';
    $('remaining').open = !!query || filter !== 'all';
    const selected = board.candidates.filter(c => state(c) === 'selected').length, rejected = board.candidates.filter(c => state(c) === 'rejected').length;
    $('counts').textContent = selected + ' selected · ' + rejected + ' rejected · ' + (board.candidates.length - selected - rejected) + ' need review';
  }
  async function loadBoard() {
    const sequence = ++loading; board = null; $('shortlist').replaceChildren(); $('lower').replaceChildren(); $('collection').replaceChildren(); message('Loading collection…');
    if (!$('runs').value) { message('No collections stored yet. Run the source collector first.'); return; }
    try {
      const data = await api('board?run=' + encodeURIComponent($('runs').value)); if (sequence !== loading) return; board = data;
      const s = data.summary, area = $('collection'); const stats = el('div', undefined, 'stats');
      for (const [label, value] of [['Collected', date(s.started_at)], ['Sources', s.source_total + ' · ' + s.source_ok + ' without warnings'], ['Candidates', s.item_total], ['Status', s.status]]) { const box = el('div'); box.append(el('span', label), el('strong', String(value))); stats.append(box); } area.append(stats);
      if (Date.now() - Date.parse(s.started_at) > 48 * 3600000) area.append(el('p', 'This collection is more than 48 hours old. Check for newer evidence before planning an edition.', 'warning'));
      const warnings = data.coverage.sources.filter(x => x.status !== 'ok');
      for (const w of warnings) area.append(el('p', w.name + ' — ' + w.issues.join('; ') + (w.latest_source_item_at ? '. Latest dated item: ' + date(w.latest_source_item_at) : ''), 'warning'));
      for (const w of data.coverage.warnings || []) area.append(el('p', w, 'warning'));
      const health = el('details', undefined, 'method'); health.append(el('summary', 'All source health and coverage gaps'));
      for (const source of data.coverage.sources) health.append(el('p', source.name + ': ' + source.status + (source.issues.length ? ' — ' + source.issues.join('; ') : '')));
      health.append(el('h3', 'Research still needed')); const gaps = el('ul'); for (const gap of data.coverage.search_only || []) gaps.append(el('li', gap)); health.append(gaps); area.append(health);
      renderCandidates(); message('Collection loaded. Source descriptions and scores are unverified reading aids.');
    } catch (error) { if (sequence === loading) message(error.message, true); }
  }
  async function loadRuns(older = false) {
    try { const data = await api('runs?offset=' + (older ? nextOffset : 0)); const previous = $('runs').value; runs = older ? [...runs, ...data.runs] : data.runs; nextOffset = data.next_offset; $('runs').replaceChildren(); for (const r of runs) { const o = el('option', date(r.started_at) + ' · ' + r.status); o.value = r.run_id; $('runs').append(o); } if (runs.some(r => r.run_id === previous)) $('runs').value = previous; $('older').hidden = nextOffset === null; if (!older) await loadBoard(); } catch (error) { message(error.message, true); }
  }
  $('login')?.addEventListener('submit', async event => { event.preventDefault(); const button = event.target.querySelector('button'); button.disabled = true; try { await api('login', { key: $('access-key').value }); $('access-key').value = ''; location.replace('/editorial/review'); } catch (error) { message(error.message, true); button.disabled = false; } });
  $('logout')?.addEventListener('click', async () => { try { await api('logout', {}); location.replace('/editorial/review'); } catch (error) { message(error.message, true); } });
  if ($('runs')) { $('runs').addEventListener('change', loadBoard); $('refresh').addEventListener('click', () => loadRuns()); $('older').addEventListener('click', () => loadRuns(true)); $('search').addEventListener('input', () => board && renderCandidates()); $('filter').addEventListener('change', () => board && renderCandidates()); loadRuns(); }
  window.addEventListener('pageshow', event => { if (event.persisted) location.reload(); });
})();

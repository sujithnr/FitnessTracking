'use strict';
let dataset;
let filter = 'all';
const number = value => new Intl.NumberFormat('en-US', {maximumFractionDigits: 1, minimumFractionDigits: 1}).format(value);
const dateLabel = value => new Date(value + 'T12:00:00').toLocaleDateString('en-US', {month:'short',day:'numeric',year:'numeric'});
const put = (id, text) => { document.getElementById(id).textContent = text; };
function renderShoes() {
  const target = document.getElementById('shoes');
  target.replaceChildren();
  const cycles = dataset.cycles.filter(shoe => filter === 'all' || shoe.retired === (filter === 'retired'));
  for (const shoe of cycles) {
    const card = document.getElementById('shoe-template').content.cloneNode(true);
    const status = card.querySelector('.status');
    status.textContent = shoe.retired ? '↗ RETIRED' : '● IN ROTATION';
    status.classList.toggle('retired', shoe.retired);
    card.querySelector('.shoe-number').textContent = String(dataset.cycles.indexOf(shoe) + 1).padStart(2, '0');
    card.querySelector('h3').textContent = shoe.name;
    card.querySelector('.pair-label').textContent = shoe.label;
    card.querySelector('.mileage strong').textContent = number(shoe.miles);
    card.querySelector('.shoe-date').textContent = shoe.retired_date ? 'Retired ' + dateLabel(shoe.retired_date) : shoe.started ? 'In rotation since ' + dateLabel(shoe.started) : 'Start date not recorded';
    target.append(card);
  }
  if (!cycles.length) target.textContent = 'No shoes in this group yet.';
}
function render() {
  put('total', number(dataset.total_miles)); put('week', number(dataset.week_miles)); put('runs', dataset.run_count.toLocaleString());
  put('since', dataset.since ? 'Recorded since ' + dateLabel(dataset.since) : 'No runs synced yet');
  put('sync', dataset.last_synced ? 'Last Strava sync · ' + new Date(dataset.last_synced).toLocaleString('en-US', {month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZone:dataset.timezone,timeZoneName:'short'}) : 'No Strava sync recorded');
  put('built', 'Dashboard built ' + new Date(dataset.generated_at).toLocaleDateString('en-US') + '.');
  renderShoes();
  const chart = document.getElementById('chart'); chart.replaceChildren();
  const max = Math.max(1, ...dataset.days.map(day => day.miles));
  for (const day of dataset.days) {
    const bar = document.createElement('div'); bar.className = 'bar'; bar.style.height = Math.max(2, day.miles / max * 100) + '%';
    bar.title = dateLabel(day.date) + ': ' + number(day.miles) + ' miles'; bar.setAttribute('aria-label', bar.title); bar.tabIndex = 0; chart.append(bar);
  }
  const labels = document.getElementById('chart-labels'); labels.replaceChildren();
  if (dataset.days.length) for (const day of [dataset.days[0], dataset.days[dataset.days.length - 1]]) { const label = document.createElement('span'); label.textContent = dateLabel(day.date); labels.append(label); }
  const unassigned = document.getElementById('unassigned'); unassigned.replaceChildren();
  for (const item of dataset.unassigned) { const row = document.createElement('div'); row.className = 'unassigned-row'; const name = document.createElement('span'); name.textContent = item.name; const miles = document.createElement('span'); miles.textContent = number(item.miles) + ' mi'; row.append(name, miles); unassigned.append(row); }
  if (!dataset.unassigned.length) unassigned.textContent = 'All miles are assigned to a pair.';
  const recent = document.getElementById('recent'); recent.replaceChildren();
  for (const run of dataset.recent) { const row = document.createElement('tr'); for (const [index, text] of [dateLabel(run.date), run.shoe, run.assigned ? 'Assigned' : 'Needs review', number(run.miles)].entries()) { const cell = document.createElement('td'); cell.textContent = text; if (index === 2) cell.className = 'pair-tag' + (run.assigned ? '' : ' pending'); if (index === 3) cell.className = 'numeric'; row.append(cell); } recent.append(row); }
  if (!dataset.recent.length) { const row = recent.insertRow(); const cell = row.insertCell(); cell.colSpan = 4; cell.textContent = 'No runs synced yet. Your first miles will appear here.'; }
}
async function load() {
  const button = document.getElementById('refresh'); button.disabled = true;
  try { const response = await fetch('data.json', {cache:'no-store'}); if (!response.ok) throw new Error('HTTP ' + response.status); dataset = await response.json(); render(); document.getElementById('error').hidden = true; }
  catch (error) { put('error', 'Could not load the dashboard. Try refreshing in a moment.'); document.getElementById('error').hidden = false; if (!dataset) put('sync', 'Dashboard data unavailable'); }
  finally { button.disabled = false; }
}
for (const button of document.querySelectorAll('[data-filter]')) button.addEventListener('click', () => { filter = button.dataset.filter; for (const item of document.querySelectorAll('[data-filter]')) item.setAttribute('aria-pressed', String(item === button)); if (dataset) renderShoes(); });
document.getElementById('refresh').addEventListener('click', load);
document.addEventListener('visibilitychange', () => { if (!document.hidden) load(); });
setInterval(load, 15 * 60 * 1000);
load();

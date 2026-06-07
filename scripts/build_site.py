"""
build_site.py  —  reads /data JSON and writes static HTML to /docs
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

FLAG_URL = "https://flagcdn.com/20x15/{code}.png"

COUNTRY_NAMES = {
    "ARG": "Argentina", "EST": "Estonia", "USA": "United States",
    "ESP": "Spain", "FRA": "France", "GBR": "Great Britain",
    "GER": "Germany", "ITA": "Italy", "RUS": "Russia",
    "AUS": "Australia", "BRA": "Brazil", "CAN": "Canada",
    "JPN": "Japan", "CHN": "China", "CZE": "Czech Republic",
    "POL": "Poland", "ROU": "Romania", "SRB": "Serbia",
    "SVK": "Slovakia", "SUI": "Switzerland", "BEL": "Belgium",
    "NED": "Netherlands", "CRO": "Croatia", "UKR": "Ukraine",
    "LAT": "Latvia", "LTU": "Lithuania", "FIN": "Finland",
    "SWE": "Sweden", "NOR": "Norway", "DEN": "Denmark",
    "POR": "Portugal", "HUN": "Hungary", "BUL": "Bulgaria",
    "GRE": "Greece", "TUR": "Turkey", "KAZ": "Kazakhstan",
    "UZB": "Uzbekistan", "RSA": "South Africa", "MEX": "Mexico",
    "COL": "Colombia", "CHI": "Chile", "PER": "Peru",
    "PAR": "Paraguay", "URU": "Uruguay", "VEN": "Venezuela",
    "ECU": "Ecuador", "BOL": "Bolivia", "IND": "India",
    "TPE": "Chinese Taipei", "KOR": "South Korea", "THA": "Thailand",
    "MAS": "Malaysia", "INA": "Indonesia", "PHI": "Philippines",
    "NZL": "New Zealand", "ISR": "Israel", "EGY": "Egypt",
    "MAR": "Morocco", "TUN": "Tunisia", "NIG": "Nigeria",
    "KEN": "Kenya", "ZIM": "Zimbabwe",
}

ISO2 = {
    "ARG": "ar", "EST": "ee", "USA": "us", "ESP": "es", "FRA": "fr",
    "GBR": "gb", "GER": "de", "ITA": "it", "RUS": "ru", "AUS": "au",
    "BRA": "br", "CAN": "ca", "JPN": "jp", "CHN": "cn", "CZE": "cz",
    "POL": "pl", "ROU": "ro", "SRB": "rs", "SVK": "sk", "SUI": "ch",
    "BEL": "be", "NED": "nl", "CRO": "hr", "UKR": "ua", "LAT": "lv",
    "LTU": "lt", "FIN": "fi", "SWE": "se", "NOR": "no", "DEN": "dk",
    "POR": "pt", "HUN": "hu", "BUL": "bg", "GRE": "gr", "TUR": "tr",
    "KAZ": "kz", "UZB": "uz", "RSA": "za", "MEX": "mx", "COL": "co",
    "CHI": "cl", "PER": "pe", "PAR": "py", "URU": "uy", "VEN": "ve",
    "ECU": "ec", "BOL": "bo", "IND": "in", "TPE": "tw", "KOR": "kr",
    "THA": "th", "MAS": "my", "INA": "id", "PHI": "ph", "NZL": "nz",
    "ISR": "il", "EGY": "eg", "MAR": "ma", "TUN": "tn", "NIG": "ng",
    "KEN": "ke", "ZIM": "zw",
}

def flag(code):
    iso = ISO2.get((code or "").upper(), "")
    if not iso:
        return f'<span class="no-flag">{code or "—"}</span>'
    return f'<img src="{FLAG_URL.format(code=iso)}" alt="{code}" title="{COUNTRY_NAMES.get(code.upper(), code)}" class="flag"> {code}'

def load(name):
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def country_options(players, selected=""):
    countries = sorted(set(p.get("country","") for p in players if p.get("country")))
    opts = '<option value="">All countries</option>'
    for c in countries:
        name = COUNTRY_NAMES.get(c, c)
        sel = 'selected' if c == selected else ''
        opts += f'<option value="{c}" {sel}>{name} ({c})</option>'
    return opts

def birth_year_options(players):
    years = sorted(set(p.get("birth_year") for p in players if p.get("birth_year")), reverse=True)
    opts = '<option value="">All years</option>'
    for y in years:
        opts += f'<option value="{y}">{y}</option>'
    return opts

CSS = """
:root {
    --bg: #0f0f13;
    --surface: #1a1a24;
    --surface2: #22222f;
    --accent: #7c6af7;
    --accent2: #a78bfa;
    --text: #e8e8f0;
    --muted: #888899;
    --border: #2e2e42;
    --green: #34d399;
    --yellow: #fbbf24;
    --red: #f87171;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 14px; }
a { color: var(--accent2); text-decoration: none; }
a:hover { text-decoration: underline; }

/* NAV */
nav { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0 16px; display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
nav a { display: inline-block; padding: 14px 12px; color: var(--muted); font-size: 13px; font-weight: 500; transition: color .2s; }
nav a:hover, nav a.active { color: var(--accent2); text-decoration: none; border-bottom: 2px solid var(--accent); }
.nav-brand { font-weight: 700; color: var(--text) !important; font-size: 15px; margin-right: 8px; border-bottom: none !important; }

/* LAYOUT */
.container { max-width: 1100px; margin: 0 auto; padding: 24px 16px; }
h1 { font-size: 20px; margin-bottom: 4px; }
h2 { font-size: 16px; color: var(--muted); font-weight: 400; margin-bottom: 20px; }
.updated { font-size: 12px; color: var(--muted); margin-bottom: 20px; }

/* FILTERS */
.filters { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; align-items: center; }
.filters select, .filters input { background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 7px 10px; border-radius: 6px; font-size: 13px; outline: none; }
.filters select:focus, .filters input:focus { border-color: var(--accent); }
.filters label { font-size: 12px; color: var(--muted); }
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.badge-main { background: #1e3a5f; color: #60b4ff; }
.badge-qual { background: #2d3b1e; color: #86efac; }
.badge-alt { background: #3b2d1e; color: #fbbf24; }
.count-badge { background: var(--surface2); border: 1px solid var(--border); color: var(--muted); padding: 2px 8px; border-radius: 12px; font-size: 11px; }

/* TABLE */
.table-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; }
thead th { background: var(--surface2); padding: 10px 12px; text-align: left; font-size: 12px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid var(--border); white-space: nowrap; }
tbody tr { border-bottom: 1px solid var(--border); transition: background .15s; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: var(--surface2); }
tbody td { padding: 9px 12px; }
.rank-num { color: var(--accent2); font-weight: 600; font-variant-numeric: tabular-nums; }
.flag { vertical-align: middle; border-radius: 2px; }
.no-flag { font-size: 11px; color: var(--muted); }
.hidden { display: none !important; }

/* TOURNAMENT CARDS */
.t-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-top: 8px; }
.t-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
.t-card h3 { font-size: 15px; margin-bottom: 6px; }
.t-card .meta { font-size: 12px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.t-card .meta span { display: flex; align-items: center; gap: 4px; }
.btn { display: inline-block; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover { background: var(--accent2); }

/* WEEK TABS */
.week-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.week-tab { padding: 7px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--muted); font-size: 13px; cursor: pointer; transition: all .2s; }
.week-tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }

/* ENTRY MODAL */
.modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.7); z-index: 100; justify-content: center; align-items: flex-start; padding-top: 40px; }
.modal-overlay.open { display: flex; }
.modal { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; width: 95%; max-width: 700px; max-height: 80vh; display: flex; flex-direction: column; }
.modal-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.modal-body { overflow-y: auto; padding: 16px 20px; flex: 1; }
.modal-close { background: none; border: none; color: var(--muted); font-size: 20px; cursor: pointer; line-height: 1; }

/* SECTION TABS */
.section-tabs { display: flex; gap: 4px; margin-bottom: 14px; }
.section-tab { padding: 5px 12px; border-radius: 5px; font-size: 12px; cursor: pointer; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); }
.section-tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }

@media (max-width: 600px) {
    nav { gap: 0; }
    nav a { padding: 12px 8px; font-size: 12px; }
    .t-grid { grid-template-columns: 1fr; }
}
"""

JS_RANKING = """
function applyFilters(tableId, countrySelId, yearSelId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const country = document.getElementById(countrySelId)?.value || '';
    const year = document.getElementById(yearSelId)?.value || '';
    let vis = 0;
    table.querySelectorAll('tbody tr').forEach(tr => {
        const c = tr.dataset.country || '';
        const y = tr.dataset.year || '';
        const show = (!country || c === country) && (!year || y === year);
        tr.classList.toggle('hidden', !show);
        if (show) vis++;
    });
    const cnt = document.getElementById(tableId + '_count');
    if (cnt) cnt.textContent = vis + ' players';
}
"""

JS_ENTRY = """
let _allEntries = {};

function openEntry(key) {
    const modal = document.getElementById('entry-modal');
    const title = document.getElementById('entry-title');
    const body = document.getElementById('entry-body');
    const data = _allEntries[key];
    if (!data) return;
    title.textContent = data.name;
    renderSection('MAIN', data, body);
    modal.classList.add('open');
}

function closeEntry() {
    document.getElementById('entry-modal').classList.remove('open');
}

function renderSection(section, data, body) {
    const players = data.entries.filter(p => p.section === section);
    const fCountry = document.getElementById('ef-country')?.value || '';
    const fYear = document.getElementById('ef-year')?.value || '';

    let countries = [...new Set(data.entries.map(p=>p.country).filter(Boolean))].sort();
    let years = [...new Set(data.entries.map(p=>p.birth_year).filter(Boolean))].sort((a,b)=>b-a);

    let html = `<div class="section-tabs">
        <button class="section-tab ${section==='MAIN'?'active':''}" onclick="renderSection('MAIN',_allEntries[currentKey],document.getElementById('entry-body'))">Main Draw</button>
        <button class="section-tab ${section==='QUAL'?'active':''}" onclick="renderSection('QUAL',_allEntries[currentKey],document.getElementById('entry-body'))">Qualifying</button>
        <button class="section-tab ${section==='ALT'?'active':''}" onclick="renderSection('ALT',_allEntries[currentKey],document.getElementById('entry-body'))">Alternates</button>
    </div>
    <div class="filters" style="margin-bottom:12px;">
        <div class="filter-group"><label>Country</label>
        <select id="ef-country" onchange="renderSection('${section}',_allEntries[currentKey],document.getElementById('entry-body'))">
            <option value="">All</option>
            ${countries.map(c=>`<option value="${c}" ${c===fCountry?'selected':''}>${c}</option>`).join('')}
        </select></div>
        <div class="filter-group"><label>Birth year</label>
        <select id="ef-year" onchange="renderSection('${section}',_allEntries[currentKey],document.getElementById('entry-body'))">
            <option value="">All</option>
            ${years.map(y=>`<option value="${y}" ${String(y)===String(fYear)?'selected':''}>${y}</option>`).join('')}
        </select></div>
    </div>`;

    let filtered = players.filter(p => {
        return (!fCountry || p.country === fCountry) && (!fYear || String(p.birth_year) === String(fYear));
    });

    html += `<div class="table-wrap"><table>
        <thead><tr><th>#</th><th>Player</th><th>Country</th><th>Rank</th><th>Born</th></tr></thead>
        <tbody>`;
    filtered.forEach(p => {
        const rank = p.wta_rank || p.itf_rank || '—';
        html += `<tr><td class="rank-num">${p.pos}</td><td>${p.name}</td>
            <td>${p.country||'—'}</td>
            <td>${rank}</td>
            <td>${p.birth_year||'—'}</td></tr>`;
    });
    html += `</tbody></table></div>`;
    body.innerHTML = html;
}

let currentKey = '';
function openEntryKey(key) {
    currentKey = key;
    openEntry(key);
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeEntry(); });
"""

def nav(active=""):
    pages = [
        ("index.html", "🏠 Home"),
        ("wta_rankings.html", "WTA Rankings"),
        ("junior_rankings.html", "Junior Rankings"),
        ("wta_entries.html", "WTA Entries"),
        ("itf_entries.html", "ITF Entries"),
        ("jr_entries.html", "Junior Entries"),
    ]
    links = '<a href="index.html" class="nav-brand">🎾 Circuit Hub</a>'
    for href, label in pages[1:]:
        cls = ' class="active"' if href == active else ''
        links += f'<a href="{href}"{cls}>{label}</a>'
    return f'<nav>{links}</nav>'

def base_html(title, active, body, extra_js=""):
    meta = load("meta") or {}
    updated = meta.get("updated_at", "—")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Circuit Hub</title>
<style>{CSS}</style>
</head>
<body>
{nav(active)}
<div class="container">
<p class="updated">Last updated: {updated}</p>
{body}
</div>
<script>{JS_RANKING}{extra_js}</script>
</body>
</html>"""

# ─────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────

def build_index():
    meta = load("meta") or {}
    wta = load("wta_rankings") or []
    jr = load("junior_rankings") or []
    wta_cal = load("wta_calendar") or []
    jr_cal = load("itf_jr_calendar") or []
    body = f"""
<h1>Circuit Hub</h1>
<h2>Women's tennis data — rankings, entries & draws</h2>
<div class="t-grid">
  <div class="t-card">
    <h3>WTA Rankings</h3>
    <div class="meta"><span>{len(wta)} players</span></div>
    <a href="wta_rankings.html" class="btn btn-primary">View →</a>
  </div>
  <div class="t-card">
    <h3>Junior Rankings</h3>
    <div class="meta"><span>{len(jr)} players · Filter by country & year</span></div>
    <a href="junior_rankings.html" class="btn btn-primary">View →</a>
  </div>
  <div class="t-card">
    <h3>WTA Entry Lists</h3>
    <div class="meta"><span>{len(wta_cal)} tournaments</span></div>
    <a href="wta_entries.html" class="btn btn-primary">View →</a>
  </div>
  <div class="t-card">
    <h3>Junior Entry Lists</h3>
    <div class="meta"><span>{len(jr_cal)} tournaments</span></div>
    <a href="jr_entries.html" class="btn btn-primary">View →</a>
  </div>
</div>"""
    html = base_html("Home", "index.html", body)
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("  built index.html")

def build_ranking_page(data_key, title, filename, circuit_label=""):
    players = load(data_key) or []
    country_opts = country_options(players)
    year_opts = birth_year_options(players)

    rows = ""
    for p in players:
        c = p.get("country","")
        y = p.get("birth_year","")
        rows += f"""<tr data-country="{c}" data-year="{y or ''}">
            <td class="rank-num">{p.get('rank','—')}</td>
            <td>{p.get('name','')}</td>
            <td>{flag(c)}</td>
            <td>{p.get('points',0)}</td>
            <td>{y or '—'}</td>
        </tr>"""

    tid = filename.replace(".html","")
    body = f"""
<h1>{title}</h1>
<div class="filters">
  <div class="filter-group">
    <label>Country</label>
    <select id="{tid}_country" onchange="applyFilters('{tid}','{tid}_country','{tid}_year')">
      {country_opts}
    </select>
  </div>
  <div class="filter-group">
    <label>Birth year</label>
    <select id="{tid}_year" onchange="applyFilters('{tid}','{tid}_country','{tid}_year')">
      {year_opts}
    </select>
  </div>
  <span class="count-badge" id="{tid}_count">{len(players)} players</span>
</div>
<div class="table-wrap">
<table id="{tid}">
  <thead><tr><th>Rank</th><th>Player</th><th>Country</th><th>Points</th><th>Born</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>"""
    html = base_html(title, filename, body)
    with open(os.path.join(DOCS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  built {filename}")

def build_entry_page(data_key, title, filename, circuit="wt"):
    entries_data = load(data_key) or {}

    cards = ""
    all_entries_js = {}
    for key, t in entries_data.items():
        safe_key = key.replace("-","_").replace(".","_")
        all_entries_js[safe_key] = t
        entries = t.get("entries", [])
        main_count = sum(1 for p in entries if p.get("section")=="MAIN")
        qual_count = sum(1 for p in entries if p.get("section")=="QUAL")
        cards += f"""<div class="t-card">
            <h3>{t.get('name', key)}</h3>
            <div class="meta">
                <span>{flag(t.get('country',''))} {t.get('country','')}</span>
                <span>📅 {t.get('start_date','')}</span>
                <span>🎾 {t.get('surface','')}</span>
            </div>
            <div style="display:flex;gap:8px;margin-bottom:12px;">
                <span class="badge badge-main">MD {main_count}</span>
                <span class="badge badge-qual">Q {qual_count}</span>
            </div>
            <button class="btn btn-primary" onclick="openEntryKey('{safe_key}')">Entry List →</button>
        </div>"""

    if not cards:
        cards = '<p style="color:var(--muted)">No upcoming tournaments with entry lists available yet.</p>'

    entries_json = json.dumps(all_entries_js, ensure_ascii=False)
    extra_js = f"_allEntries = {entries_json};\n{JS_ENTRY}"

    body = f"""
<h1>{title}</h1>
<div class="t-grid">{cards}</div>
<div class="modal-overlay" id="entry-modal" onclick="if(event.target===this)closeEntry()">
  <div class="modal">
    <div class="modal-header">
      <strong id="entry-title"></strong>
      <button class="modal-close" onclick="closeEntry()">✕</button>
    </div>
    <div class="modal-body" id="entry-body"></div>
  </div>
</div>"""

    html = base_html(title, filename, body, extra_js=extra_js)
    with open(os.path.join(DOCS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  built {filename}")

def build_wta_entries():
    """WTA entry lists from WTA calendar (upcoming tournaments)."""
    wta_cal = load("wta_calendar") or []
    from datetime import timedelta
    today = datetime.now().strftime("%Y-%m-%d")
    cutoff = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")

    cards = ""
    for t in wta_cal:
        start = t.get("start_date","")
        if start < today or start > cutoff:
            continue
        tid = t.get("id","")
        name_slug = t.get("name","").lower().replace(" ","-").replace("'","-")
        year = t.get("year", datetime.now().year)
        url = f"https://www.wtatennis.com/tournaments/{tid}/{name_slug}/{year}/player-list"
        level = t.get("level","")
        city = t.get("city","")
        country = t.get("country","")
        surface = t.get("surface","")
        display = f"{level} {city}".strip() if level else t.get("name", city)
        cards += f"""<div class="t-card">
            <h3>{display}</h3>
            <div class="meta">
                <span>{flag(country)} {country}</span>
                <span>📅 {start}</span>
                <span>🎾 {surface}</span>
                <span class="badge badge-main">{level}</span>
            </div>
            <a href="{url}" target="_blank" class="btn btn-primary">WTA Player List ↗</a>
        </div>"""

    if not cards:
        cards = '<p style="color:var(--muted)">No upcoming WTA tournaments in the next 3 weeks.</p>'

    body = f'<h1>WTA Entry Lists</h1><div class="t-grid">{cards}</div>'
    html = base_html("WTA Entry Lists", "wta_entries.html", body)
    with open(os.path.join(DOCS_DIR, "wta_entries.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("  built wta_entries.html")

def main():
    print("Building site...")
    build_index()
    build_ranking_page("wta_rankings", "WTA Rankings", "wta_rankings.html")
    build_ranking_page("junior_rankings", "Junior Rankings (Girls)", "junior_rankings.html", circuit_label="JG")
    build_wta_entries()
    build_entry_page("wt_entry_lists", "ITF Women's Tour — Entry Lists", "itf_entries.html", circuit="wt")
    build_entry_page("jr_entry_lists", "Junior Girls — Entry Lists", "jr_entries.html", circuit="jg")
    print("Site built.")

if __name__ == "__main__":
    main()

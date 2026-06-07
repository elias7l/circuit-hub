"""
fetch_data.py  —  pulls circuit data and writes JSON to /data
"""

import json
import time
import os
import requests
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS_WTA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "referer": "https://www.wtatennis.com/",
    "account": "wta",
}

HEADERS_ITF = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.itftennis.com/en/rankings/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
}

def save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  saved {name}.json  ({len(data) if isinstance(data, list) else '...'} items)")

# ─────────────────────────────────────────────
# WTA Rankings
# ─────────────────────────────────────────────

def fetch_wta_rankings(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    url = "https://api.wtatennis.com/tennis/players/rankings"
    all_players = []
    page = 0
    while True:
        params = {
            "page": page,
            "pageSize": 500,
            "type": "rankSingles",
            "sort": "asc",
            "metric": "SINGLES",
            "at": date_str,
        }
        try:
            r = requests.get(url, headers=HEADERS_WTA, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            items = data.get("content", [])
            if not items:
                break
            for item in items:
                p = item.get("player", {})
                dob = p.get("dateOfBirth", "")
                birth_year = int(dob[:4]) if dob and len(dob) >= 4 else None
                all_players.append({
                    "rank": item.get("ranking"),
                    "name": p.get("fullName", ""),
                    "country": p.get("countryCode", ""),
                    "points": item.get("points", 0),
                    "birth_year": birth_year,
                })
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  WTA rankings page {page} error: {e}")
            break
    return all_players

# ─────────────────────────────────────────────
# ITF Rankings (WT = Women's Tour, JG = Junior Girls)
# ─────────────────────────────────────────────

def fetch_itf_rankings(circuit="JG", nationality=None):
    url = "https://www.itftennis.com/tennis/api/PlayerRankApi/GetPlayerRankings"
    all_players = []
    skip = 0
    take = 100
    while True:
        params = {
            "circuitCode": circuit,
            "matchTypeCode": "S",
            "ageCategoryCode": "",
            "take": take,
            "skip": skip,
            "isOrderAscending": "true",
        }
        if nationality:
            params["nationCode"] = nationality
        try:
            r = requests.get(url, headers=HEADERS_ITF, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            items = data.get("items", []) if isinstance(data, dict) else []
            if not items:
                break
            for p in items:
                dob = p.get("dateOfBirth", "") or ""
                birth_year = int(dob[:4]) if dob and len(dob) >= 4 else None
                all_players.append({
                    "rank": p.get("rank"),
                    "name": f"{p.get('playerGivenName','')} {p.get('playerFamilyName','')}".strip(),
                    "country": p.get("playerNationalityCode", ""),
                    "points": p.get("rankingPoints", 0),
                    "birth_year": birth_year,
                    "itf_id": p.get("playerId", ""),
                })
            total = data.get("totalItems", 0)
            skip += len(items)
            if skip >= total or not total:
                break
            time.sleep(0.3)
        except Exception as e:
            print(f"  ITF {circuit} rankings skip={skip} error: {e}")
            break
    return all_players

# ─────────────────────────────────────────────
# ITF Calendar
# ─────────────────────────────────────────────

def fetch_itf_calendar(circuit="JG"):
    year = datetime.now().year
    url = "https://www.itftennis.com/tennis/api/TournamentApi/GetCalendar"
    all_items = []
    skip = 0
    take = 250
    while True:
        params = {
            "circuitCode": circuit,
            "searchString": "",
            "skip": skip,
            "take": take,
            "dateFrom": f"{year}-01-01",
            "dateTo": f"{year}-12-31",
            "isOrderAscending": "true",
            "orderField": "startDate",
        }
        try:
            r = requests.get(url, headers=HEADERS_ITF, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            items = data.get("items", []) if isinstance(data, dict) else []
            if not items:
                break
            all_items.extend(items)
            total = data.get("totalItems", 0)
            skip += len(items)
            if skip >= total or not total:
                break
            time.sleep(0.5)
        except Exception as e:
            print(f"  ITF calendar {circuit} skip={skip} error: {e}")
            break
    return all_items

# ─────────────────────────────────────────────
# ITF Entry List
# ─────────────────────────────────────────────

def fetch_itf_entry_list(tournament_key, circuit="JG"):
    key = tournament_key.strip().lower()
    url = "https://www.itftennis.com/tennis/api/TournamentApi/GetAcceptanceList"
    params = {"tournamentKey": key, "circuitCode": circuit}
    try:
        r = requests.get(url, headers=HEADERS_ITF, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        root = []
        if isinstance(data, list) and data:
            root = data[0].get("entryClassifications", []) if isinstance(data[0], dict) else []
        elif isinstance(data, dict):
            root = data.get("entryClassifications", [])
        return parse_entry_list(root)
    except Exception as e:
        print(f"  Entry list {tournament_key} error: {e}")
        return []

def parse_entry_list(classifications):
    players = []
    for cls in classifications:
        code = cls.get("entryClassificationCode", "")
        if code in ("MDA", "JR", "JA"):
            section = "MAIN"
        elif code == "Q":
            section = "QUAL"
        elif code == "A":
            section = "ALT"
        else:
            continue
        for entry in cls.get("entries") or []:
            pos = entry.get("positionDisplay", "-")
            for p in entry.get("players") or []:
                dob = p.get("dateOfBirth", "") or ""
                birth_year = int(dob[:4]) if dob and len(dob) >= 4 else None
                players.append({
                    "pos": pos,
                    "name": f"{p.get('givenName','')} {p.get('familyName','')}".strip(),
                    "country": p.get("nationalityCode", "-"),
                    "wta_rank": p.get("atpWtaRank", ""),
                    "itf_rank": p.get("itfBTRank", ""),
                    "birth_year": birth_year,
                    "section": section,
                })
    return players

# ─────────────────────────────────────────────
# WTA Calendar
# ─────────────────────────────────────────────

def fetch_wta_calendar():
    year = datetime.now().year
    url = "https://api.wtatennis.com/tennis/tournaments/"
    params = {
        "page": 0,
        "pageSize": 200,
        "excludeLevels": "ITF",
        "from": f"{year}-01-01",
        "to": f"{year}-12-31",
    }
    try:
        r = requests.get(url, headers=HEADERS_WTA, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        items = data.get("content", [])
        result = []
        for t in items:
            result.append({
                "id": t.get("tournamentGroup", {}).get("id", ""),
                "name": t.get("tournamentGroup", {}).get("name", ""),
                "city": t.get("city", ""),
                "country": t.get("countryCode") or t.get("country") or "",
                "level": t.get("level", ""),
                "surface": t.get("surface") or t.get("surfaceType") or "",
                "start_date": t.get("startDate", ""),
                "end_date": t.get("endDate", ""),
                "year": t.get("year", year),
            })
        return result
    except Exception as e:
        print(f"  WTA calendar error: {e}")
        return []

# ─────────────────────────────────────────────
# WTA Entry List
# ─────────────────────────────────────────────

def fetch_wta_entry_list(tournament_id, name_slug, year):
    from bs4 import BeautifulSoup
    url = f"https://www.wtatennis.com/tournaments/{tournament_id}/{name_slug}/{year}/player-list"
    try:
        r = requests.get(url, headers=HEADERS_WTA, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        import re
        players = []
        current = "MAIN"
        for tag in soup.find_all(True):
            tab = tag.get("data-ui-tab", "").lower()
            if "qualifying" in tab:
                current = "QUAL"
            elif "doubles" in tab:
                current = "IGNORE"
            if current == "IGNORE":
                continue
            href = tag.get("href", "")
            m = re.match(r"/players/(\d+)/([^/]+)", href)
            if m:
                pid, slug = m.group(1), m.group(2)
                display = slug.replace("-", " ").title()
                players.append({
                    "pid": pid,
                    "name": display,
                    "section": current,
                    "country": "",
                    "rank": "",
                    "birth_year": None,
                })
        # deduplicate
        seen = set()
        deduped = []
        for p in players:
            if p["pid"] not in seen:
                seen.add(p["pid"])
                deduped.append(p)
        return deduped
    except Exception as e:
        print(f"  WTA entry list {tournament_id} error: {e}")
        return []

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print("Fetching WTA rankings...")
    wta_rankings = fetch_wta_rankings(today)
    save("wta_rankings", wta_rankings)

    print("Fetching ITF Junior Girls rankings (all countries)...")
    junior_rankings = fetch_itf_rankings(circuit="JG")
    save("junior_rankings", junior_rankings)

    print("Fetching ITF Women's Tour rankings...")
    itf_wt_rankings = fetch_itf_rankings(circuit="WT")
    save("itf_wt_rankings", itf_wt_rankings)

    print("Fetching WTA calendar...")
    wta_cal = fetch_wta_calendar()
    save("wta_calendar", wta_cal)

    print("Fetching ITF Junior Girls calendar...")
    itf_jr_cal = fetch_itf_calendar(circuit="JG")
    save("itf_jr_calendar", itf_jr_cal)

    print("Fetching ITF Women's Tour calendar...")
    itf_wt_cal = fetch_itf_calendar(circuit="WT")
    save("itf_wt_calendar", itf_wt_cal)

    # Entry lists: top upcoming tournaments (next 2 weeks)
    from datetime import timedelta
    cutoff = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    today_s = today

    print("Fetching ITF Junior entry lists...")
    jr_entries = {}
    for t in itf_jr_cal:
        start = (t.get("startDate") or "")[:10]
        if start < today_s or start > cutoff:
            continue
        key = (t.get("tournamentKey") or t.get("tournamentLink","").rstrip("/").split("/")[-1] or "").lower()
        if not key:
            continue
        status = (t.get("status") or t.get("tournamentStatus") or "").lower()
        if "cancel" in status:
            continue
        print(f"  entry list: {t.get('tournamentName',key)}")
        entries = fetch_itf_entry_list(key, circuit="JG")
        jr_entries[key] = {
            "name": t.get("tournamentName", key),
            "start_date": start,
            "country": t.get("hostNationCode") or t.get("hostNation") or "",
            "surface": t.get("surfaceDesc") or t.get("surface") or "",
            "entries": entries,
        }
        time.sleep(2)
    save("jr_entry_lists", jr_entries)

    print("Fetching ITF WT entry lists...")
    wt_entries = {}
    for t in itf_wt_cal:
        start = (t.get("startDate") or "")[:10]
        if start < today_s or start > cutoff:
            continue
        key = (t.get("tournamentKey") or t.get("tournamentLink","").rstrip("/").split("/")[-1] or "").lower()
        if not key:
            continue
        status = (t.get("status") or t.get("tournamentStatus") or "").lower()
        if "cancel" in status:
            continue
        print(f"  entry list: {t.get('tournamentName',key)}")
        entries = fetch_itf_entry_list(key, circuit="WT")
        wt_entries[key] = {
            "name": t.get("tournamentName", key),
            "start_date": start,
            "country": t.get("hostNationCode") or t.get("hostNation") or "",
            "surface": t.get("surfaceDesc") or t.get("surface") or "",
            "entries": entries,
        }
        time.sleep(2)
    save("wt_entry_lists", wt_entries)

    # Save metadata
    save("meta", {"updated_at": today, "timestamp": datetime.now().isoformat() + "Z"})
    print("Done.")

if __name__ == "__main__":
    main()

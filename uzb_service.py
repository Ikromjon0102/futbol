"""O'zbekiston Superligasi: API-Football (api-sports.io) orqali jonli natijalar.

Bepul tarif kuniga 100 ta so'rov beradi, shuning uchun so'rovlar tejaladi:
o'yin bo'lmaganda 3 soatda bir, o'yin ketayotganda 10 daqiqada bir.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

import pytz

from config import (
    API_FOOTBALL_KEY, API_FOOTBALL_UZ_LEAGUE_ID, API_FOOTBALL_UZ_SEASON,
    UZ_LIVE_INTERVAL, UZ_IDLE_INTERVAL, UZ_STATS_INTERVAL
)
from database import get_db_connection

UZB_LEAGUE_ID = 1001
API_BASE = "https://v3.football.api-sports.io"
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

LIVE_STATUSES = {"1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"}
FINISHED_STATUSES = {"FT", "AET", "PEN", "AWD", "WO"}

_state = {"next_fixtures": 0, "next_stats": 0, "blocked_until": 0, "remaining": None}


def _season():
    return API_FOOTBALL_UZ_SEASON or datetime.now(TASHKENT_TZ).year


def _next_utc_midnight():
    now = datetime.now(timezone.utc)
    return (now + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0).timestamp()


def api_get(path, **params):
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"x-apisports-key": API_FOOTBALL_KEY})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            remaining = res.headers.get("x-ratelimit-requests-remaining")
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"⚠️ API-Football so'rovi muvaffaqiyatsiz: {path} ({e})")
        return None

    if remaining is not None and remaining.isdigit():
        _state["remaining"] = int(remaining)
        if int(remaining) <= 0:
            _state["blocked_until"] = _next_utc_midnight()

    errors = data.get("errors")
    if errors:
        print(f"❌ API-Football xatosi ({path}): {errors}")
        # Quota/plan/key errors won't fix themselves within minutes.
        _state["blocked_until"] = max(_state["blocked_until"], time.time() + 3600)
        return None
    return data.get("response", [])


def _round(round_str):
    m = re.search(r"(\d+)\s*$", round_str or "")
    if m:
        return int(m.group(1)), f"{m.group(1)}-tur"
    return 0, round_str or "Tur"


def _events(raw_events, home_id):
    events = []
    for e in raw_events or []:
        etype = e.get("type")
        detail = e.get("detail") or ""
        t = e.get("time") or {}
        minute = f"{t.get('elapsed') or ''}{'+' + str(t['extra']) if t.get('extra') else ''}"
        player = (e.get("player") or {}).get("name") or ""
        side = "home" if (e.get("team") or {}).get("id") == home_id else "away"
        if etype == "Goal" and detail != "Missed Penalty":
            label = {"Own Goal": "Avtogol", "Penalty": "Penalti"}.get(detail, "Gol")
            events.append({"type": "goal", "minute": minute, "player": player, "team": side, "detail": label})
        elif etype == "Card":
            events.append({"type": "card", "minute": minute, "player": player, "team": side,
                           "card": "red" if "Red" in detail else "yellow"})
    return events


def _fixture_row(item, with_events):
    fx = item.get("fixture", {})
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    home, away = teams.get("home", {}), teams.get("away", {})
    status = fx.get("status", {})
    short = status.get("short")
    is_live = short in LIVE_STATUSES
    is_finished = short in FINISHED_STATUSES

    live_time = None
    if is_live:
        live_time = "Tanaffus" if short == "HT" else f"{status.get('elapsed') or ''}'"

    ts = fx.get("timestamp") or 0
    t_dt = datetime.fromtimestamp(ts, TASHKENT_TZ) if ts else None
    hs, as_ = goals.get("home"), goals.get("away")
    score_str = f"{hs or 0} : {as_ or 0}" if (is_live or is_finished) else None
    round_num, round_name = _round(item.get("league", {}).get("round"))
    venue = fx.get("venue") or {}

    return (
        f"apif_{fx.get('id')}", UZB_LEAGUE_ID, round_num, round_name,
        home.get("id"), home.get("name"), home.get("logo"),
        away.get("id"), away.get("name"), away.get("logo"),
        score_str, "" if hs is None else str(hs), "" if as_ is None else str(as_),
        1 if is_live else 0, 1 if is_finished else 0, live_time,
        fx.get("date"), t_dt.strftime("%d.%m.%Y") if t_dt else "", t_dt.strftime("%H:%M") if t_dt else "--:--", "",
        ts, ", ".join(x for x in (venue.get("name"), venue.get("city")) if x), fx.get("referee") or "",
        json.dumps(_events(item.get("events"), home.get("id"))) if with_events else None,
        time.time()
    )


def _save_fixtures(items, with_events):
    conn = get_db_connection()
    cursor = conn.cursor()
    for item in items:
        cursor.execute('''
            INSERT INTO matches (
                id, league_id, round_num, round_name,
                home_id, home_name, home_badge, away_id, away_name, away_badge,
                score_str, home_score, away_score, is_live, is_finished, live_time,
                utc_time, tashkent_date, tashkent_time, tashkent_display,
                tashkent_timestamp, stadium, referee, events_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                round_num = excluded.round_num, round_name = excluded.round_name,
                home_id = excluded.home_id, home_name = excluded.home_name, home_badge = excluded.home_badge,
                away_id = excluded.away_id, away_name = excluded.away_name, away_badge = excluded.away_badge,
                score_str = excluded.score_str, home_score = excluded.home_score, away_score = excluded.away_score,
                is_live = excluded.is_live, is_finished = excluded.is_finished, live_time = excluded.live_time,
                utc_time = excluded.utc_time, tashkent_date = excluded.tashkent_date,
                tashkent_time = excluded.tashkent_time, tashkent_timestamp = excluded.tashkent_timestamp,
                stadium = excluded.stadium, referee = excluded.referee,
                events_json = COALESCE(excluded.events_json, matches.events_json),
                updated_at = excluded.updated_at
        ''', _fixture_row(item, with_events))
    if items and not with_events:
        # Real season data replaces the hand-entered placeholder matches.
        cursor.execute("DELETE FROM matches WHERE league_id = ? AND id NOT LIKE 'apif_%'", (UZB_LEAGUE_ID,))
    conn.commit()
    conn.close()


def _active_fixture_ids(now):
    """Fixtures that are live or kicked off within the last 3 hours (or start in 10 minutes)."""
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT id FROM matches
        WHERE league_id = ? AND id LIKE 'apif_%'
          AND (is_live = 1 OR tashkent_timestamp BETWEEN ? AND ?)
        ORDER BY tashkent_timestamp ASC LIMIT 20
    ''', (UZB_LEAGUE_ID, now - 3 * 3600, now + 10 * 60)).fetchall()
    conn.close()
    return [r["id"].replace("apif_", "") for r in rows]


def _next_kickoff(now):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT MIN(tashkent_timestamp) AS ts FROM matches
        WHERE league_id = ? AND id LIKE 'apif_%' AND is_finished = 0 AND tashkent_timestamp > ?
    ''', (UZB_LEAGUE_ID, now)).fetchone()
    conn.close()
    return row["ts"] if row and row["ts"] else None


def sync_fixtures():
    now = time.time()
    active = _active_fixture_ids(now)
    if active:
        items = api_get("/fixtures", ids="-".join(active))
        if items is not None:
            _save_fixtures(items, with_events=True)
            print(f"🇺🇿 {len(items)} ta jonli/bugungi o'yin yangilandi")
    else:
        items = api_get("/fixtures", league=API_FOOTBALL_UZ_LEAGUE_ID, season=_season())
        if items is not None:
            _save_fixtures(items, with_events=False)
            print(f"🇺🇿 Superliga: {len(items)} ta o'yin yuklandi")

    now = time.time()
    if _active_fixture_ids(now):
        interval = UZ_LIVE_INTERVAL
    else:
        interval = UZ_IDLE_INTERVAL
        kickoff = _next_kickoff(now)
        if kickoff:
            interval = max(60, min(interval, kickoff - 5 * 60 - now))
    if _state["remaining"] is not None and _state["remaining"] < 15:
        interval = max(interval, 3600)
    _state["next_fixtures"] = now + interval


def sync_standings_and_scorers():
    season = _season()
    league = API_FOOTBALL_UZ_LEAGUE_ID
    now_ts = time.time()

    standings = api_get("/standings", league=league, season=season)
    if standings:
        table = standings[0].get("league", {}).get("standings", [[]])[0]
        conn = get_db_connection()
        conn.execute('DELETE FROM standings WHERE league_id = ?', (UZB_LEAGUE_ID,))
        for t in table:
            team = t.get("team", {})
            stats = t.get("all", {})
            g = stats.get("goals", {})
            conn.execute('''
                INSERT INTO standings (
                    league_id, team_id, rank, name, short_name,
                    played, wins, draws, losses, scores_str, goal_diff, points, badge, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                UZB_LEAGUE_ID, team.get("id"), t.get("rank"), team.get("name"), team.get("name"),
                stats.get("played", 0), stats.get("win", 0), stats.get("draw", 0), stats.get("lose", 0),
                f"{g.get('for', 0)}-{g.get('against', 0)}", t.get("goalsDiff", 0), t.get("points", 0),
                team.get("logo"), now_ts
            ))
        conn.commit()
        conn.close()

    scorers = api_get("/players/topscorers", league=league, season=season)
    assists = api_get("/players/topassists", league=league, season=season)
    if scorers is None and assists is None:
        return standings is not None

    players = {}
    for item in (scorers or []) + (assists or []):
        p = item.get("player", {})
        st = (item.get("statistics") or [{}])[0]
        team = st.get("team", {})
        players[p.get("id") or p.get("name")] = (
            UZB_LEAGUE_ID, p.get("name"), team.get("name"), team.get("logo"), p.get("photo") or "",
            (st.get("goals") or {}).get("total") or 0, (st.get("goals") or {}).get("assists") or 0,
            (st.get("games") or {}).get("appearences") or 0, (st.get("penalty") or {}).get("scored") or 0,
            now_ts
        )
    conn = get_db_connection()
    conn.execute('DELETE FROM player_stats WHERE league_id = ?', (UZB_LEAGUE_ID,))
    conn.executemany('''
        INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', list(players.values()))
    conn.commit()
    conn.close()
    print(f"🇺🇿 Superliga jadvali va {len(players)} ta futbolchi statistikasi yangilandi")
    return True


def tick():
    """Called every minute; only spends API requests when their interval has passed."""
    if not API_FOOTBALL_KEY:
        return
    now = time.time()
    if now < _state["blocked_until"]:
        return
    if now >= _state["next_fixtures"]:
        sync_fixtures()
    if now >= _state["next_stats"] and time.time() >= _state["blocked_until"]:
        ok = sync_standings_and_scorers()
        _state["next_stats"] = time.time() + (UZ_STATS_INTERVAL if ok else 1800)


if __name__ == '__main__':
    if not API_FOOTBALL_KEY:
        print("API_FOOTBALL_KEY o'rnatilmagan")
    else:
        sync_fixtures()
        sync_standings_and_scorers()

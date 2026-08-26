import sqlite3
import json
import time
import os
from datetime import datetime
import pytz

DB_PATH = os.path.join(os.path.dirname(__file__), 'futbol.db')
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    if force:
        cursor.execute('DROP TABLE IF EXISTS leagues')
        cursor.execute('DROP TABLE IF EXISTS matches')
        cursor.execute('DROP TABLE IF EXISTS standings')
        cursor.execute('DROP TABLE IF EXISTS player_stats')
        cursor.execute('DROP TABLE IF EXISTS sync_meta')

    # 1. Ligalar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            full_name TEXT,
            country TEXT,
            flag TEXT,
            icon TEXT,
            badge TEXT,
            sort_order INTEGER DEFAULT 0
        )
    ''')

    # 2. O'yinlar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id TEXT PRIMARY KEY,
            league_id INTEGER,
            round_num INTEGER,
            round_name TEXT,
            home_id INTEGER,
            home_name TEXT,
            home_badge TEXT,
            away_id INTEGER,
            away_name TEXT,
            away_badge TEXT,
            score_str TEXT,
            home_score TEXT,
            away_score TEXT,
            is_live INTEGER DEFAULT 0,
            is_finished INTEGER DEFAULT 0,
            live_time TEXT,
            utc_time TEXT,
            tashkent_date TEXT,
            tashkent_time TEXT,
            tashkent_display TEXT,
            tashkent_timestamp REAL,
            stadium TEXT,
            referee TEXT,
            events_json TEXT,
            updated_at REAL,
            FOREIGN KEY (league_id) REFERENCES leagues (id)
        )
    ''')

    # 3. Turnir jadvallari
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS standings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id INTEGER,
            team_id INTEGER,
            rank INTEGER,
            name TEXT,
            short_name TEXT,
            played INTEGER,
            wins INTEGER,
            draws INTEGER,
            losses INTEGER,
            scores_str TEXT,
            goal_diff INTEGER,
            points INTEGER,
            badge TEXT,
            updated_at REAL
        )
    ''')

    # 4. To'purarlar va assistentlar (Stats)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id INTEGER,
            player_name TEXT,
            team_name TEXT,
            team_badge TEXT,
            photo TEXT,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            matches INTEGER DEFAULT 0,
            penalties INTEGER DEFAULT 0,
            updated_at REAL
        )
    ''')

    conn.commit()
    conn.close()

def get_leagues_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leagues ORDER BY sort_order ASC')
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r["id"],
        "name": r["name"],
        "fullName": r["full_name"],
        "country": r["country"],
        "flag": r["flag"],
        "icon": r["icon"],
        "badge": r["badge"]
    } for r in rows]

def get_matches_from_db(league_id, round_num=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if round_num:
        cursor.execute('SELECT * FROM matches WHERE league_id = ? AND round_num = ? ORDER BY tashkent_timestamp ASC', (league_id, round_num))
    else:
        cursor.execute('SELECT * FROM matches WHERE league_id = ? ORDER BY round_num ASC, tashkent_timestamp ASC', (league_id,))
    
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        events = []
        if r["events_json"]:
            try:
                events = json.loads(r["events_json"])
            except Exception:
                pass

        result.append({
            "id": r["id"],
            "leagueId": r["league_id"],
            "round": r["round_num"],
            "roundName": r["round_name"],
            "homeTeam": {
                "id": r["home_id"],
                "name": r["home_name"],
                "score": r["home_score"],
                "badge": r["home_badge"]
            },
            "awayTeam": {
                "id": r["away_id"],
                "name": r["away_name"],
                "score": r["away_score"],
                "badge": r["away_badge"]
            },
            "isLive": bool(r["is_live"]),
            "isFinished": bool(r["is_finished"]),
            "scoreStr": r["score_str"],
            "liveTime": r["live_time"],
            "stadium": r["stadium"] or "Markaziy stadion",
            "referee": r["referee"] or "Bosh hakam",
            "events": events,
            "tashkent": {
                "date": r["tashkent_date"],
                "time": r["tashkent_time"],
                "displayDay": r["tashkent_display"],
                "timestamp": r["tashkent_timestamp"]
            }
        })
    return result

def get_rounds_summary(league_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT round_num, round_name, 
               COUNT(*) as total_matches,
               SUM(is_finished) as finished_matches,
               SUM(is_live) as live_matches
        FROM matches 
        WHERE league_id = ? 
        GROUP BY round_num 
        ORDER BY round_num ASC
    ''', (league_id,))
    rows = cursor.fetchall()
    conn.close()

    rounds = []
    current_round = rows[0]["round_num"] if rows else 1

    for r in rows:
        r_num = r["round_num"]
        total = r["total_matches"]
        finished = r["finished_matches"] or 0
        live = r["live_matches"] or 0
        
        # Determine active round: prefer round with live or uncompleted games
        if live > 0 or (finished < total):
            current_round = r_num

        rounds.append({
            "round": r_num,
            "name": r["round_name"],
            "total": total,
            "finished": finished,
            "live": live,
            "isCurrent": (r_num == current_round)
        })

    return {"rounds": rounds, "currentRound": current_round}

def get_standings_from_db(league_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM standings WHERE league_id = ? ORDER BY rank ASC', (league_id,))
    rows = cursor.fetchall()
    conn.close()

    return [{
        "rank": r["rank"],
        "id": r["team_id"],
        "name": r["name"],
        "shortName": r["short_name"],
        "played": r["played"],
        "wins": r["wins"],
        "draws": r["draws"],
        "losses": r["losses"],
        "scoresStr": r["scores_str"],
        "goalDiff": r["goal_diff"],
        "points": r["points"],
        "badge": r["badge"]
    } for r in rows]

def get_player_stats_from_db(league_id):
    """To'purarlar va assistentlar"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Top Scorers
    cursor.execute('''
        SELECT * FROM player_stats 
        WHERE league_id = ? AND goals > 0 
        ORDER BY goals DESC, assists DESC 
        LIMIT 15
    ''', (league_id,))
    scorers = [dict(r) for r in cursor.fetchall()]

    # Top Assists
    cursor.execute('''
        SELECT * FROM player_stats 
        WHERE league_id = ? AND assists > 0 
        ORDER BY assists DESC, goals DESC 
        LIMIT 15
    ''', (league_id,))
    assists = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {"topScorers": scorers, "topAssists": assists}

def get_team_fixtures(team_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM matches 
        WHERE home_name LIKE ? OR away_name LIKE ? 
        ORDER BY tashkent_timestamp ASC
    ''', (f"%{team_name}%", f"%{team_name}%"))
    rows = cursor.fetchall()
    conn.close()

    completed = None
    upcoming = None

    for r in rows:
        events = []
        if r["events_json"]:
            try:
                events = json.loads(r["events_json"])
            except Exception:
                pass

        item = {
            "id": r["id"],
            "roundName": r["round_name"],
            "homeTeam": {"name": r["home_name"], "badge": r["home_badge"], "score": r["home_score"]},
            "awayTeam": {"name": r["away_name"], "badge": r["away_badge"], "score": r["away_score"]},
            "isFinished": bool(r["is_finished"]),
            "scoreStr": r["score_str"],
            "events": events,
            "tashkent": {
                "date": r["tashkent_date"],
                "time": r["tashkent_time"],
                "displayDay": r["tashkent_display"],
                "timestamp": r["tashkent_timestamp"]
            }
        }
        if r["is_finished"]:
            completed = item
        elif not upcoming:
            upcoming = item

    return {"lastMatch": completed, "nextMatch": upcoming}

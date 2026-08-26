import sqlite3
import json
import time
import os
import sys
import http.client
from datetime import datetime, timedelta
import pytz
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, SUPPORTED_LEAGUES

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), 'futbol.db')
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_date_from_rapidapi(date_str):
    """Fetch matches on specific date YYYYMMDD"""
    try:
        conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': RAPIDAPI_HOST,
            'Content-Type': 'application/json'
        }
        conn.request('GET', f'/football-get-matches-by-date?date={date_str}', headers=headers)
        res = conn.getresponse()
        raw = res.read().decode('utf-8', errors='ignore')
        data = json.loads(raw)
        return data.get('response', {}).get('matches', [])
    except Exception as e:
        print(f"Fetch date error ({date_str}): {e}")
        return []

def to_tashkent_time(utc_time_str):
    if not utc_time_str:
        return {"date": "", "time": "--:--", "display": "Tez kunda", "displayDay": "Tez kunda", "timestamp": 0}
    try:
        clean_str = utc_time_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(clean_str)
        tashkent_dt = dt.astimezone(TASHKENT_TZ)
        
        now = datetime.now(TASHKENT_TZ)
        is_today = (tashkent_dt.date() == now.date())
        is_tomorrow = ((tashkent_dt.date() - now.date()).days == 1)
        is_yesterday = ((now.date() - tashkent_dt.date()).days == 1)
        
        time_str = tashkent_dt.strftime("%H:%M")
        date_str = tashkent_dt.strftime("%d.%m.%Y")
        day_month = tashkent_dt.strftime("%d-%b")
        
        if is_today:
            display_day = "Bugun"
        elif is_tomorrow:
            display_day = "Ertaga"
        elif is_yesterday:
            display_day = "Kecha"
        else:
            display_day = day_month

        return {
            "date": date_str,
            "time": time_str,
            "displayDay": display_day,
            "displayTime": f"{display_day} {time_str}",
            "timestamp": tashkent_dt.timestamp(),
            "iso": tashkent_dt.isoformat()
        }
    except Exception:
        return {"date": "", "time": "--:--", "display": "Tez kunda", "displayDay": "Tez kunda", "timestamp": 0}

def sync_2026_season():
    """2026-2027 mavsum o'yinlarini sanalar bo'yicha tortib SQLite ga yozish"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear old legacy matches
    cursor.execute('DELETE FROM matches')
    conn.commit()

    # Target leagues IDs
    target_league_ids = [47, 87, 71, 55, 42, 54] # APL, La Liga, Turkey, Serie A, UCL, Bundesliga

    # Dates to fetch (August 15, 2026 to September 15, 2026 - covers Round 1, 2, 3, 4)
    start_date = datetime(2026, 8, 15)
    dates_to_check = [(start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range(30)]

    print(f"📅 2026-2027 mavsum o'yinlari {len(dates_to_check)} kunlik taqvim bo'yicha yuklanmoqda...")
    
    collected_matches = []
    for d in dates_to_check:
        matches = fetch_date_from_rapidapi(d)
        for m in matches:
            lid = m.get('leagueId')
            if lid in target_league_ids:
                collected_matches.append((lid, m))
        time.sleep(0.15) # gentle API rate limit

    print(f"✅ Top ligalardan jami {len(collected_matches)} ta 2026/2027 mavsum o'yinlari topildi.")

    # Group by league and determine rounds based on dates
    by_league = {}
    for lid, m in collected_matches:
        if lid not in by_league:
            by_league[lid] = []
        by_league[lid].append(m)

    now_ts = time.time()

    for lid, matches_list in by_league.items():
        # Sort chronologically
        matches_list.sort(key=lambda m: m.get('status', {}).get('utcTime') or m.get('time') or '')
        
        # In a league, matches on the same weekend/week form a round
        # Let's group by week / round:
        # Aug 21-25: 1-tur, Aug 28-31: 2-tur, Sep 04-07: 3-tur, Sep 11-14: 4-tur
        for m in matches_list:
            match_id = str(m.get('id'))
            st = m.get('status', {})
            utc_time = st.get('utcTime') or m.get('time')
            t_info = to_tashkent_time(utc_time)
            
            # Determine round by date
            m_dt = datetime.fromtimestamp(t_info['timestamp']) if t_info['timestamp'] > 0 else datetime(2026, 8, 22)
            if m_dt < datetime(2026, 8, 27):
                round_num = 1
            elif m_dt < datetime(2026, 9, 3):
                round_num = 2
            elif m_dt < datetime(2026, 9, 10):
                round_num = 3
            else:
                round_num = 4
            
            round_name = f"{round_num}-tur"

            is_live = 1 if (st.get('started') and not st.get('finished') and not st.get('cancelled')) else 0
            is_finished = 1 if (st.get('finished') or bool(st.get('scoreStr'))) else 0

            home_id = m.get('home', {}).get('id')
            home_name = m.get('home', {}).get('name') or 'Mezbon'
            home_badge = f"https://images.fotmob.com/image_resources/logo/teamlogo/{home_id}.png" if home_id else ""
            home_score = str(m.get('home', {}).get('score', ''))

            away_id = m.get('away', {}).get('id')
            away_name = m.get('away', {}).get('name') or 'Mehmon'
            away_badge = f"https://images.fotmob.com/image_resources/logo/teamlogo/{away_id}.png" if away_id else ""
            away_score = str(m.get('away', {}).get('score', ''))

            score_str = st.get('scoreStr')
            if not score_str and is_finished and home_score and away_score:
                score_str = f"{home_score} : {away_score}"

            live_time = st.get('liveTime', {}).get('short') or ('LIVE' if is_live else None)

            cursor.execute('''
                INSERT OR REPLACE INTO matches (
                    id, league_id, round_num, round_name,
                    home_id, home_name, home_badge,
                    away_id, away_name, away_badge,
                    score_str, home_score, away_score,
                    is_live, is_finished, live_time,
                    utc_time, tashkent_date, tashkent_time, tashkent_display,
                    tashkent_timestamp, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_id, lid, round_num, round_name,
                home_id, home_name, home_badge,
                away_id, away_name, away_badge,
                score_str, home_score, away_score,
                is_live, is_finished, live_time,
                utc_time, t_info['date'], t_info['time'], t_info['displayDay'],
                t_info['timestamp'], now_ts
            ))

    cursor.execute('INSERT OR REPLACE INTO sync_meta (key, last_synced) VALUES (?, ?)', ("matches_2026_season", now_ts))
    conn.commit()
    conn.close()
    print("🎉 Barcha 2026-2027 mavsum o'yinlari SQLite ga muvaffaqiyatli saqlandi!")

if __name__ == '__main__':
    sync_2026_season()

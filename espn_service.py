import urllib.request
import json
import ssl
import time
import sys
from datetime import datetime, timedelta
import pytz
from database import get_db_connection, init_db

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

ESPN_LEAGUE_MAP = {
    47: "eng.1",            # APL (Premier League)
    87: "esp.1",            # La Liga (Ispaniya)
    55: "ita.1",            # Serie A (Italiya)
    54: "ger.1",            # Bundesliga (Germaniya)
    71: "tur.1",            # Turkish Süper Lig
    42: "uefa.champions"    # UEFA Champions League
}

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def fetch_espn_scoreboard(espn_league_slug, date_str):
    """Fetch official ESPN match data including goals, cards, time"""
    url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_league_slug}/scoreboard?dates={date_str}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as res:
            return json.loads(res.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        return None

def parse_espn_event(ev, league_id, round_num=1):
    comp = ev.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) < 2:
        return None

    home_comp = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
    away_comp = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])

    home_team = home_comp.get('team', {})
    away_team = away_comp.get('team', {})

    home_score = home_comp.get('score')
    away_score = away_comp.get('score')

    status_type = comp.get('status', {}).get('type', {})
    is_finished = status_type.get('completed', False)
    is_live = status_type.get('state') == 'in'
    live_time = comp.get('status', {}).get('displayClock') or ('LIVE' if is_live else None)

    utc_date_str = ev.get('date')
    t_info = to_tashkent_time_dict(utc_date_str)

    score_str = None
    if is_finished or is_live:
        score_str = f"{home_score or 0} : {away_score or 0}"

    # Extract Goalscorers and Cards
    events = []
    for d in comp.get('details', []):
        type_text = d.get('type', {}).get('text', '')
        clock = d.get('clock', {}).get('displayValue', '')
        # Clean clock string: 90'+9' -> 90+9'
        clock_clean = clock.replace("'", "").replace("+", "+")
        
        athlete = ""
        if d.get('athletesInvolved'):
            athlete = d['athletesInvolved'][0].get('displayName', '')
        if not athlete:
            athlete = d.get('text', '')

        team_id = d.get('team', {}).get('id')
        team_side = 'home' if str(team_id) == str(home_team.get('id')) else 'away'

        if 'Goal' in type_text or 'Penalty' in type_text:
            detail_label = 'Gol'
            if 'Penalty' in type_text:
                detail_label = 'Penalti'
            elif 'Own' in type_text:
                detail_label = 'Avtogol'
            elif 'Header' in type_text:
                detail_label = 'Bosh bilan'

            events.append({
                "type": "goal",
                "minute": clock_clean,
                "player": athlete,
                "team": team_side,
                "detail": detail_label
            })
        elif 'Card' in type_text:
            events.append({
                "type": "card",
                "minute": clock_clean,
                "player": athlete,
                "team": team_side,
                "card": "red" if 'Red' in type_text else "yellow"
            })

    venue = comp.get('venue', {}).get('fullName', '')
    referee = ""
    officials = comp.get('officials', [])
    if officials:
        referee = officials[0].get('displayName', '')

    return {
        "id": f"espn_{ev.get('id')}",
        "leagueId": league_id,
        "roundNum": round_num,
        "roundName": f"{round_num}-tur",
        "homeId": home_team.get('id'),
        "homeName": home_team.get('shortDisplayName') or home_team.get('name'),
        "homeBadge": home_team.get('logo') or f"https://images.fotmob.com/image_resources/logo/teamlogo/{home_team.get('id')}.png",
        "homeScore": str(home_score or ''),
        "awayId": away_team.get('id'),
        "awayName": away_team.get('shortDisplayName') or away_team.get('name'),
        "awayBadge": away_team.get('logo') or f"https://images.fotmob.com/image_resources/logo/teamlogo/{away_team.get('id')}.png",
        "awayScore": str(away_score or ''),
        "scoreStr": score_str,
        "isLive": 1 if is_live else 0,
        "isFinished": 1 if is_finished else 0,
        "liveTime": live_time,
        "utcTime": utc_date_str,
        "tashkentDate": t_info['date'],
        "tashkentTime": t_info['time'],
        "tashkentDisplay": t_info['displayDay'],
        "tashkentTimestamp": t_info['timestamp'],
        "stadium": venue,
        "referee": referee,
        "events": events
    }

def to_tashkent_time_dict(utc_date_str):
    if not utc_date_str:
        return {"date": "", "time": "--:--", "display": "Tez kunda", "displayDay": "Tez kunda", "timestamp": 0}
    try:
        clean_str = utc_date_str.replace('Z', '+00:00')
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
            "timestamp": tashkent_dt.timestamp()
        }
    except Exception:
        return {"date": "", "time": "--:--", "display": "Tez kunda", "displayDay": "Tez kunda", "timestamp": 0}

def sync_espn_matches():
    """Sync real 2026/2027 official match data from ESPN for top leagues"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = time.time()

    # Dates covering Round 1 (Aug 21-25) and Round 2 (Aug 28-31)
    round1_dates = ["20260821", "20260822", "20260823", "20260824", "20260825"]
    round2_dates = ["20260828", "20260829", "20260830", "20260831", "20260901"]

    for league_id, slug in ESPN_LEAGUE_MAP.items():
        print(f"🔄 ESPN dan {slug} (Liga {league_id}) yuklanmoqda...")
        
        # Round 1
        for d in round1_dates:
            data = fetch_espn_scoreboard(slug, d)
            if data and 'events' in data:
                for ev in data['events']:
                    parsed = parse_espn_event(ev, league_id, round_num=1)
                    if parsed:
                        save_single_match(cursor, parsed, now_ts)

        # Round 2
        for d in round2_dates:
            data = fetch_espn_scoreboard(slug, d)
            if data and 'events' in data:
                for ev in data['events']:
                    parsed = parse_espn_event(ev, league_id, round_num=2)
                    if parsed:
                        save_single_match(cursor, parsed, now_ts)

    conn.commit()
    conn.close()
    print("✅ ESPN dan 100% haqiqiy matchlar va gollar muvaffaqiyatli saqlandi!")

def save_single_match(cursor, p, now_ts):
    cursor.execute('''
        INSERT OR REPLACE INTO matches (
            id, league_id, round_num, round_name,
            home_id, home_name, home_badge,
            away_id, away_name, away_badge,
            score_str, home_score, away_score,
            is_live, is_finished, live_time,
            utc_time, tashkent_date, tashkent_time, tashkent_display,
            tashkent_timestamp, stadium, referee, events_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        p["id"], p["leagueId"], p["roundNum"], p["roundName"],
        p["homeId"], p["homeName"], p["homeBadge"],
        p["awayId"], p["awayName"], p["awayBadge"],
        p["scoreStr"], p["homeScore"], p["awayScore"],
        p["isLive"], p["isFinished"], p["liveTime"],
        p["utcTime"], p["tashkentDate"], p["tashkentTime"], p["tashkentDisplay"],
        p["tashkentTimestamp"], p["stadium"], p["referee"], json.dumps(p["events"]), now_ts
    ))

if __name__ == '__main__':
    sync_espn_matches()

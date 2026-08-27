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
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

ESPN_LEAGUE_MAP = {
    47: ("eng.1", "APL"),
    87: ("esp.1", "La Liga"),
    55: ("ita.1", "Serie A"),
    54: ("ger.1", "Bundesliga"),
    71: ("tur.1", "Turkiya"),
    42: ("uefa.champions", "Chempionlar Ligasi")
}

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def fetch_json(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=8) as res:
            return json.loads(res.read().decode('utf-8', errors='ignore'))
    except Exception:
        return None

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

    events = []
    for d in comp.get('details', []):
        type_text = d.get('type', {}).get('text', '')
        clock = d.get('clock', {}).get('displayValue', '')
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

def sync_all_live_data():
    """Sync real-time matches, standings, and recompute top scorers dynamically"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = time.time()

    # Dynamic date range: from 7 days ago to 7 days ahead
    base_date = datetime.now()
    dates_to_check = [(base_date + timedelta(days=offset)).strftime("%Y%m%d") for offset in range(-7, 8)]

    # 1. Sync Matches from ESPN
    for league_id, (slug, lname) in ESPN_LEAGUE_MAP.items():
        for d in dates_to_check:
            # Determine round: before Aug 26 -> round 1, Aug 26 onwards -> round 2
            r_num = 2 if int(d) >= 20260826 else 1
            data = fetch_json(f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={d}")
            if data and 'events' in data:
                for ev in data['events']:
                    parsed = parse_espn_event(ev, league_id, round_num=r_num)
                    if parsed:
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
                            parsed["id"], parsed["leagueId"], parsed["roundNum"], parsed["roundName"],
                            parsed["homeId"], parsed["homeName"], parsed["homeBadge"],
                            parsed["awayId"], parsed["awayName"], parsed["awayBadge"],
                            parsed["scoreStr"], parsed["homeScore"], parsed["awayScore"],
                            parsed["isLive"], parsed["isFinished"], parsed["liveTime"],
                            parsed["utcTime"], parsed["tashkentDate"], parsed["tashkentTime"], parsed["tashkentDisplay"],
                            parsed["tashkentTimestamp"], parsed["stadium"], parsed["referee"], json.dumps(parsed["events"]), now_ts
                        ))

    # 2. Sync Official Standings from ESPN
    for league_id, (slug, lname) in ESPN_LEAGUE_MAP.items():
        data = fetch_json(f"https://site.web.api.espn.com/apis/v2/sports/soccer/{slug}/standings")
        if data:
            children = data.get('children', [])
            entries = []
            if children and 'standings' in children[0]:
                entries = children[0]['standings'].get('entries', [])
            elif 'standings' in data:
                entries = data['standings'].get('entries', [])

            if entries:
                cursor.execute('DELETE FROM standings WHERE league_id = ?', (league_id,))
                for idx, e in enumerate(entries):
                    team = e.get('team', {})
                    team_id = team.get('id')
                    name = team.get('displayName') or team.get('name')
                    short_name = team.get('shortDisplayName') or name
                    badge = team.get('logos', [{}])[0].get('href') if team.get('logos') else f"https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}.png"

                    stats_dict = {s.get('name'): s.get('value', 0) for s in e.get('stats', [])}

                    rank = int(stats_dict.get('rank', idx + 1))
                    games_played = int(stats_dict.get('gamesPlayed', 0))
                    wins = int(stats_dict.get('wins', 0))
                    draws = int(stats_dict.get('ties', 0))
                    losses = int(stats_dict.get('losses', 0))
                    points = int(stats_dict.get('points', 0))
                    goal_diff = int(stats_dict.get('pointDifferential', 0))
                    scores_str = f"{int(stats_dict.get('pointsFor', 0))}-{int(stats_dict.get('pointsAgainst', 0))}"

                    cursor.execute('''
                        INSERT INTO standings (
                            league_id, team_id, rank, name, short_name,
                            played, wins, draws, losses, scores_str, goal_diff, points, badge, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        league_id, team_id, rank, name, short_name,
                        games_played, wins, draws, losses, scores_str, goal_diff, points, badge, now_ts
                    ))

    # 3. Dynamically re-compute Top Scorers from all actual match events in SQLite
    cursor.execute('DELETE FROM player_stats WHERE league_id != 1001')
    for league_id in ESPN_LEAGUE_MAP.keys():
        cursor.execute('SELECT events_json, home_name, away_name FROM matches WHERE league_id = ?', (league_id,))
        match_rows = cursor.fetchall()
        scorers = {}
        player_teams = {}

        for row in match_rows:
            events = json.loads(row[0]) if row[0] else []
            for ev in events:
                if ev.get('type') == 'goal' and ev.get('detail') != 'Avtogol':
                    p_name = ev.get('player')
                    if p_name:
                        scorers[p_name] = scorers.get(p_name, 0) + 1
                        team_name = row[1] if ev.get('team') == 'home' else row[2]
                        player_teams[p_name] = team_name

        for p_name, g_count in sorted(scorers.items(), key=lambda x: x[1], reverse=True):
            t_name = player_teams.get(p_name, '')
            cursor.execute('''
                INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (league_id, p_name, t_name, f"https://images.fotmob.com/image_resources/logo/leaguelogo/dark/{league_id}.png", "", g_count, 0, 2, 0, now_ts))

    # 4. Sync Uzbekistan Super League
    try:
        from sync_uzb_full import sync_uzbekistan_full
        sync_uzbekistan_full()
    except Exception as e:
        print("Uzbekistan sync error:", e)

    conn.commit()
    conn.close()
    print("✅ Barcha 7 ta chempionat (O'zbekiston, La Liga, APL, Turkiya, A Seriya, UCL, Bundesliga) birgalikda to'liq yangilandi!")

def sync_espn_matches():
    sync_all_live_data()

if __name__ == '__main__':
    sync_all_live_data()

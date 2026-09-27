import urllib.request
import json
import ssl
import time
import sys
from datetime import datetime, timedelta
import pytz
from database import get_db_connection

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

UZ_MONTHS = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
             "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]

SYNC_DAYS_BACK = 7
SYNC_DAYS_AHEAD = 10


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
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as res:
            return json.loads(res.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"⚠️ ESPN so'rovi muvaffaqiyatsiz: {url} ({e})")
        return None


def week_round(ts):
    """Group matches into Tuesday–Monday weeks so a Fri–Mon matchday stays together."""
    d = datetime.fromtimestamp(ts, TASHKENT_TZ).date()
    start = d - timedelta(days=(d.weekday() - 1) % 7)
    end = start + timedelta(days=6)
    if start.month == end.month:
        name = f"{start.day}–{end.day} {UZ_MONTHS[end.month - 1]}"
    else:
        name = f"{start.day} {UZ_MONTHS[start.month - 1]} – {end.day} {UZ_MONTHS[end.month - 1]}"
    return int(start.strftime("%Y%m%d")), name


def to_tashkent_time_dict(utc_date_str):
    if not utc_date_str:
        return {"date": "", "time": "--:--", "timestamp": 0}
    try:
        dt = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
        tashkent_dt = dt.astimezone(TASHKENT_TZ)
        return {
            "date": tashkent_dt.strftime("%d.%m.%Y"),
            "time": tashkent_dt.strftime("%H:%M"),
            "timestamp": tashkent_dt.timestamp()
        }
    except Exception:
        return {"date": "", "time": "--:--", "timestamp": 0}


def parse_espn_event(ev, league_id):
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

    status = comp.get('status', {})
    status_type = status.get('type', {})
    is_finished = status_type.get('completed', False)
    is_live = status_type.get('state') == 'in'
    live_time = None
    if is_live:
        live_time = status_type.get('shortDetail') or status.get('displayClock') or 'LIVE'

    utc_date_str = ev.get('date')
    t_info = to_tashkent_time_dict(utc_date_str)
    round_num, round_name = week_round(t_info['timestamp']) if t_info['timestamp'] else (0, "Sana belgilanmagan")

    score_str = None
    if is_finished or is_live:
        score_str = f"{home_score or 0} : {away_score or 0}"

    events = []
    for d in comp.get('details', []):
        type_text = d.get('type', {}).get('text', '')
        clock_clean = d.get('clock', {}).get('displayValue', '').replace("'", "")

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

    return (
        f"espn_{ev.get('id')}", league_id, round_num, round_name,
        home_team.get('id'), home_team.get('shortDisplayName') or home_team.get('name'),
        home_team.get('logo') or f"https://images.fotmob.com/image_resources/logo/teamlogo/{home_team.get('id')}.png",
        away_team.get('id'), away_team.get('shortDisplayName') or away_team.get('name'),
        away_team.get('logo') or f"https://images.fotmob.com/image_resources/logo/teamlogo/{away_team.get('id')}.png",
        score_str, str(home_score or ''), str(away_score or ''),
        1 if is_live else 0, 1 if is_finished else 0, live_time,
        utc_date_str, t_info['date'], t_info['time'], "",
        t_info['timestamp'], venue, referee, json.dumps(events), time.time()
    )


def sync_matches(days_back=SYNC_DAYS_BACK):
    """Fetch scoreboards (one request per league for the whole date window)."""
    now = datetime.now(TASHKENT_TZ)
    date_range = f"{(now - timedelta(days=days_back)).strftime('%Y%m%d')}-{(now + timedelta(days=SYNC_DAYS_AHEAD)).strftime('%Y%m%d')}"

    conn = get_db_connection()
    cursor = conn.cursor()
    total = 0
    live = 0
    for league_id, (slug, _) in ESPN_LEAGUE_MAP.items():
        data = fetch_json(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={date_range}&limit=300")
        if not data:
            continue
        for ev in data.get('events', []):
            row = parse_espn_event(ev, league_id)
            if not row:
                continue
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
            ''', row)
            total += 1
            live += row[13]

    # Old ESPN rows were stored with a hardcoded round 1/2; regroup them into weeks.
    cursor.execute("SELECT id, tashkent_timestamp FROM matches WHERE id LIKE 'espn_%' AND round_num < 10000000 AND tashkent_timestamp > 0")
    for match_id, ts in cursor.fetchall():
        r_num, r_name = week_round(ts)
        cursor.execute('UPDATE matches SET round_num = ?, round_name = ? WHERE id = ?', (r_num, r_name, match_id))

    conn.commit()
    conn.close()
    print(f"⚽ {total} ta o'yin yangilandi ({live} tasi jonli)")
    return live


def sync_standings():
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = time.time()
    for league_id, (slug, _) in ESPN_LEAGUE_MAP.items():
        data = fetch_json(f"https://site.api.espn.com/apis/v2/sports/soccer/{slug}/standings")
        if not data:
            continue
        children = data.get('children', [])
        entries = []
        if children and 'standings' in children[0]:
            entries = children[0]['standings'].get('entries', [])
        elif 'standings' in data:
            entries = data['standings'].get('entries', [])
        if not entries:
            continue

        cursor.execute('DELETE FROM standings WHERE league_id = ?', (league_id,))
        for idx, e in enumerate(entries):
            team = e.get('team', {})
            team_id = team.get('id')
            name = team.get('displayName') or team.get('name')
            short_name = team.get('shortDisplayName') or name
            badge = team.get('logos', [{}])[0].get('href') if team.get('logos') else f"https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}.png"
            stats = {s.get('name'): s.get('value', 0) for s in e.get('stats', [])}

            cursor.execute('''
                INSERT INTO standings (
                    league_id, team_id, rank, name, short_name,
                    played, wins, draws, losses, scores_str, goal_diff, points, badge, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                league_id, team_id, int(stats.get('rank') or idx + 1), name, short_name,
                int(stats.get('gamesPlayed', 0)), int(stats.get('wins', 0)), int(stats.get('ties', 0)),
                int(stats.get('losses', 0)),
                f"{int(stats.get('pointsFor', 0))}-{int(stats.get('pointsAgainst', 0))}",
                int(stats.get('pointDifferential', 0)), int(stats.get('points', 0)), badge, now_ts
            ))
    conn.commit()
    conn.close()


def recompute_scorers():
    """Rebuild top scorers from the goal events stored in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = time.time()
    cursor.execute('DELETE FROM player_stats WHERE league_id != 1001')
    for league_id in ESPN_LEAGUE_MAP.keys():
        cursor.execute('SELECT events_json, home_name, away_name FROM matches WHERE league_id = ?', (league_id,))
        scorers = {}
        player_teams = {}
        for events_json, home_name, away_name in cursor.fetchall():
            for ev in (json.loads(events_json) if events_json else []):
                if ev.get('type') == 'goal' and ev.get('detail') != 'Avtogol' and ev.get('player'):
                    p_name = ev['player']
                    scorers[p_name] = scorers.get(p_name, 0) + 1
                    player_teams[p_name] = home_name if ev.get('team') == 'home' else away_name

        for p_name, g_count in sorted(scorers.items(), key=lambda x: x[1], reverse=True):
            cursor.execute('''
                INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (league_id, p_name, player_teams.get(p_name, ''), f"https://images.fotmob.com/image_resources/logo/leaguelogo/dark/{league_id}.png", "", g_count, 0, 0, 0, now_ts))
    conn.commit()
    conn.close()


def sync_all_live_data():
    sync_matches(days_back=60)
    sync_standings()
    recompute_scorers()
    print("✅ Barcha chempionatlar ESPN'dan yangilandi")


if __name__ == '__main__':
    sync_all_live_data()

import urllib.request
import json
import ssl
import time
import sys
import sqlite3
from database import get_db_connection

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = 'futbol.db'

ESPN_LEAGUE_MAP = {
    47: "eng.1",            # APL
    87: "esp.1",            # La Liga
    55: "ita.1",            # Serie A
    54: "ger.1",            # Bundesliga
    71: "tur.1",            # Turkish Süper Lig
    42: "uefa.champions"    # UEFA Champions League
}

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def sync_espn_standings():
    """Fetch official standings from ESPN and save into SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_ts = time.time()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    for league_id, slug in ESPN_LEAGUE_MAP.items():
        url = f"https://site.web.api.espn.com/apis/v2/sports/soccer/{slug}/standings"
        print(f"🔄 ESPN dan Turnir Jadvali yuklanmoqda: {slug} (Liga {league_id})...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as res:
                data = json.loads(res.read().decode('utf-8', errors='ignore'))
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
                        stats_display = {s.get('name'): s.get('displayValue', '') for s in e.get('stats', [])}

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
                    print(f"  ✅ Liga {league_id} ({slug}) ga {len(entries)} ta jamoa jadvali saqlandi!")
        except Exception as e:
            print(f"  ❌ Standings error ({slug}): {e}")

    # Seed stats (to'purarlar) for European leagues
    seed_european_stats(cursor, now_ts)

    conn.commit()
    conn.close()
    print("🎉 Barcha chempionatlar jadvallari va to'purarlari SQLite bazasiga muvaffaqiyatli saqlandi!")

def seed_european_stats(cursor, now_ts):
    # APL Stats
    cursor.execute('DELETE FROM player_stats WHERE league_id = 47')
    apl_stats = [
        (47, "Anthony Elanga", "Newcastle", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", "", 1, 0, 1, 0),
        (47, "Cody Gakpo", "Liverpool", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 1, 0, 1, 0),
        (47, "Dominik Szoboszlai", "Liverpool", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 1, 0, 1, 1),
        (47, "Joe Willock", "Newcastle", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", "", 1, 0, 1, 0),
        (47, "Bukayo Saka", "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "", 1, 1, 1, 0),
        (47, "Kai Havertz", "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "", 1, 0, 1, 0),
        (47, "Jack Hinshelwood", "Brighton", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", "", 2, 0, 1, 0),
        (47, "Marcus Tavernier", "Bournemouth", "https://images.fotmob.com/image_resources/logo/teamlogo/9826.png", "", 1, 0, 1, 0),
        (47, "Josko Gvardiol", "Man City", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 1, 0, 1, 0),
        (47, "Martin Ødegaard", "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "", 0, 1, 1, 0),
        (47, "Phil Foden", "Man City", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 0, 1, 1, 0)
    ]
    for s in apl_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # La Liga Stats
    cursor.execute('DELETE FROM player_stats WHERE league_id = 87')
    laliga_stats = [
        (87, "Robert Lewandowski", "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", "", 2, 0, 1, 0),
        (87, "Kylian Mbappé", "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", "", 1, 0, 1, 0),
        (87, "Lamine Yamal", "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", "", 1, 2, 1, 0),
        (87, "Vinicius Junior", "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", "", 1, 1, 1, 0),
        (87, "Julián Álvarez", "Atletico Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/9906.png", "", 1, 0, 1, 0),
        (87, "Dani Olmo", "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", "", 1, 1, 1, 0)
    ]
    for s in laliga_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # Turkey Stats
    cursor.execute('DELETE FROM player_stats WHERE league_id = 71')
    tur_stats = [
        (71, "Mauro Icardi", "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 2, 1, 1, 0),
        (71, "Husniddin Aliqulov 🇺🇿", "Rizespor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "", 1, 0, 1, 0),
        (71, "Edin Dzeko", "Fenerbahçe", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 1, 0, 1, 0),
        (71, "Barış Alper Yılmaz", "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 1, 1, 0),
        (71, "Dries Mertens", "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 1, 1, 0)
    ]
    for s in tur_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # Serie A Stats
    cursor.execute('DELETE FROM player_stats WHERE league_id = 55')
    ita_stats = [
        (55, "Lautaro Martínez", "Inter", "https://images.fotmob.com/image_resources/logo/teamlogo/8636.png", "", 2, 0, 1, 0),
        (55, "Eldor Shomurodov 🇺🇿", "Roma", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 1, 1, 0),
        (55, "Paulo Dybala", "Roma", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 1, 1, 0),
        (55, "Dušan Vlahović", "Juventus", "https://images.fotmob.com/image_resources/logo/teamlogo/9885.png", "", 1, 0, 1, 0),
        (55, "Rafael Leão", "Milan", "https://images.fotmob.com/image_resources/logo/teamlogo/8564.png", "", 1, 1, 1, 0)
    ]
    for s in ita_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

if __name__ == '__main__':
    sync_espn_standings()

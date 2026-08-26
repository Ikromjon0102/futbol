import sqlite3
import json
import time
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), 'futbol.db')

def update_uzbekistan_superleague():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_ts = time.time()

    # 1. Update Uzbekistan Standings with EXACT 16 teams from Google
    cursor.execute('DELETE FROM standings WHERE league_id = 1001')

    # Team logos map (reliable high-res badges)
    uzb_teams = [
        (1, "Neftchi Fergana", "Neftchi", 19, 14, 3, 2, "45-10", 35, 45, "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png"),
        (2, "Paxtakor", "Paxtakor", 19, 11, 7, 1, "31-18", 13, 40, "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png"),
        (3, "Buxoro", "Buxoro", 19, 10, 4, 5, "28-20", 8, 34, "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png"),
        (4, "Navbahor", "Navbahor", 18, 10, 4, 4, "29-17", 12, 34, "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png"),
        (5, "AGMK (OKMK)", "OKMK", 19, 8, 5, 6, "27-25", 2, 29, "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png"),
        (6, "Lokomotiv Tashkent", "Lokomotiv", 18, 8, 4, 6, "28-25", 3, 28, "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png"),
        (7, "Andijan", "Andijon", 19, 8, 3, 8, "24-20", 4, 27, "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png"),
        (8, "Dinamo Samarqand", "Dinamo", 19, 7, 5, 7, "29-30", -1, 26, "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png"),
        (9, "Nasaf", "Nasaf", 18, 6, 7, 5, "20-17", 3, 25, "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png"),
        (10, "Sogdiana", "So'g'diyona", 19, 7, 3, 9, "32-39", -7, 24, "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png"),
        (11, "Qizilqum", "Qizilqum", 18, 6, 2, 10, "16-26", -10, 20, "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png"),
        (12, "Xorazm", "Xorazm", 19, 5, 5, 9, "17-28", -11, 20, "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png"),
        (13, "Surkhon", "Surxon", 19, 5, 5, 9, "16-26", -10, 20, "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png"),
        (14, "Kokand 1912", "Qo'qon 1912", 19, 4, 7, 8, "17-26", -9, 19, "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png"),
        (15, "Bunyodkor", "Bunyodkor", 18, 6, 1, 11, "19-27", -8, 19, "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png"),
        (16, "Mash'al", "Mash'al", 18, 1, 1, 16, "8-32", -24, 4, "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png")
    ]

    for rank, name, sname, mp, w, d, l, scores, gd, pts, badge in uzb_teams:
        team_id = 1000 + rank
        cursor.execute('''
            INSERT INTO standings (
                league_id, team_id, rank, name, short_name, played, wins, draws, losses, scores_str, goal_diff, points, badge, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1001, team_id, rank, name, sname, mp, w, d, l, scores, gd, pts, badge, now_ts))

    # 2. Update Uzbekistan Matches (19-tur completed & 20-tur upcoming)
    cursor.execute('DELETE FROM matches WHERE league_id = 1001')

    uzb_matches = [
        # 19-tur (Yakunlangan o'yinlar)
        ("uzb_19_1", 1001, 19, "19-tur", 1001, "Neftchi Fergana", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", 1016, "Mash'al", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", "3 : 0", "3", "0", 0, 1, None, "2026-08-21T14:30:00Z", "21.08.2026", "19:30", "21-Aug", 1787322600, "Istiqlol Stadioni, Farg'ona", "Ilgyz Tantashev", json.dumps([
            {"type": "goal", "minute": 18, "player": "Khusayin Norchaev", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 45, "player": "Khusayin Norchaev", "team": "home", "detail": "Gol (Bosh bilan)"},
            {"type": "goal", "minute": 72, "player": "Bilolxon Toshmirzayev", "team": "home", "detail": "Gol"},
            {"type": "card", "minute": 34, "player": "Abror Ismoilov", "team": "home", "card": "yellow"}
        ])),
        ("uzb_19_2", 1001, 19, "19-tur", 1002, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 1007, "Andijan", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "2 : 1", "2", "1", 0, 1, None, "2026-08-22T14:30:00Z", "22.08.2026", "19:30", "22-Aug", 1787409000, "Paxtakor Markaziy Stadioni", "Ravshan Ermatov", json.dumps([
            {"type": "goal", "minute": 22, "player": "Dragan Ceran", "team": "home", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 54, "player": "Rustam Turdimurodov", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 88, "player": "Diyor Kholmatov", "team": "home", "detail": "Gol"}
        ])),
        ("uzb_19_3", 1001, 19, "19-tur", 1003, "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", 1008, "Dinamo Samarqand", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "1 : 0", "1", "0", 0, 1, None, "2026-08-23T14:00:00Z", "23.08.2026", "19:00", "23-Aug", 1787493600, "Buxoro Arena", "Ahrol Risqullayev", json.dumps([
            {"type": "goal", "minute": 64, "player": "Jasur Khasanov", "team": "home", "detail": "Gol"}
        ])),
        ("uzb_19_4", 1001, 19, "19-tur", 1005, "AGMK (OKMK)", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", 1010, "Sogdiana", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "2 : 2", "2", "2", 0, 1, None, "2026-08-24T14:00:00Z", "24.08.2026", "19:00", "24-Aug", 1787580000, "OKMK Majmuasi, Olmaliq", "Firdavs Norsafarov", json.dumps([
            {"type": "goal", "minute": 12, "player": "Khurshid Giyosov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 39, "player": "Ljupcho Doriyev", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 61, "player": "Ljupcho Doriyev", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 83, "player": "Ruben Sanchez", "team": "home", "detail": "Gol"}
        ])),
        ("uzb_19_5", 1001, 19, "19-tur", 1009, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", 1004, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "2 : 1", "2", "1", 0, 1, None, "2026-08-24T14:30:00Z", "24.08.2026", "19:30", "24-Aug", 1787581800, "Markaziy Stadion, Qarshi", "Ilgyz Tantashev", json.dumps([
            {"type": "goal", "minute": 31, "player": "Zoran Marusic", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 58, "player": "Toma Tabatadze", "team": "away", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 79, "player": "Akmal Mozgovoy", "team": "home", "detail": "Gol"}
        ])),

        # 20-tur (Navbatdagi kelgusi o'yinlar)
        ("uzb_20_1", 1001, 20, "20-tur", 1002, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 1001, "Neftchi Fergana", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", None, None, None, 0, 0, None, "2026-08-29T14:30:00Z", "29.08.2026", "19:30", "29-Aug", 1788013800, "Paxtakor Markaziy Stadioni (Katta Derbi 🔥)", "Ravshan Ermatov", json.dumps([])),
        ("uzb_20_2", 1001, 20, "20-tur", 1004, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", 1003, "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", None, None, None, 0, 0, None, "2026-08-29T14:00:00Z", "29.08.2026", "19:00", "29-Aug", 1788012000, "Markaziy Stadion, Namangan", "Ilgyz Tantashev", json.dumps([])),
        ("uzb_20_3", 1001, 20, "20-tur", 1009, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", 1005, "AGMK (OKMK)", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", None, None, None, 0, 0, None, "2026-08-30T14:30:00Z", "30.08.2026", "19:30", "30-Aug", 1788100200, "Markaziy Stadion, Qarshi", "Ahrol Risqullayev", json.dumps([])),
        ("uzb_20_4", 1001, 20, "20-tur", 1007, "Andijan", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", 1006, "Lokomotiv Tashkent", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", None, None, None, 0, 0, None, "2026-08-30T13:00:00Z", "30.08.2026", "18:00", "30-Aug", 1788094800, "Bobur Arena, Andijon", "Firdavs Norsafarov", json.dumps([])),
        ("uzb_20_5", 1001, 20, "20-tur", 1008, "Dinamo Samarqand", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", 1012, "Xorazm", "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png", None, None, None, 0, 0, None, "2026-08-30T14:00:00Z", "30.08.2026", "19:00", "30-Aug", 1788098400, "Dinamo Stadioni, Samarqand", "Rustam Lutfullin", json.dumps([])),
        ("uzb_20_6", 1001, 20, "20-tur", 1010, "Sogdiana", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", 1014, "Kokand 1912", "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png", None, None, None, 0, 0, None, "2026-08-31T14:00:00Z", "31.08.2026", "19:00", "31-Aug", 1788184800, "So'g'diyona Stadioni, Jizzax", "Asker Najafaliyev", json.dumps([])),
        ("uzb_20_7", 1001, 20, "20-tur", 1015, "Bunyodkor", "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png", 1013, "Surkhon", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", None, None, None, 0, 0, None, "2026-08-31T14:00:00Z", "31.08.2026", "19:00", "31-Aug", 1788184800, "Bunyodkor Stadioni, Toshkent", "Vadim Agishev", json.dumps([])),
        ("uzb_20_8", 1001, 20, "20-tur", 1011, "Qizilqum", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", 1016, "Mash'al", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", None, None, None, 0, 0, None, "2026-08-31T13:30:00Z", "31.08.2026", "18:30", "31-Aug", 1788183000, "Yoshlar SM, Navoiy", "G'ayrat Jo'rayev", json.dumps([]))
    ]

    for m in uzb_matches:
        cursor.execute('''
            INSERT INTO matches (
                id, league_id, round_num, round_name, home_id, home_name, home_badge,
                away_id, away_name, away_badge, score_str, home_score, away_score,
                is_live, is_finished, live_time, utc_time, tashkent_date, tashkent_time,
                tashkent_display, tashkent_timestamp, stadium, referee, events_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*m, now_ts))

    # 3. Update Scorers (To'purarlar) for 19 rounds
    cursor.execute('DELETE FROM player_stats WHERE league_id = 1001')
    uzb_stats = [
        (1001, "Khusayin Norchaev", "Neftchi Fergana", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 15, 4, 19, 2),
        (1001, "Dragan Ceran", "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 14, 6, 19, 4),
        (1001, "Ljupcho Doriyev", "Sogdiana", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "", 11, 7, 19, 2),
        (1001, "Toma Tabatadze", "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "", 10, 3, 18, 3),
        (1001, "Zoran Marusic", "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", "", 9, 4, 18, 0),
        (1001, "Jasur Khasanov", "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "", 8, 5, 19, 1),
        (1001, "Rustam Turdimurodov", "Andijan", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 8, 3, 19, 0),
        (1001, "Khurshid Giyosov", "AGMK (OKMK)", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", "", 7, 6, 19, 2),
        (1001, "Jamshid Iskanderov", "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "", 5, 10, 18, 1),
        (1001, "Diyor Kholmatov", "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 4, 8, 18, 0),
        (1001, "Akmal Mozgovoy", "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", "", 6, 5, 18, 0)
    ]

    for s in uzb_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    conn.commit()
    conn.close()
    print("🇺🇿 O'zbekiston Superligasi (16 ta jamoa, 19-tur natijalari va 20-tur taqvimi) muvaffaqiyatli saqlandi!")

if __name__ == '__main__':
    update_uzbekistan_superleague()

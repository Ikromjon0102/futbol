import sqlite3
import json
import time
import os
import sys
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), 'futbol.db')

from database import init_db

def seed_database():
    init_db(force=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ==================== 1. LEAGUES ====================
    leagues_data = [
        (1001, "O'zbekiston", "O'zbekiston Superligasi", "O'zbekiston", "🇺🇿", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/525.png", "Milliy chempionat", 1),
        (47, "APL", "Angliya Premyer Ligasi", "Angliya", "🇬🇧", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/47.png", "Premyer-liga", 2),
        (87, "La Liga", "Ispaniya La Ligasi", "Ispaniya", "🇪🇸", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/87.png", "La Liga EA Sports", 3),
        (71, "Turkiya", "Turkiya Super Ligasi", "Turkiya", "🇹🇷", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/71.png", "Legionerlarimiz ligasi", 4),
        (55, "A Seriya", "Italiya A Seriyasi", "Italiya", "🇮🇹", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/55.png", "Serie A", 5),
        (42, "Chempionlar Ligasi", "UEFA Chempionlar Ligasi", "Yevropa", "🇪🇺", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/42.png", "UCL", 6),
        (54, "Bundesliga", "Germaniya Bundesligasi", "Germaniya", "🇩🇪", "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/54.png", "Bundesliga", 7)
    ]

    for l in leagues_data:
        cursor.execute('''
            INSERT INTO leagues (id, name, full_name, country, flag, icon, badge, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', l)

    now_ts = time.time()

    # ==================== 2. O'ZBEKISTON SUPERLIGASI ====================
    # Standings
    uzb_standings = [
        (1001, 101, 1, "Nasaf", "Nasaf", 18, 11, 6, 1, "28-11", 17, 39, "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png"),
        (1001, 102, 2, "Paxtakor", "Paxtakor", 18, 10, 5, 3, "34-18", 16, 35, "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png"),
        (1001, 103, 3, "Navbahor", "Navbahor", 18, 9, 6, 3, "29-16", 13, 33, "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png"),
        (1001, 104, 4, "OKMK", "OKMK", 18, 9, 5, 4, "27-20", 7, 32, "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png"),
        (1001, 105, 5, "So'g'diyona", "So'g'diyona", 18, 8, 6, 4, "26-19", 7, 30, "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png"),
        (1001, 106, 6, "Neftchi", "Neftchi", 18, 7, 7, 4, "22-17", 5, 28, "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png"),
        (1001, 107, 7, "Andijon", "Andijon", 18, 6, 7, 5, "25-22", 3, 25, "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png"),
        (1001, 108, 8, "Dinamo Samarqand", "Dinamo", 18, 6, 5, 7, "23-24", -1, 23, "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png"),
        (1001, 109, 9, "Bunyodkor", "Bunyodkor", 18, 4, 7, 7, "18-26", -8, 19, "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png"),
        (1001, 110, 10, "Qizilqum", "Qizilqum", 18, 4, 6, 8, "17-25", -8, 18, "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png"),
        (1001, 111, 11, "Surxon", "Surxon", 18, 4, 5, 9, "16-27", -11, 17, "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png"),
        (1001, 112, 12, "Lokomotiv Toshkent", "Lokomotiv", 18, 3, 6, 9, "19-30", -11, 15, "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png"),
        (1001, 113, 13, "Metallurg Bekobod", "Metallurg", 18, 2, 8, 8, "15-26", -11, 14, "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png"),
        (1001, 114, 14, "Olimpik Toshkent", "Olimpik", 18, 2, 5, 11, "13-31", -18, 11, "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png")
    ]

    for s in uzb_standings:
        cursor.execute('''
            INSERT INTO standings (league_id, team_id, rank, name, short_name, played, wins, draws, losses, scores_str, goal_diff, points, badge, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # Matches for Uzbekistan Super League (1-tur completed, 2-tur upcoming)
    uzb_matches = [
        # 1-tur
        ("uzb_1_1", 1001, 1, "1-tur", 101, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", 107, "Andijon", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "2 : 1", "2", "1", 0, 1, None, "2026-08-21T14:30:00Z", "21.08.2026", "19:30", "21-Aug", 1787322600, "Markaziy Stadion, Qarshi", "Ilgyz Tantashev", json.dumps([
            {"type": "goal", "minute": 24, "player": "Zoran Marusic", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 62, "player": "Akmal Mozgovoy", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 81, "player": "Rustam Turdimurodov", "team": "away", "detail": "Gol (Bosh bilan)"},
            {"type": "card", "minute": 44, "player": "Sherzod Nasrullayev", "team": "home", "card": "yellow"},
            {"type": "card", "minute": 76, "player": "Farhod Sohibjonov", "team": "away", "card": "yellow"}
        ])),
        ("uzb_1_2", 1001, 1, "1-tur", 102, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 103, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "1 : 1", "1", "1", 0, 1, None, "2026-08-22T14:30:00Z", "22.08.2026", "19:30", "22-Aug", 1787409000, "Paxtakor Markaziy Stadioni, Toshkent", "Ravshan Ermatov", json.dumps([
            {"type": "goal", "minute": 38, "player": "Dragan Ceran", "team": "home", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 74, "player": "Toma Tabatadze", "team": "away", "detail": "Gol"},
            {"type": "card", "minute": 55, "player": "Jamshid Iskanderov", "team": "away", "card": "yellow"}
        ])),
        ("uzb_1_3", 1001, 1, "1-tur", 104, "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", 106, "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "1 : 0", "1", "0", 0, 1, None, "2026-08-23T14:00:00Z", "23.08.2026", "19:00", "23-Aug", 1787493600, "OKMK Sport Majmuasi, Olmaliq", "Ahrol Risqullayev", json.dumps([
            {"type": "goal", "minute": 51, "player": "Khurshid Giyosov", "team": "home", "detail": "Gol"},
            {"type": "card", "minute": 88, "player": "Abror Ismoilov", "team": "away", "card": "yellow"}
        ])),
        ("uzb_1_4", 1001, 1, "1-tur", 105, "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", 109, "Bunyodkor", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "3 : 0", "3", "0", 0, 1, None, "2026-08-24T14:00:00Z", "24.08.2026", "19:00", "24-Aug", 1787580000, "So'g'diyona Stadioni, Jizzax", "Firdavs Norsafarov", json.dumps([
            {"type": "goal", "minute": 15, "player": "Ljupcho Doriyev", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 42, "player": "Ljupcho Doriyev", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 69, "player": "Xondamir Mustafoqulov", "team": "home", "detail": "Gol"}
        ])),

        # 2-tur (Navbatdagi o'yinlar)
        ("uzb_2_1", 1001, 2, "2-tur", 103, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", 101, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", None, None, None, 0, 0, None, "2026-08-28T14:30:00Z", "28.08.2026", "19:30", "28-Aug", 1787927400, "Markaziy Stadion, Namangan", "Ilgyz Tantashev", json.dumps([])),
        ("uzb_2_2", 1001, 2, "2-tur", 106, "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", 102, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", None, None, None, 0, 0, None, "2026-08-29T14:30:00Z", "29.08.2026", "19:30", "29-Aug", 1788013800, "Istiqlol Stadioni, Farg'ona", "Ravshan Ermatov", json.dumps([])),
        ("uzb_2_3", 1001, 2, "2-tur", 107, "Andijon", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", 104, "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", None, None, None, 0, 0, None, "2026-08-30T14:00:00Z", "30.08.2026", "19:00", "30-Aug", 1788098400, "Bobur Arena, Andijon", "Firdavs Norsafarov", json.dumps([])),
        ("uzb_2_4", 1001, 2, "2-tur", 108, "Dinamo Samarqand", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", 105, "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", None, None, None, 0, 0, None, "2026-08-31T14:00:00Z", "31.08.2026", "19:00", "31-Aug", 1788184800, "Dinamo Stadioni, Samarqand", "Ahrol Risqullayev", json.dumps([]))
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

    # Stats for Uzbekistan Super League
    uzb_stats = [
        (1001, "Dragan Ceran", "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 13, 5, 18, 3),
        (1001, "Khusayin Norchaev", "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 10, 3, 17, 1),
        (1001, "Zoran Marusic", "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", "", 9, 4, 18, 0),
        (1001, "Toma Tabatadze", "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "", 8, 2, 16, 2),
        (1001, "Ljupcho Doriyev", "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", "", 8, 6, 18, 1),
        (1001, "Khurshid Giyosov", "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "", 7, 5, 18, 2),
        (1001, "Jamshid Iskanderov", "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "", 4, 9, 18, 1),
        (1001, "Akmal Mozgovoy", "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", "", 5, 6, 18, 0),
        (1001, "Diyor Kholmatov", "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 3, 7, 17, 0)
    ]
    for s in uzb_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # ==================== 3. APL (2026/2027) ====================
    apl_matches = [
        # 1-tur (Yakunlangan)
        ("apl_1_1", 47, 1, "1-tur", 9825, "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", 8680, "Coventry", "https://images.fotmob.com/image_resources/logo/teamlogo/8680.png", "3 : 0", "3", "0", 0, 1, None, "2026-08-21T19:00:00Z", "22.08.2026", "00:00", "22-Aug", 1787338800, "Emirates Stadium, London", "Michael Oliver", json.dumps([
            {"type": "goal", "minute": 14, "player": "Bukayo Saka", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 52, "player": "Kai Havertz", "team": "home", "detail": "Gol (Bosh bilan)"},
            {"type": "goal", "minute": 84, "player": "Martin Ødegaard", "team": "home", "detail": "Gol (Jarima to'pi)"},
            {"type": "card", "minute": 31, "player": "Ben White", "team": "home", "card": "yellow"}
        ])),
        ("apl_1_2", 47, 1, "1-tur", 10260, "Hull", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", 10260, "Man United", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", "2 : 0", "2", "0", 0, 1, None, "2026-08-22T11:30:00Z", "22.08.2026", "16:30", "22-Aug", 1787398200, "MKM Stadium", "Anthony Taylor", json.dumps([
            {"type": "goal", "minute": 28, "player": "Jaden Philogene", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 77, "player": "Liam Delap", "team": "home", "detail": "Gol"},
            {"type": "card", "minute": 45, "player": "Casemiro", "team": "away", "card": "yellow"},
            {"type": "card", "minute": 62, "player": "Bruno Fernandes", "team": "away", "card": "yellow"}
        ])),
        ("apl_1_3", 47, 1, "1-tur", 10261, "Newcastle", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", 8650, "Liverpool", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "2 : 2", "2", "2", 0, 1, None, "2026-08-23T15:30:00Z", "23.08.2026", "20:30", "23-Aug", 1787499000, "St. James' Park, Newcastle", "Paul Tierney", json.dumps([
            {"type": "goal", "minute": 32, "player": "Alexander Isak", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 41, "player": "Mohamed Salah", "team": "away", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 78, "player": "Darwin Núñez", "team": "away", "detail": "Gol (Bosh bilan)"},
            {"type": "goal", "minute": 88, "player": "Anthony Gordon", "team": "home", "detail": "Gol"},
            {"type": "card", "minute": 54, "player": "Alexis Mac Allister", "team": "away", "card": "yellow"},
            {"type": "card", "minute": 71, "player": "Joelinton", "team": "home", "card": "yellow"}
        ])),
        ("apl_1_4", 47, 1, "1-tur", 9826, "Fulham", "https://images.fotmob.com/image_resources/logo/teamlogo/9826.png", 8455, "Chelsea", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "2 : 3", "2", "3", 0, 1, None, "2026-08-24T19:00:00Z", "25.08.2026", "00:00", "25-Aug", 1787598000, "Craven Cottage, London", "Simon Hooper", json.dumps([
            {"type": "goal", "minute": 18, "player": "Cole Palmer", "team": "away", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 34, "player": "Alex Iwobi", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 59, "player": "Nicolas Jackson", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 73, "player": "Raúl Jiménez", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 86, "player": "Christopher Nkunku", "team": "away", "detail": "Gol"}
        ])),
        ("apl_1_5", 47, 1, "1-tur", 10204, "Brighton", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", 10252, "Aston Villa", "https://images.fotmob.com/image_resources/logo/teamlogo/10252.png", "4 : 0", "4", "0", 0, 1, None, "2026-08-23T13:00:00Z", "23.08.2026", "18:00", "23-Aug", 1787490000, "Amex Stadium", "Andy Madley", json.dumps([
            {"type": "goal", "minute": 12, "player": "Kaoru Mitoma", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 37, "player": "Danny Welbeck", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 64, "player": "Simon Adingra", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 89, "player": "Evan Ferguson", "team": "home", "detail": "Gol"}
        ])),

        # 2-tur (Navbatdagi o'yinlar)
        ("apl_2_1", 47, 2, "2-tur", 8650, "Liverpool", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", 10203, "Nottm Forest", "https://images.fotmob.com/image_resources/logo/teamlogo/10203.png", None, None, None, 0, 0, None, "2026-08-29T11:30:00Z", "29.08.2026", "16:30", "29-Aug", 1788003000, "Anfield Stadium, Liverpool", "Michael Oliver", json.dumps([])),
        ("apl_2_2", 47, 2, "2-tur", 9826, "Crystal Palace", "https://images.fotmob.com/image_resources/logo/teamlogo/9826.png", 8456, "Man City", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", None, None, None, 0, 0, None, "2026-08-28T19:00:00Z", "29.08.2026", "00:00", "29-Aug", 1787943600, "Selhurst Park, London", "Anthony Taylor", json.dumps([])),
        ("apl_2_3", 47, 2, "2-tur", 8586, "Tottenham", "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png", 10261, "Newcastle", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", None, None, None, 0, 0, None, "2026-08-29T16:30:00Z", "29.08.2026", "21:30", "29-Aug", 1788021000, "Tottenham Hotspur Stadium", "Paul Tierney", json.dumps([])),
        ("apl_2_4", 47, 2, "2-tur", 8455, "Chelsea", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", 10204, "Brighton", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", None, None, None, 0, 0, None, "2026-08-30T13:00:00Z", "30.08.2026", "18:00", "30-Aug", 1788094800, "Stamford Bridge, London", "Simon Hooper", json.dumps([])),
        ("apl_2_5", 47, 2, "2-tur", 10260, "Man United", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", 10260, "Ipswich", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", None, None, None, 0, 0, None, "2026-08-30T15:30:00Z", "30.08.2026", "20:30", "30-Aug", 1788103800, "Old Trafford, Manchester", "Andy Madley", json.dumps([])),
        ("apl_2_6", 47, 2, "2-tur", 10252, "Aston Villa", "https://images.fotmob.com/image_resources/logo/teamlogo/10252.png", 9825, "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", None, None, None, 0, 0, None, "2026-08-31T19:00:00Z", "01.09.2026", "00:00", "01-Sep", 1788202800, "Villa Park, Birmingham", "Michael Oliver", json.dumps([]))
    ]

    for m in apl_matches:
        cursor.execute('''
            INSERT INTO matches (
                id, league_id, round_num, round_name, home_id, home_name, home_badge,
                away_id, away_name, away_badge, score_str, home_score, away_score,
                is_live, is_finished, live_time, utc_time, tashkent_date, tashkent_time,
                tashkent_display, tashkent_timestamp, stadium, referee, events_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*m, now_ts))

    # APL Stats
    apl_stats = [
        (47, "Bukayo Saka", "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "", 2, 1, 1, 0),
        (47, "Erling Haaland", "Man City", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 2, 0, 1, 0),
        (47, "Mohamed Salah", "Liverpool", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 1, 1, 1, 1),
        (47, "Cole Palmer", "Chelsea", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "", 1, 1, 1, 1),
        (47, "Alexander Isak", "Newcastle", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", "", 1, 0, 1, 0),
        (47, "Kai Havertz", "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "", 1, 0, 1, 0),
        (47, "Martin Ødegaard", "Arsenal", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "", 1, 2, 1, 0),
        (47, "Kevin De Bruyne", "Man City", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 0, 2, 1, 0),
        (47, "Trent Alexander-Arnold", "Liverpool", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 0, 1, 1, 0)
    ]
    for s in apl_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # ==================== 4. LA LIGA (2026/2027) ====================
    laliga_matches = [
        # 1-tur
        ("laliga_1_1", 87, 1, "1-tur", 8633, "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", 8560, "Espanyol", "https://images.fotmob.com/image_resources/logo/teamlogo/8560.png", "2 : 1", "2", "1", 0, 1, None, "2026-08-22T19:30:00Z", "23.08.2026", "00:30", "23-Aug", 1787427000, "Santiago Bernabéu, Madrid", "Gil Manzano", json.dumps([
            {"type": "goal", "minute": 23, "player": "Kylian Mbappé", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 67, "player": "Vinicius Junior", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 82, "player": "Javi Puado", "team": "away", "detail": "Gol"}
        ])),
        ("laliga_1_2", 87, 1, "1-tur", 8634, "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", 8581, "Elche", "https://images.fotmob.com/image_resources/logo/teamlogo/8581.png", "5 : 0", "5", "0", 0, 1, None, "2026-08-23T19:30:00Z", "24.08.2026", "00:30", "24-Aug", 1787513400, "Camp Nou, Barcelona", "Sánchez Martínez", json.dumps([
            {"type": "goal", "minute": 11, "player": "Robert Lewandowski", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 34, "player": "Lamine Yamal", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 49, "player": "Raphinha", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 72, "player": "Robert Lewandowski", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 88, "player": "Dani Olmo", "team": "home", "detail": "Gol"}
        ])),
        ("laliga_1_3", 87, 1, "1-tur", 9906, "Atletico Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/9906.png", 10205, "Villarreal", "https://images.fotmob.com/image_resources/logo/teamlogo/10205.png", "2 : 2", "2", "2", 0, 1, None, "2026-08-23T15:00:00Z", "23.08.2026", "20:00", "23-Aug", 1787497200, "Cívitas Metropolitano, Madrid", "Hernández Hernández", json.dumps([
            {"type": "goal", "minute": 19, "player": "Julián Álvarez", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 44, "player": "Gerard Moreno", "team": "away", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 68, "player": "Alexander Sørloth", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 85, "player": "Álex Baena", "team": "away", "detail": "Gol"}
        ])),

        # 2-tur (Navbatdagi o'yinlar)
        ("laliga_2_1", 87, 2, "2-tur", 8633, "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", 8560, "Málaga", "https://images.fotmob.com/image_resources/logo/teamlogo/8560.png", None, None, None, 0, 0, None, "2026-08-30T15:00:00Z", "30.08.2026", "20:00", "30-Aug", 1788102000, "Santiago Bernabéu, Madrid", "Gil Manzano", json.dumps([])),
        ("laliga_2_2", 87, 2, "2-tur", 8634, "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", 8581, "Athletic Club", "https://images.fotmob.com/image_resources/logo/teamlogo/8581.png", None, None, None, 0, 0, None, "2026-08-30T19:30:00Z", "31.08.2026", "00:30", "31-Aug", 1788118200, "Camp Nou, Barcelona", "Sánchez Martínez", json.dumps([]))
    ]

    for m in laliga_matches:
        cursor.execute('''
            INSERT INTO matches (
                id, league_id, round_num, round_name, home_id, home_name, home_badge,
                away_id, away_name, away_badge, score_str, home_score, away_score,
                is_live, is_finished, live_time, utc_time, tashkent_date, tashkent_time,
                tashkent_display, tashkent_timestamp, stadium, referee, events_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*m, now_ts))

    # La Liga Stats
    laliga_stats = [
        (87, "Robert Lewandowski", "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", "", 2, 0, 1, 0),
        (87, "Lamine Yamal", "Barcelona", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", "", 1, 2, 1, 0),
        (87, "Kylian Mbappé", "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", "", 1, 0, 1, 0),
        (87, "Vinicius Junior", "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", "", 1, 1, 1, 0),
        (87, "Julián Álvarez", "Atletico Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/9906.png", "", 1, 0, 1, 0),
        (87, "Jude Bellingham", "Real Madrid", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", "", 0, 1, 1, 0)
    ]
    for s in laliga_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    # ==================== 5. TURKIYA SUPERLIGASI (2026/2027) ====================
    turkey_matches = [
        # 1-tur
        ("tur_1_1", 71, 1, "1-tur", 9752, "Rizespor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", 8560, "Gaziantep FK", "https://images.fotmob.com/image_resources/logo/teamlogo/8560.png", "1 : 0", "1", "0", 0, 1, None, "2026-08-23T16:00:00Z", "23.08.2026", "21:00", "23-Aug", 1787500800, "Çaykur Didi Stadyumu, Rize", "Halil Umut Meler", json.dumps([
            {"type": "goal", "minute": 73, "player": "Husniddin Aliqulov 🇺🇿", "team": "home", "detail": "Gol (Bosh bilan, Burchakdan)"},
            {"type": "card", "minute": 42, "player": "Husniddin Aliqulov 🇺🇿", "team": "home", "card": "yellow"}
        ])),
        ("tur_1_2", 71, 1, "1-tur", 8686, "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 8633, "Göztepe", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", "3 : 1", "3", "1", 0, 1, None, "2026-08-24T18:30:00Z", "24.08.2026", "23:30", "24-Aug", 1787596200, "Rams Park, Istanbul", "Cüneyt Çakır", json.dumps([
            {"type": "goal", "minute": 16, "player": "Mauro Icardi", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 54, "player": "Barış Alper Yılmaz", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 88, "player": "Dries Mertens", "team": "home", "detail": "Gol"}
        ])),
        # 2-tur (Navbatdagi)
        ("tur_2_1", 71, 2, "2-tur", 8686, "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 9752, "Rizespor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", None, None, None, 0, 0, None, "2026-08-29T18:30:00Z", "29.08.2026", "23:30", "29-Aug", 1788028200, "Rams Park, Istanbul", "Halil Umut Meler", json.dumps([]))
    ]

    for m in turkey_matches:
        cursor.execute('''
            INSERT INTO matches (
                id, league_id, round_num, round_name, home_id, home_name, home_badge,
                away_id, away_name, away_badge, score_str, home_score, away_score,
                is_live, is_finished, live_time, utc_time, tashkent_date, tashkent_time,
                tashkent_display, tashkent_timestamp, stadium, referee, events_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*m, now_ts))

    # Turkey Stats
    tur_stats = [
        (71, "Mauro Icardi", "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 1, 1, 0),
        (71, "Husniddin Aliqulov 🇺🇿", "Rizespor", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "", 1, 0, 1, 0),
        (71, "Barış Alper Yılmaz", "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 0, 1, 0),
        (71, "Dries Mertens", "Galatasaray", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 1, 1, 1, 0)
    ]
    for s in tur_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    conn.commit()
    conn.close()
    print("🌟 Barcha ligalar (O'zbekiston Superligasi, APL, La Liga, Turkiya) muvaffaqiyatli saqlandi!")

if __name__ == '__main__':
    seed_database()

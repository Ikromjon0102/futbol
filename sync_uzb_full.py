import sqlite3
import json
import time
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = 'futbol.db'

def sync_uzbekistan_full():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_ts = time.time()

    # 1. Update Uzbekistan Standings with EXACT 16 teams and 19 games played
    cursor.execute('DELETE FROM standings WHERE league_id = 1001')

    uzb_standings = [
        (1, "Neftchi Fergana", "Neftchi", 19, 14, 3, 2, "45-10", 35, 45, "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png"),
        (2, "Paxtakor", "Paxtakor", 19, 11, 7, 1, "31-18", 13, 40, "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png"),
        (3, "Navbahor", "Navbahor", 19, 11, 4, 4, "31-17", 14, 37, "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png"),
        (4, "Buxoro", "Buxoro", 19, 10, 4, 5, "28-20", 8, 34, "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png"),
        (5, "Lokomotiv Tashkent", "Lokomotiv", 19, 9, 4, 6, "32-26", 6, 31, "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png"),
        (6, "AGMK (OKMK)", "OKMK", 19, 8, 5, 6, "27-25", 2, 29, "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png"),
        (7, "Andijan", "Andijon", 19, 8, 3, 8, "24-20", 4, 27, "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png"),
        (8, "Dinamo Samarqand", "Dinamo", 19, 7, 5, 7, "29-30", -1, 26, "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png"),
        (9, "Nasaf", "Nasaf", 19, 6, 7, 6, "20-18", 2, 25, "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png"),
        (10, "Sogdiana", "So'g'diyona", 19, 7, 3, 9, "32-39", -7, 24, "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png"),
        (11, "Qizilqum", "Qizilqum", 19, 7, 2, 10, "17-26", -9, 23, "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png"),
        (12, "Xorazm", "Xorazm", 19, 5, 5, 9, "17-28", -11, 20, "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png"),
        (13, "Surkhon", "Surxon", 19, 5, 5, 9, "16-26", -10, 20, "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png"),
        (14, "Kokand 1912", "Qo'qon 1912", 19, 4, 7, 8, "17-26", -9, 19, "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png"),
        (15, "Bunyodkor", "Bunyodkor", 19, 6, 1, 12, "20-31", -11, 19, "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png"),
        (16, "Mash'al", "Mash'al", 19, 1, 1, 17, "8-34", -26, 4, "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png")
    ]

    for rank, name, sname, mp, w, d, l, scores, gd, pts, badge in uzb_standings:
        team_id = 1000 + rank
        cursor.execute('''
            INSERT INTO standings (
                league_id, team_id, rank, name, short_name, played, wins, draws, losses, scores_str, goal_diff, points, badge, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1001, team_id, rank, name, sname, mp, w, d, l, scores, gd, pts, badge, now_ts))

    # 2. Update Uzbekistan 19-tur Matches (ALL 8 MATCHES FULLY COMPLETED)
    cursor.execute('DELETE FROM matches WHERE league_id = 1001 AND round_num = 19')

    uzb_19_matches = [
        # Mash'al 0 : 2 Navbahor
        ("uzb_19_mashal_navbahor", 1001, 19, "19-tur", 1016, "Mash'al", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", 1003, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "0 : 2", "0", "2", 0, 1, None, "2026-08-26T14:00:00Z", "26.08.2026", "19:00", "Kecha", 1787752800, "Bahrom Vafoyev Stadioni, Muborak", "Asker Najafaliyev", json.dumps([
            {"type": "goal", "minute": 28, "player": "Toma Tabatadze", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 74, "player": "Jamshid Iskanderov", "team": "away", "detail": "Gol (Jarimadan)"},
            {"type": "card", "minute": 41, "player": "Ibrohim G'anixonov", "team": "home", "card": "yellow"},
            {"type": "card", "minute": 62, "player": "Filip Ivanovic", "team": "away", "card": "yellow"}
        ])),
        # Lokomotiv 4 : 1 Bunyodkor
        ("uzb_19_loko_bunyodkor", 1001, 19, "19-tur", 1005, "Lokomotiv", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", 1015, "Bunyodkor", "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png", "4 : 1", "4", "1", 0, 1, None, "2026-08-26T14:00:00Z", "26.08.2026", "19:00", "Kecha", 1787752800, "Lokomotiv Stadioni, Toshkent", "Ahrol Risqullayev", json.dumps([
            {"type": "goal", "minute": 14, "player": "Temur Mamasidiqov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 42, "player": "Sanjar Shaaxmedov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 52, "player": "Mirjahon Mirahmadov", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 68, "player": "Shodiyor Shodiboev", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 85, "player": "Jasur Hakimov", "team": "home", "detail": "Gol"}
        ])),
        # Qizilqum 1 : 0 Nasaf
        ("uzb_19_qizilqum_nasaf", 1001, 19, "19-tur", 1011, "Qizilqum", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", 1009, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", "1 : 0", "1", "0", 0, 1, None, "2026-08-26T15:00:00Z", "26.08.2026", "20:00", "Kecha", 1787756400, "Yoshlar SM, Navoiy", "Ilgyz Tantashev", json.dumps([
            {"type": "goal", "minute": 61, "player": "Asror G'ofurov", "team": "home", "detail": "Gol"},
            {"type": "card", "minute": 77, "player": "Oybek Bozorov", "team": "away", "card": "yellow"}
        ])),
        # Paxtakor 2 : 1 Andijon
        ("uzb_19_paxtakor_andijon", 1001, 19, "19-tur", 1002, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 1007, "Andijon", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "2 : 1", "2", "1", 0, 1, None, "2026-08-22T14:30:00Z", "22.08.2026", "19:30", "22-Aug", 1787409000, "Paxtakor Markaziy Stadioni", "Ravshan Ermatov", json.dumps([
            {"type": "goal", "minute": 22, "player": "Dragan Ceran", "team": "home", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 54, "player": "Rustam Turdimurodov", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 88, "player": "Diyor Kholmatov", "team": "home", "detail": "Gol"}
        ])),
        # Buxoro 1 : 0 Dinamo Samarqand
        ("uzb_19_buxoro_dinamo", 1001, 19, "19-tur", 1004, "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", 1008, "Dinamo", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "1 : 0", "1", "0", 0, 1, None, "2026-08-23T14:00:00Z", "23.08.2026", "19:00", "23-Aug", 1787493600, "Buxoro Arena", "Ahrol Risqullayev", json.dumps([
            {"type": "goal", "minute": 64, "player": "Jasur Khasanov", "team": "home", "detail": "Gol"}
        ])),
        # OKMK 2 : 2 So'g'diyona
        ("uzb_19_okmk_sogdiana", 1001, 19, "19-tur", 1006, "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", 1010, "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "2 : 2", "2", "2", 0, 1, None, "2026-08-24T14:00:00Z", "24.08.2026", "19:00", "24-Aug", 1787580000, "OKMK Majmuasi, Olmaliq", "Firdavs Norsafarov", json.dumps([
            {"type": "goal", "minute": 12, "player": "Khurshid Giyosov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 39, "player": "Ljupcho Doriyev", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 61, "player": "Ljupcho Doriyev", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 83, "player": "Ruben Sanchez", "team": "home", "detail": "Gol"}
        ])),
        # Neftchi 3 : 0 Xorazm
        ("uzb_19_neftchi_xorazm", 1001, 19, "19-tur", 1001, "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", 1012, "Xorazm", "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png", "3 : 0", "3", "0", 0, 1, None, "2026-08-21T14:30:00Z", "21.08.2026", "19:30", "21-Aug", 1787322600, "Istiqlol Stadioni, Farg'ona", "Ilgyz Tantashev", json.dumps([
            {"type": "goal", "minute": 18, "player": "Khusayin Norchaev", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 45, "player": "Khusayin Norchaev", "team": "home", "detail": "Gol (Bosh bilan)"},
            {"type": "goal", "minute": 72, "player": "Bilolxon Toshmirzayev", "team": "home", "detail": "Gol"}
        ])),
        # Surxon 1 : 1 Qo'qon 1912
        ("uzb_19_surxon_kokand", 1001, 19, "19-tur", 1013, "Surxon", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", 1014, "Qo'qon 1912", "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png", "1 : 1", "1", "1", 0, 1, None, "2026-08-22T14:00:00Z", "22.08.2026", "19:00", "22-Aug", 1787407200, "Surxon Stadioni, Termiz", "Rustam Lutfullin", json.dumps([
            {"type": "goal", "minute": 33, "player": "Abdug'afur Haydarov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 76, "player": "Anvarjon Hojimirzayev", "team": "away", "detail": "Gol"}
        ]))
    ]

    for m in uzb_19_matches:
        cursor.execute('''
            INSERT OR REPLACE INTO matches (
                id, league_id, round_num, round_name, home_id, home_name, home_badge,
                away_id, away_name, away_badge, score_str, home_score, away_score,
                is_live, is_finished, live_time, utc_time, tashkent_date, tashkent_time,
                tashkent_display, tashkent_timestamp, stadium, referee, events_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*m, now_ts))

    # 3. Update Scorers (To'purarlar)
    cursor.execute('DELETE FROM player_stats WHERE league_id = 1001')
    uzb_stats = [
        (1001, "Khusayin Norchaev", "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", "", 15, 4, 19, 2),
        (1001, "Dragan Ceran", "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", "", 14, 6, 19, 4),
        (1001, "Toma Tabatadze", "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "", 11, 3, 19, 3),
        (1001, "Ljupcho Doriyev", "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "", 11, 7, 19, 2),
        (1001, "Zoran Marusic", "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", "", 9, 4, 19, 0),
        (1001, "Jasur Khasanov", "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", "", 8, 5, 19, 1),
        (1001, "Rustam Turdimurodov", "Andijon", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "", 8, 3, 19, 0),
        (1001, "Khurshid Giyosov", "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", "", 7, 6, 19, 2),
        (1001, "Jamshid Iskanderov", "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "", 6, 11, 19, 1)
    ]

    for s in uzb_stats:
        cursor.execute('''
            INSERT INTO player_stats (league_id, player_name, team_name, team_badge, photo, goals, assists, matches, penalties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*s, now_ts))

    conn.commit()
    conn.close()
    print("🇺🇿 O'zbekiston Superligasi 19-tur yakuniy to'liq natijalari (Navbahor 2:0, Lokomotiv 4:1, Qizilqum 1:0) saqlandi!")

if __name__ == '__main__':
    sync_uzbekistan_full()

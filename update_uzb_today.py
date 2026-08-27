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

DB_PATH = 'futbol.db'

def update_uzb_live_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_ts = time.time()

    # Clear 19-tur and 20-tur for Uzbekistan
    cursor.execute('DELETE FROM matches WHERE league_id = 1001')

    uzb_matches = [
        # ==================== 19-TUR (BUGUNGI VA YAKUNLANGAN O'YINLAR) ====================
        # 1. Mash'al vs Navbahor (Bugun 26.08.2026 - LIVE)
        ("uzb_19_mashal_navbahor", 1001, 19, "19-tur", 1016, "Mash'al", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", 1004, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", "0 : 0", "0", "0", 1, 0, "1'", "2026-08-26T14:00:00Z", "26.08.2026", "19:00", "Bugun (LIVE)", 1787752800, "Bahrom Vafoyev Stadioni, Muborak", "Asker Najafaliyev", json.dumps([])),
        
        # 2. Lokomotiv vs Bunyodkor (Bugun 26.08.2026 - 19:00)
        ("uzb_19_loko_bunyodkor", 1001, 19, "19-tur", 1006, "Lokomotiv", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", 1015, "Bunyodkor", "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png", None, None, None, 0, 0, None, "2026-08-26T14:00:00Z", "26.08.2026", "19:00", "Bugun 19:00", 1787752800, "Lokomotiv Stadioni, Toshkent", "Ahrol Risqullayev", json.dumps([])),
        
        # 3. Qizilqum vs Nasaf (Bugun 26.08.2026 - 20:00)
        ("uzb_19_qizilqum_nasaf", 1001, 19, "19-tur", 1011, "Qizilqum", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", 1009, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", None, None, None, 0, 0, None, "2026-08-26T15:00:00Z", "26.08.2026", "20:00", "Bugun 20:00", 1787756400, "Yoshlar SM, Navoiy", "Ilgyz Tantashev", json.dumps([])),

        # 4. Paxtakor vs Andijon (Yakunlangan)
        ("uzb_19_paxtakor_andijon", 1001, 19, "19-tur", 1002, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 1007, "Andijon", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", "2 : 1", "2", "1", 0, 1, None, "2026-08-22T14:30:00Z", "22.08.2026", "19:30", "22-Aug", 1787409000, "Paxtakor Markaziy Stadioni", "Ravshan Ermatov", json.dumps([
            {"type": "goal", "minute": 22, "player": "Dragan Ceran", "team": "home", "detail": "Gol (Penalti)"},
            {"type": "goal", "minute": 54, "player": "Rustam Turdimurodov", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 88, "player": "Diyor Kholmatov", "team": "home", "detail": "Gol"}
        ])),

        # 5. Buxoro vs Dinamo Samarqand (Yakunlangan)
        ("uzb_19_buxoro_dinamo", 1001, 19, "19-tur", 1003, "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", 1008, "Dinamo", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", "1 : 0", "1", "0", 0, 1, None, "2026-08-23T14:00:00Z", "23.08.2026", "19:00", "23-Aug", 1787493600, "Buxoro Arena", "Ahrol Risqullayev", json.dumps([
            {"type": "goal", "minute": 64, "player": "Jasur Khasanov", "team": "home", "detail": "Gol"}
        ])),

        # 6. OKMK vs So'g'diyona (Yakunlangan)
        ("uzb_19_okmk_sogdiana", 1001, 19, "19-tur", 1005, "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", 1010, "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", "2 : 2", "2", "2", 0, 1, None, "2026-08-24T14:00:00Z", "24.08.2026", "19:00", "24-Aug", 1787580000, "OKMK Majmuasi, Olmaliq", "Firdavs Norsafarov", json.dumps([
            {"type": "goal", "minute": 12, "player": "Khurshid Giyosov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 39, "player": "Ljupcho Doriyev", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 61, "player": "Ljupcho Doriyev", "team": "away", "detail": "Gol"},
            {"type": "goal", "minute": 83, "player": "Ruben Sanchez", "team": "home", "detail": "Gol"}
        ])),

        # 7. Neftchi vs Xorazm (Yakunlangan)
        ("uzb_19_neftchi_xorazm", 1001, 19, "19-tur", 1001, "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", 1012, "Xorazm", "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png", "3 : 0", "3", "0", 0, 1, None, "2026-08-21T14:30:00Z", "21.08.2026", "19:30", "21-Aug", 1787322600, "Istiqlol Stadioni, Farg'ona", "Ilgyz Tantashev", json.dumps([
            {"type": "goal", "minute": 18, "player": "Khusayin Norchaev", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 45, "player": "Khusayin Norchaev", "team": "home", "detail": "Gol (Bosh bilan)"},
            {"type": "goal", "minute": 72, "player": "Bilolxon Toshmirzayev", "team": "home", "detail": "Gol"}
        ])),

        # 8. Surxon vs Qo'qon 1912 (Yakunlangan)
        ("uzb_19_surxon_kokand", 1001, 19, "19-tur", 1013, "Surxon", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", 1014, "Qo'qon 1912", "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png", "1 : 1", "1", "1", 0, 1, None, "2026-08-22T14:00:00Z", "22.08.2026", "19:00", "22-Aug", 1787407200, "Surxon Stadioni, Termiz", "Rustam Lutfullin", json.dumps([
            {"type": "goal", "minute": 33, "player": "Abdug'afur Haydarov", "team": "home", "detail": "Gol"},
            {"type": "goal", "minute": 76, "player": "Anvarjon Hojimirzayev", "team": "away", "detail": "Gol"}
        ])),

        # ==================== 20-TUR (DAM OLISH KUNLARI) ====================
        ("uzb_20_paxtakor_neftchi", 1001, 20, "20-tur", 1002, "Paxtakor", "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png", 1001, "Neftchi", "https://images.fotmob.com/image_resources/logo/teamlogo/8456.png", None, None, None, 0, 0, None, "2026-08-29T14:30:00Z", "29.08.2026", "19:30", "29-Aug", 1788013800, "Paxtakor Markaziy Stadioni (Katta Derbi 🔥)", "Ravshan Ermatov", json.dumps([])),
        ("uzb_20_navbahor_buxoro", 1001, 20, "20-tur", 1004, "Navbahor", "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png", 1003, "Buxoro", "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png", None, None, None, 0, 0, None, "2026-08-29T14:00:00Z", "29.08.2026", "19:00", "29-Aug", 1788012000, "Markaziy Stadion, Namangan", "Ilgyz Tantashev", json.dumps([])),
        ("uzb_20_nasaf_okmk", 1001, 20, "20-tur", 1009, "Nasaf", "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png", 1005, "OKMK", "https://images.fotmob.com/image_resources/logo/teamlogo/10204.png", None, None, None, 0, 0, None, "2026-08-30T14:30:00Z", "30.08.2026", "19:30", "30-Aug", 1788100200, "Markaziy Stadion, Qarshi", "Ahrol Risqullayev", json.dumps([])),
        ("uzb_20_andijon_loko", 1001, 20, "20-tur", 1007, "Andijon", "https://images.fotmob.com/image_resources/logo/teamlogo/8650.png", 1006, "Lokomotiv", "https://images.fotmob.com/image_resources/logo/teamlogo/8633.png", None, None, None, 0, 0, None, "2026-08-30T13:00:00Z", "30.08.2026", "18:00", "30-Aug", 1788094800, "Bobur Arena, Andijon", "Firdavs Norsafarov", json.dumps([])),
        ("uzb_20_dinamo_xorazm", 1001, 20, "20-tur", 1008, "Dinamo", "https://images.fotmob.com/image_resources/logo/teamlogo/9825.png", 1012, "Xorazm", "https://images.fotmob.com/image_resources/logo/teamlogo/9847.png", None, None, None, 0, 0, None, "2026-08-30T14:00:00Z", "30.08.2026", "19:00", "30-Aug", 1788098400, "Dinamo Stadioni, Samarqand", "Rustam Lutfullin", json.dumps([])),
        ("uzb_20_sogdiana_kokand", 1001, 20, "20-tur", 1010, "So'g'diyona", "https://images.fotmob.com/image_resources/logo/teamlogo/8455.png", 1014, "Qo'qon 1912", "https://images.fotmob.com/image_resources/logo/teamlogo/9823.png", None, None, None, 0, 0, None, "2026-08-31T14:00:00Z", "31.08.2026", "19:00", "31-Aug", 1788184800, "So'g'diyona Stadioni, Jizzax", "Asker Najafaliyev", json.dumps([])),
        ("uzb_20_bunyodkor_surxon", 1001, 20, "20-tur", 1015, "Bunyodkor", "https://images.fotmob.com/image_resources/logo/teamlogo/8586.png", 1013, "Surxon", "https://images.fotmob.com/image_resources/logo/teamlogo/8634.png", None, None, None, 0, 0, None, "2026-08-31T14:00:00Z", "31.08.2026", "19:00", "31-Aug", 1788184800, "Bunyodkor Stadioni, Toshkent", "Vadim Agishev", json.dumps([])),
        ("uzb_20_qizilqum_mashal", 1001, 20, "20-tur", 1011, "Qizilqum", "https://images.fotmob.com/image_resources/logo/teamlogo/10260.png", 1016, "Mash'al", "https://images.fotmob.com/image_resources/logo/teamlogo/10261.png", None, None, None, 0, 0, None, "2026-08-31T13:30:00Z", "31.08.2026", "18:30", "31-Aug", 1788183000, "Yoshlar SM, Navoiy", "G'ayrat Jo'rayev", json.dumps([]))
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

    conn.commit()
    conn.close()
    print("✅ Bugungi (26.08.2026) LIVE va o'yinlar muvaffaqiyatli saqlandi!")

if __name__ == '__main__':
    update_uzb_live_matches()

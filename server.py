import os
import sys
import json
import time
import asyncio
from datetime import datetime
import pytz
import aiohttp
from aiohttp import web
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, PORT, SUPPORTED_LEAGUES, LEGIONER_PLAYERS
from database import (
    init_db, get_leagues_from_db, get_matches_from_db, get_rounds_summary,
    get_standings_from_db, get_player_stats_from_db, get_team_fixtures,
    get_db_connection
)

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

init_db()

# ==================== API HANDLERS ====================

async def handle_get_leagues(request):
    leagues = get_leagues_from_db()
    return web.json_response({
        "status": "success",
        "data": leagues
    })

async def handle_get_rounds(request):
    league_id = int(request.match_info.get('league_id', 1001))
    rounds_info = get_rounds_summary(league_id)
    return web.json_response({
        "status": "success",
        "leagueId": league_id,
        "rounds": rounds_info["rounds"],
        "currentRound": rounds_info["currentRound"]
    })

async def handle_get_matches(request):
    league_id = int(request.match_info.get('league_id', 1001))
    round_param = request.query.get('round')
    round_num = int(round_param) if (round_param and round_param.isdigit()) else None

    if round_num is None:
        rounds_info = get_rounds_summary(league_id)
        round_num = rounds_info["currentRound"]

    matches = get_matches_from_db(league_id, round_num)
    leagues = get_leagues_from_db()
    league_info = next((l for l in leagues if l["id"] == league_id), {"id": league_id, "name": "Liga"})

    return web.json_response({
        "status": "success",
        "league": league_info,
        "round": round_num,
        "data": matches
    })

async def handle_get_standings(request):
    league_id = int(request.match_info.get('league_id', 1001))
    standings = get_standings_from_db(league_id)
    leagues = get_leagues_from_db()
    league_info = next((l for l in leagues if l["id"] == league_id), {"id": league_id, "name": "Liga"})

    return web.json_response({
        "status": "success",
        "league": league_info,
        "data": standings
    })

async def handle_get_stats(request):
    league_id = int(request.match_info.get('league_id', 1001))
    stats = get_player_stats_from_db(league_id)
    return web.json_response({
        "status": "success",
        "leagueId": league_id,
        "data": stats
    })

async def handle_get_legioners(request):
    result = []
    for p in LEGIONER_PLAYERS:
        fixtures = get_team_fixtures(p.get('teamName'))
        result.append({
            **p,
            "lastMatch": fixtures["lastMatch"],
            "nextMatch": fixtures["nextMatch"]
        })

    return web.json_response({
        "status": "success",
        "data": result
    })

async def handle_get_all_upcoming(request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM matches 
        WHERE is_finished = 0 
        ORDER BY tashkent_timestamp ASC
    ''')
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "leagueId": r["league_id"],
            "roundName": r["round_name"],
            "homeTeam": {"id": r["home_id"], "name": r["home_name"], "badge": r["home_badge"]},
            "awayTeam": {"id": r["away_id"], "name": r["away_name"], "badge": r["away_badge"]},
            "tashkentTimestamp": r["tashkent_timestamp"],
            "tashkentDate": r["tashkent_date"],
            "tashkentTime": r["tashkent_time"],
            "tashkentDisplay": r["tashkent_display"]
        })
    return web.json_response({"status": "success", "data": result})

async def handle_index(request):
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    index_path = os.path.join(public_dir, 'index.html')
    return web.FileResponse(index_path)

# ==================== APP INIT ====================

async def on_startup(app):
    app['http_session'] = aiohttp.ClientSession()

async def on_cleanup(app):
    await app['http_session'].close()

def create_app():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # API routes
    app.router.add_get('/api/leagues', handle_get_leagues)
    app.router.add_get('/api/rounds/{league_id}', handle_get_rounds)
    app.router.add_get('/api/matches/{league_id}', handle_get_matches)
    app.router.add_get('/api/standings/{league_id}', handle_get_standings)
    app.router.add_get('/api/stats/{league_id}', handle_get_stats)
    app.router.add_get('/api/upcoming', handle_get_all_upcoming)
    app.router.add_get('/api/legioners', handle_get_legioners)

    # Root route
    app.router.add_get('/', handle_index)

    # Static PWA and UI files
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    if not os.path.exists(public_dir):
        os.makedirs(public_dir, exist_ok=True)
    
    app.router.add_static('/', path=public_dir, show_index=False)
    return app

if __name__ == '__main__':
    print(f"🚀 Futbol Serveri http://localhost:{PORT}")
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=PORT)

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { SUPPORTED_LEAGUES, LEGIONER_PLAYERS } from './leaguesData.js';
import { getStandings, getLeagueMatches, getLiveMatches } from './footballApi.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// 1. Get supported leagues
app.get('/api/leagues', (req, res) => {
  res.json({
    status: 'success',
    data: SUPPORTED_LEAGUES
  });
});

// 2. Get standings for a specific league
app.get('/api/standings/:leagueId', async (req, res) => {
  const { leagueId } = req.params;
  try {
    const standings = await getStandings(leagueId);
    const leagueInfo = SUPPORTED_LEAGUES.find(l => l.id == leagueId) || { id: leagueId, name: 'Liga' };
    res.json({
      status: 'success',
      league: leagueInfo,
      data: standings
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// 3. Get matches for a specific league
app.get('/api/matches/:leagueId', async (req, res) => {
  const { leagueId } = req.params;
  try {
    const matches = await getLeagueMatches(leagueId);
    const leagueInfo = SUPPORTED_LEAGUES.find(l => l.id == leagueId) || { id: leagueId, name: 'Liga' };
    res.json({
      status: 'success',
      league: leagueInfo,
      data: matches
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// 4. Get live matches
app.get('/api/live', async (req, res) => {
  try {
    const liveMatches = await getLiveMatches();
    res.json({
      status: 'success',
      count: liveMatches.length,
      data: liveMatches
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// 5. Get Legioners info (Shomurodov, Fayzullaev, etc.)
app.get('/api/legioners', async (req, res) => {
  try {
    // For each legioner, let's fetch their team's next & recent matches
    const results = await Promise.all(
      LEGIONER_PLAYERS.map(async (player) => {
        let teamMatches = [];
        if (player.leagueId) {
          const allLeagueMatches = await getLeagueMatches(player.leagueId);
          teamMatches = allLeagueMatches.filter(
            m => m.homeTeam?.id === player.teamId || 
                 m.awayTeam?.id === player.teamId ||
                 (m.homeTeam?.name && m.homeTeam.name.toLowerCase().includes(player.teamName.toLowerCase())) ||
                 (m.awayTeam?.name && m.awayTeam.name.toLowerCase().includes(player.teamName.toLowerCase()))
          );
        }

        // Find latest completed and upcoming match
        const completed = teamMatches.filter(m => m.status.finished).slice(-1)[0] || null;
        const upcoming = teamMatches.filter(m => !m.status.finished)[0] || null;

        return {
          ...player,
          lastMatch: completed,
          nextMatch: upcoming
        };
      })
    );

    res.json({
      status: 'success',
      data: results
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`⚽ Futbol API Serveri http://localhost:${PORT} portida ishga tushdi`);
});

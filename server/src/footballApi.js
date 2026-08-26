import https from 'https';
import NodeCache from 'node-cache';
import dotenv from 'dotenv';

dotenv.config();

const cache = new NodeCache({ stdTTL: 300, checkperiod: 60 });

const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY || "122ec983ecmshc311b9bfd74e54ap125147jsn64f37f88a8dd";
const RAPIDAPI_HOST = process.env.RAPIDAPI_HOST || "free-api-live-football-data.p.rapidapi.com";

function fetchFromRapidApi(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: RAPIDAPI_HOST,
      path: path,
      method: 'GET',
      headers: {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch (e) {
          reject(new Error(`JSON parse xatoligi: ${e.message}`));
        }
      });
    });

    req.on('error', (e) => {
      reject(e);
    });

    req.setTimeout(12000, () => {
      req.destroy();
      reject(new Error('RapidAPI so\'rov vaqti tugadi (Timeout)'));
    });

    req.end();
  });
}

/**
 * Format date/time to Tashkent time (UTC+5)
 */
export function formatToTashkentTime(utcDateStr) {
  if (!utcDateStr) return { date: '', time: '', text: '' };
  try {
    const dateObj = new Date(utcDateStr);
    if (isNaN(dateObj.getTime())) return { date: '', time: '', text: '' };

    // Tashkent is UTC+5
    const options = { timeZone: 'Asia/Tashkent', hour12: false };
    const hours = new Intl.DateTimeFormat('uz-UZ', { ...options, hour: '2-digit' }).format(dateObj);
    const minutes = new Intl.DateTimeFormat('uz-UZ', { ...options, minute: '2-digit' }).format(dateObj);
    const day = new Intl.DateTimeFormat('uz-UZ', { ...options, day: '2-digit' }).format(dateObj);
    const month = new Intl.DateTimeFormat('uz-UZ', { ...options, month: '2-digit' }).format(dateObj);
    const timeStr = `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`;
    const dateStr = `${day}.${month}`;

    return {
      date: dateStr,
      time: timeStr,
      fullTime: `${dateStr} ${timeStr}`,
      iso: dateObj.toISOString()
    };
  } catch (e) {
    return { date: '', time: '', text: '' };
  }
}

/**
 * Get standings for a league
 */
export async function getStandings(leagueId) {
  const cacheKey = `standings_${leagueId}`;
  const cached = cache.get(cacheKey);
  if (cached) return cached;

  try {
    const data = await fetchFromRapidApi(`/football-get-standing-all?leagueid=${leagueId}`);
    const standingsList = data?.response?.standing || [];
    
    // Normalise standings
    const formatted = standingsList.map((team, idx) => ({
      rank: team.rank || team.idx || (idx + 1),
      id: team.id,
      name: team.name,
      shortName: team.shortName || team.name,
      played: team.played ?? team.matches ?? 0,
      wins: team.wins ?? team.win ?? 0,
      draws: team.draws ?? team.draw ?? 0,
      losses: team.losses ?? team.loss ?? 0,
      scoresStr: team.scoresStr || `${team.goalConDiff || 0}`,
      goalDiff: team.goalConDiff ?? (team.goalsFor - team.goalsAgainst) ?? 0,
      points: team.pts ?? team.points ?? 0,
      badge: `https://images.fotmob.com/image_resources/logo/teamlogo/${team.id}.png`
    }));

    cache.set(cacheKey, formatted, 900); // 15 mins cache
    return formatted;
  } catch (error) {
    console.error(`Standings xatoligi (liga ${leagueId}):`, error.message);
    return [];
  }
}

/**
 * Get all matches / fixtures for a league
 */
export async function getLeagueMatches(leagueId) {
  const cacheKey = `matches_${leagueId}`;
  const cached = cache.get(cacheKey);
  if (cached) return cached;

  try {
    const data = await fetchFromRapidApi(`/football-get-all-matches-by-league?leagueid=${leagueId}`);
    const matchesList = data?.response?.matches || [];

    const formatted = matchesList.map((m) => {
      const timeInfo = formatToTashkentTime(m.status?.utcTime || m.time || m.status?.startDate);
      const isFinished = m.status?.finished === true || m.status?.cancelled === true || m.status?.scoreStr;
      const isLive = m.status?.started === true && !m.status?.finished;

      return {
        id: m.id,
        round: m.round || m.roundName || '',
        homeTeam: {
          id: m.home?.id,
          name: m.home?.name || m.home?.shortName || 'Mezbon',
          score: m.home?.score ?? (m.status?.scoreStr ? m.status.scoreStr.split('-')[0]?.trim() : null),
          badge: `https://images.fotmob.com/image_resources/logo/teamlogo/${m.home?.id}.png`
        },
        awayTeam: {
          id: m.away?.id,
          name: m.away?.name || m.away?.shortName || 'Mehmon',
          score: m.away?.score ?? (m.status?.scoreStr ? m.status.scoreStr.split('-')[1]?.trim() : null),
          badge: `https://images.fotmob.com/image_resources/logo/teamlogo/${m.away?.id}.png`
        },
        status: {
          live: isLive,
          finished: isFinished,
          scoreStr: m.status?.scoreStr || (isLive ? `${m.home?.score ?? 0} - ${m.away?.score ?? 0}` : null),
          liveTime: m.status?.liveTime?.short || (isLive ? 'LIVE' : null),
          cancelled: m.status?.cancelled || false
        },
        tashkentTime: timeInfo.time,
        tashkentDate: timeInfo.date,
        rawUtc: m.status?.utcTime || m.time
      };
    });

    cache.set(cacheKey, formatted, 300); // 5 mins cache
    return formatted;
  } catch (error) {
    console.error(`Matches xatoligi (liga ${leagueId}):`, error.message);
    return [];
  }
}

/**
 * Get current live matches across football
 */
export async function getLiveMatches() {
  const cacheKey = `live_matches_all`;
  const cached = cache.get(cacheKey);
  if (cached) return cached;

  try {
    const data = await fetchFromRapidApi('/football-current-live');
    const liveList = data?.response?.live || [];

    const formatted = liveList.map((m) => {
      const timeInfo = formatToTashkentTime(m.status?.utcTime || m.time);
      return {
        id: m.id,
        leagueId: m.leagueId,
        leagueName: m.leagueName,
        homeTeam: {
          id: m.home?.id,
          name: m.home?.name,
          score: m.home?.score ?? 0,
          badge: `https://images.fotmob.com/image_resources/logo/teamlogo/${m.home?.id}.png`
        },
        awayTeam: {
          id: m.away?.id,
          name: m.away?.name,
          score: m.away?.score ?? 0,
          badge: `https://images.fotmob.com/image_resources/logo/teamlogo/${m.away?.id}.png`
        },
        status: {
          live: true,
          scoreStr: `${m.home?.score ?? 0} - ${m.away?.score ?? 0}`,
          liveTime: m.status?.liveTime?.short || 'LIVE'
        },
        tashkentTime: timeInfo.time,
        tashkentDate: timeInfo.date
      };
    });

    cache.set(cacheKey, formatted, 30); // 30s cache for live
    return formatted;
  } catch (error) {
    console.error('Live matches xatoligi:', error.message);
    return [];
  }
}

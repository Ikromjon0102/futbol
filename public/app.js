// ==================== STATE ====================
const state = {
  currentTab: 'matches', // 'matches' | 'standings' | 'stats' | 'legioners' | 'favorites'
  currentLeagueId: 1001, // Default Uzbekistan Super League (1-o'rinda)
  currentRound: 1,
  totalRounds: 2,
  roundsList: [],
  leagues: [],
  matches: [],
  standings: [],
  stats: { topScorers: [], topAssists: [] },
  legioners: [],
  upcomingMatches: [],
  favorites: JSON.parse(localStorage.getItem('futbol_favorites') || '[]'),
  fontSize: localStorage.getItem('futbol_font_size') || 'large',
  notificationsEnabled: localStorage.getItem('futbol_notifications') === 'true',
  sentNotifications: JSON.parse(localStorage.getItem('futbol_sent_notifs') || '{}'),
  selectedMatchForModal: null,
  loading: false,
  deferredPrompt: null
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', async () => {
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
  }

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW error:', err));
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    state.deferredPrompt = e;
    const pwaBtn = document.getElementById('pwa-install-btn');
    if (pwaBtn) pwaBtn.classList.remove('hidden');
  });

  await loadLeagues();
  await switchLeague(1001); // Default O'zbekiston Superligasi
  await loadUpcomingMatches();

  // Periodic favorite notification check (every 30s)
  setInterval(() => {
    checkUpcomingFavoriteMatches();
  }, 30000);

  // Background auto-refresh for live match scores (every 30s)
  setInterval(() => {
    if (state.currentTab === 'matches') {
      loadMatches(state.currentLeagueId, state.currentRound);
    }
  }, 30000);
});

// ==================== MANUAL LIVE REFRESH ====================
async function manualRefresh() {
  const icon = document.getElementById('refresh-icon');
  if (icon) icon.classList.add('animate-spin');

  try {
    // 1. Trigger background server sync
    fetch('/api/sync/live', { method: 'POST' }).catch(() => {});

    // 2. Refresh active league view
    await loadRounds(state.currentLeagueId);
    if (state.currentTab === 'matches') {
      await loadMatches(state.currentLeagueId, state.currentRound);
    } else if (state.currentTab === 'standings') {
      await loadStandings(state.currentLeagueId);
    } else if (state.currentTab === 'stats') {
      await loadStats(state.currentLeagueId);
    } else if (state.currentTab === 'favorites') {
      await loadUpcomingMatches();
      renderFavorites();
    }

    showNotificationToast("✅ Ayni vaqt bo'yicha ma'lumotlar yangilandi!");
  } catch (err) {
    showNotificationToast("🔄 Ma'lumotlar yangilandi");
  } finally {
    if (icon) {
      setTimeout(() => icon.classList.remove('animate-spin'), 600);
    }
  }
}

// ==================== AUDIO SYNTHESIZER ====================
function playMatchWhistle() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(2400, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1800, ctx.currentTime + 0.15);
    osc.frequency.setValueAtTime(2600, ctx.currentTime + 0.25);
    osc.frequency.exponentialRampToValueAtTime(1600, ctx.currentTime + 0.45);

    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (e) {}
}

// ==================== NOTIFICATIONS ====================
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    alert("Brauzeringiz xabarnomalarni qo'llab-quvvatlamaydi.");
    return false;
  }

  const perm = await Notification.requestPermission();
  if (perm === 'granted') {
    state.notificationsEnabled = true;
    localStorage.setItem('futbol_notifications', 'true');
    showNotificationToast("🔔 Xabarnomalar yoqildi! Sevimli jamoangiz o'yini boshlanishidan 10 daqiqa oldin xabar beriladi.");
    return true;
  } else {
    state.notificationsEnabled = false;
    localStorage.setItem('futbol_notifications', 'false');
    return false;
  }
}

function sendMatchNotification(title, body) {
  playMatchWhistle();
  if (navigator.vibrate) navigator.vibrate([200, 100, 200]);

  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {
      body: body,
      icon: 'https://images.fotmob.com/image_resources/logo/leaguelogo/dark/47.png'
    });
  }

  showNotificationToast(`🔔 ${title}\n${body}`);
}

function showNotificationToast(msg) {
  let toast = document.getElementById('notification-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'notification-toast';
    toast.className = 'fixed top-16 left-4 right-4 max-w-md mx-auto z-50 bg-emerald-600 text-white p-4 rounded-2xl shadow-2xl font-bold border border-emerald-400 text-sm sm:text-base flex items-center justify-between transition-all transform duration-300';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `
    <div class="flex items-center gap-3">
      <span class="text-2xl">⚽</span>
      <div>${msg.replace(/\n/g, '<br/>')}</div>
    </div>
    <button onclick="this.parentElement.classList.add('hidden')" class="text-white text-lg ml-2">✕</button>
  `;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 8000);
}

function testNotification() {
  requestNotificationPermission().then(() => {
    sendMatchNotification(
      "⚽ O'yin boshlanmoqda! (10 daqiqa qoldi)",
      "Navbahor vs Nasaf o'yini 19:30 da (Toshkent vaqti) boshlanadi!"
    );
  });
}

function checkUpcomingFavoriteMatches() {
  if (state.favorites.length === 0) return;

  const nowTs = Math.floor(Date.now() / 1000);

  state.upcomingMatches.forEach(m => {
    const isFavHome = state.favorites.includes(m.homeTeam?.id);
    const isFavAway = state.favorites.includes(m.awayTeam?.id);

    if (isFavHome || isFavAway) {
      const matchTs = m.tashkentTimestamp;
      const diffSec = matchTs - nowTs;
      const diffMinutes = Math.floor(diffSec / 60);

      if (diffMinutes >= 1 && diffMinutes <= 10) {
        const notifKey = `notif_${m.id}_10min`;
        if (!state.sentNotifications[notifKey]) {
          state.sentNotifications[notifKey] = true;
          localStorage.setItem('futbol_sent_notifs', JSON.stringify(state.sentNotifications));

          const favTeam = isFavHome ? m.homeTeam.name : m.awayTeam.name;
          sendMatchNotification(
            `⚽ ${favTeam} o'yini boshlanmoqda! (${diffMinutes} daqiqa qoldi)`,
            `${m.homeTeam.name} vs ${m.awayTeam.name} • Toshkent vaqti: ${m.tashkentTime}`
          );
        }
      }
    }
  });
}

// ==================== FONT RESIZER ====================
function applyFontSize(size) {
  state.fontSize = size;
  localStorage.setItem('futbol_font_size', size);
  document.documentElement.setAttribute('data-font-size', size);

  ['normal', 'large', 'xlarge'].forEach(s => {
    const btn = document.getElementById(`font-btn-${s}`);
    if (btn) {
      if (s === size) {
        btn.classList.add('bg-emerald-600', 'text-white');
        btn.classList.remove('bg-slate-800', 'text-slate-300');
      } else {
        btn.classList.remove('bg-emerald-600', 'text-white');
        btn.classList.add('bg-slate-800', 'text-slate-300');
      }
    }
  });
}

// ==================== DATA FETCHING ====================
async function loadLeagues() {
  try {
    const res = await fetch('/api/leagues');
    const json = await res.json();
    if (json.status === 'success') {
      state.leagues = json.data;
      renderLeagueTabs();
    }
  } catch (e) {}
}

async function loadUpcomingMatches() {
  try {
    const res = await fetch('/api/upcoming');
    const json = await res.json();
    if (json.status === 'success') {
      state.upcomingMatches = json.data;
    }
  } catch (e) {}
}

async function switchLeague(leagueId) {
  state.currentLeagueId = leagueId;
  renderLeagueTabs();

  if (state.currentTab === 'standings') {
    await loadStandings(leagueId);
  } else if (state.currentTab === 'stats') {
    await loadStats(leagueId);
  } else {
    await loadRounds(leagueId);
    await loadMatches(leagueId, state.currentRound);
  }
}

async function loadRounds(leagueId) {
  try {
    const res = await fetch(`/api/rounds/${leagueId}`);
    const json = await res.json();
    if (json.status === 'success') {
      state.roundsList = json.rounds || [];
      state.totalRounds = state.roundsList.length;
      state.currentRound = json.currentRound || 1;
      renderRoundControls();
    }
  } catch (e) {}
}

async function loadMatches(leagueId, roundNum) {
  showLoader(true);
  try {
    const res = await fetch(`/api/matches/${leagueId}?round=${roundNum}`);
    const json = await res.json();
    if (json.status === 'success') {
      state.matches = json.data;
      state.currentRound = json.round || roundNum;
      renderRoundControls();
      renderMatches();
    }
  } catch (e) {
    renderError("O'yinlar ma'lumotini yuklab bo'lmadi.");
  } finally {
    showLoader(false);
  }
}

async function loadStandings(leagueId) {
  showLoader(true);
  try {
    const res = await fetch(`/api/standings/${leagueId}`);
    const json = await res.json();
    if (json.status === 'success') {
      state.standings = json.data;
      renderStandings();
    }
  } catch (e) {
    renderError("Turnir jadvalini yuklab bo'lmadi.");
  } finally {
    showLoader(false);
  }
}

async function loadStats(leagueId) {
  showLoader(true);
  try {
    const res = await fetch(`/api/stats/${leagueId}`);
    const json = await res.json();
    if (json.status === 'success') {
      state.stats = json.data;
      renderStats();
    }
  } catch (e) {
    renderError("Statistika yuklanmadi.");
  } finally {
    showLoader(false);
  }
}

async function loadLegioners() {
  showLoader(true);
  try {
    const res = await fetch('/api/legioners');
    const json = await res.json();
    if (json.status === 'success') {
      state.legioners = json.data;
      renderLegioners();
    }
  } catch (e) {
    renderError("Legionerlar ma'lumoti yuklanmadi.");
  } finally {
    showLoader(false);
  }
}

// ==================== ROUND NAVIGATION ====================
function changeRound(delta) {
  const currentIndex = state.roundsList.findIndex(r => r.round === state.currentRound);
  if (currentIndex !== -1) {
    const newIndex = currentIndex + delta;
    if (newIndex >= 0 && newIndex < state.roundsList.length) {
      const nextRoundObj = state.roundsList[newIndex];
      state.currentRound = nextRoundObj.round;
      loadMatches(state.currentLeagueId, nextRoundObj.round);
    }
  }
}

function onRoundSelectChange(selectElem) {
  const val = parseInt(selectElem.value);
  if (val) {
    state.currentRound = val;
    loadMatches(state.currentLeagueId, val);
  }
}

// ==================== RENDERING ====================
function renderLeagueTabs() {
  const container = document.getElementById('league-tabs-container');
  if (!container) return;

  container.innerHTML = state.leagues.map(l => {
    const isActive = l.id === state.currentLeagueId;
    return `
      <button onclick="switchLeague(${l.id})" 
        class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold transition-all text-sm sm:text-base border ${
          isActive 
            ? 'bg-emerald-600 border-emerald-500 text-white shadow-lg shadow-emerald-900/40' 
            : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-700'
        }">
        <span class="text-lg">${l.flag}</span>
        <span>${l.name}</span>
        ${l.badge ? `<span class="bg-amber-500 text-slate-950 text-xs px-1.5 py-0.5 rounded-full font-black">${l.id === 1001 ? '🇺🇿' : '⭐'}</span>` : ''}
      </button>
    `;
  }).join('');
}

function renderRoundControls() {
  const wrapper = document.getElementById('round-controls-wrapper');
  if (!wrapper) return;

  if (state.currentTab !== 'matches') {
    wrapper.classList.add('hidden');
    return;
  }
  wrapper.classList.remove('hidden');

  const currentIndex = state.roundsList.findIndex(r => r.round === state.currentRound);
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < state.roundsList.length - 1;

  wrapper.innerHTML = `
    <div class="flex items-center justify-between bg-slate-900/90 p-2.5 rounded-2xl border border-slate-800 shadow-md">
      <button onclick="changeRound(-1)" 
        class="px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-1.5 transition ${
          hasPrev ? 'bg-slate-800 text-slate-100 hover:bg-slate-700 active:scale-95 border border-slate-700' : 'bg-slate-900 text-slate-600 cursor-not-allowed border border-slate-800/50'
        }" ${!hasPrev ? 'disabled' : ''}>
        <span>◀</span>
        <span class="hidden sm:inline">Oldingi tur</span>
      </button>

      <div class="flex items-center gap-2">
        <select onchange="onRoundSelectChange(this)" 
          class="bg-slate-800 border border-emerald-500 text-emerald-400 font-extrabold text-sm sm:text-base px-3 py-2 rounded-xl text-center focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer">
          ${state.roundsList.map(r => `
            <option value="${r.round}" ${r.round === state.currentRound ? 'selected' : ''}>
              ${r.round}-tur ${r.finished === r.total ? '(Natijalar)' : '(Navbatdagi)'}
            </option>
          `).join('')}
        </select>
      </div>

      <button onclick="changeRound(1)" 
        class="px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-1.5 transition ${
          hasNext ? 'bg-slate-800 text-slate-100 hover:bg-slate-700 active:scale-95 border border-slate-700' : 'bg-slate-900 text-slate-600 cursor-not-allowed border border-slate-800/50'
        }" ${!hasNext ? 'disabled' : ''}>
        <span class="hidden sm:inline">Keyingi tur</span>
        <span>▶</span>
      </button>
    </div>
  `;
}

function renderMatches() {
  const container = document.getElementById('content-area');
  if (!container) return;

  if (state.matches.length === 0) {
    container.innerHTML = `
      <div class="text-center py-16 px-4 bg-slate-900/60 rounded-2xl border border-slate-800">
        <div class="text-5xl mb-3">⚽</div>
        <h3 class="text-xl font-bold text-slate-200">${state.currentRound}-turda o'yinlar topilmadi</h3>
        <p class="text-slate-400 mt-1 text-sm">Boshqa turni tanlang</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="space-y-3.5">
      ${state.matches.map(m => renderMatchCard(m)).join('')}
    </div>
  `;
}

function renderMatchCard(m) {
  const isFavHome = state.favorites.includes(m.homeTeam?.id);
  const isFavAway = state.favorites.includes(m.awayTeam?.id);

  let statusBadge = '';
  if (m.isLive) {
    statusBadge = `
      <div class="flex items-center gap-1.5 bg-rose-600 text-white px-3 py-1 rounded-full text-xs font-black live-pulse shadow-md shadow-rose-900/50">
        <span class="w-2 h-2 rounded-full bg-white animate-ping"></span>
        <span>JONLI ${m.liveTime || ''}</span>
      </div>
    `;
  } else if (m.isFinished) {
    statusBadge = `
      <div class="bg-slate-700/80 text-slate-300 px-3 py-1 rounded-full text-xs font-bold border border-slate-600">
        Tugagan • Tafsilotlar ℹ️
      </div>
    `;
  } else {
    statusBadge = `
      <div class="bg-emerald-950/90 text-emerald-300 border border-emerald-700/70 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
        <span>⏰</span>
        <span>${m.tashkent?.displayDay || ''} ${m.tashkent?.time || ''}</span>
      </div>
    `;
  }

  let scoreDisplay = '';
  if (m.isLive || m.isFinished) {
    let cleanScore = m.scoreStr;
    if (!cleanScore && m.homeTeam.score !== null && m.awayTeam.score !== null) {
      cleanScore = `${m.homeTeam.score} : ${m.awayTeam.score}`;
    }
    if (cleanScore) {
      cleanScore = cleanScore.replace('-', ':').trim();
    } else {
      cleanScore = '0 : 0';
    }

    scoreDisplay = `
      <div class="score-badge-horizontal text-amber-400 text-2xl sm:text-3xl font-black shadow-lg">
        ${cleanScore}
      </div>
    `;
  } else {
    scoreDisplay = `
      <div class="flex flex-col items-center justify-center">
        <span class="text-xl sm:text-2xl font-black text-slate-400">VS</span>
        <div class="text-xs font-bold text-emerald-400 mt-1">${m.tashkent?.time || '--:--'}</div>
      </div>
    `;
  }

  const matchDataJson = JSON.stringify(m).replace(/"/g, '&quot;');

  return `
    <div onclick="openMatchDetailsModal(${matchDataJson})" 
      class="match-card p-4 sm:p-5 relative overflow-hidden cursor-pointer hover:border-emerald-500/60 transition">
      <!-- Header / Status -->
      <div class="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3 text-xs text-slate-400">
        <span class="font-bold text-slate-200">${m.roundName || 'Chempionat o\'yini'}</span>
        ${statusBadge}
      </div>

      <!-- Teams & STRICT Horizontal Score -->
      <div class="flex items-center justify-between gap-2 py-1">
        <!-- Home Team -->
        <div class="flex-1 flex flex-col items-center text-center max-w-[40%]">
          <div class="relative w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center p-1 rounded-2xl bg-slate-800/80 border border-slate-700 shadow-inner">
            <img src="${m.homeTeam.badge}" onerror="this.src='https://images.fotmob.com/image_resources/logo/leaguelogo/dark/47.png'" class="w-10 h-10 sm:w-12 sm:h-12 object-contain" alt="${m.homeTeam.name}" />
            <button onclick="event.stopPropagation(); toggleFavorite(${m.homeTeam.id}, '${m.homeTeam.name.replace(/'/g, "\\'")}')" class="absolute -top-1.5 -right-1.5 p-1 rounded-full bg-slate-900 border border-slate-700 text-xs">
              ${isFavHome ? '❤️' : '🤍'}
            </button>
          </div>
          <span class="mt-2 font-bold text-slate-100 text-sm sm:text-base leading-tight line-clamp-2">${m.homeTeam.name}</span>
        </div>

        <!-- Score or Time Center -->
        <div class="flex-shrink-0 flex items-center justify-center px-1">
          ${scoreDisplay}
        </div>

        <!-- Away Team -->
        <div class="flex-1 flex flex-col items-center text-center max-w-[40%]">
          <div class="relative w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center p-1 rounded-2xl bg-slate-800/80 border border-slate-700 shadow-inner">
            <img src="${m.awayTeam.badge}" onerror="this.src='https://images.fotmob.com/image_resources/logo/leaguelogo/dark/47.png'" class="w-10 h-10 sm:w-12 sm:h-12 object-contain" alt="${m.awayTeam.name}" />
            <button onclick="event.stopPropagation(); toggleFavorite(${m.awayTeam.id}, '${m.awayTeam.name.replace(/'/g, "\\'")}')" class="absolute -top-1.5 -right-1.5 p-1 rounded-full bg-slate-900 border border-slate-700 text-xs">
              ${isFavAway ? '❤️' : '🤍'}
            </button>
          </div>
          <span class="mt-2 font-bold text-slate-100 text-sm sm:text-base leading-tight line-clamp-2">${m.awayTeam.name}</span>
        </div>
      </div>

      <!-- Quick Goal Preview or Time info Footer -->
      <div class="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <span class="flex items-center gap-1.5">
          <span class="text-emerald-400 font-bold">🇺🇿</span>
          <span>Toshkent: <strong class="text-slate-200">${m.tashkent?.displayDay || ''} ${m.tashkent?.time || ''}</strong></span>
        </span>
        ${m.events && m.events.length > 0 ? `<span class="text-emerald-400 font-bold">⚽ ${m.events.filter(e => e.type === 'goal').length} ta gol (Daqiqalarni ko'rish) 👉</span>` : ''}
      </div>
    </div>
  `;
}

// ==================== MATCH DETAILS MODAL (GOALSCORERS & CARDS) ====================
function openMatchDetailsModal(match) {
  state.selectedMatchForModal = match;
  let modal = document.getElementById('match-details-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'match-details-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm';
    document.body.appendChild(modal);
  }

  const goals = (match.events || []).filter(e => e.type === 'goal');
  const cards = (match.events || []).filter(e => e.type === 'card');

  modal.innerHTML = `
    <div class="bg-[#152238] border border-emerald-500/60 rounded-3xl p-5 max-w-md w-full shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <span class="text-xs font-bold text-emerald-400">${match.roundName || 'O\'yin tafsilotlari'}</span>
          <h3 class="text-base font-black text-white">${match.homeTeam.name} vs ${match.awayTeam.name}</h3>
        </div>
        <button onclick="closeMatchDetailsModal()" class="w-8 h-8 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-lg font-bold">✕</button>
      </div>

      <!-- Big Score Banner -->
      <div class="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center">
        <div class="flex items-center justify-center gap-6">
          <div class="text-center">
            <img src="${match.homeTeam.badge}" class="w-12 h-12 object-contain mx-auto mb-1" />
            <span class="font-bold text-sm text-white">${match.homeTeam.name}</span>
          </div>
          <div class="score-badge-horizontal text-3xl sm:text-4xl text-amber-400 font-black">
            ${match.scoreStr || 'VS'}
          </div>
          <div class="text-center">
            <img src="${match.awayTeam.badge}" class="w-12 h-12 object-contain mx-auto mb-1" />
            <span class="font-bold text-sm text-white">${match.awayTeam.name}</span>
          </div>
        </div>
        <div class="text-xs text-slate-400 mt-2">
          📍 ${match.stadium || 'Stadion'} • 🏁 ${match.referee || 'Hakam'}
        </div>
      </div>

      <!-- Goal Scorers Section -->
      <div class="space-y-2">
        <h4 class="text-sm font-black text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
          <span>⚽</span>
          <span>Gollar va Daqiqalar</span>
        </h4>
        ${goals.length > 0 ? `
          <div class="space-y-2 bg-slate-900/60 p-3 rounded-2xl border border-slate-800">
            ${goals.map(g => `
              <div class="flex items-center justify-between text-sm sm:text-base font-bold py-1 border-b border-slate-800/60 last:border-0">
                <div class="flex items-center gap-2">
                  <span class="text-emerald-400 font-black text-base">⚽ ${g.minute}'</span>
                  <span class="text-white">${g.player}</span>
                </div>
                <span class="text-xs text-slate-400 font-normal">(${g.detail || 'Gol'})</span>
              </div>
            `).join('')}
          </div>
        ` : `
          <p class="text-xs text-slate-400 italic bg-slate-900/40 p-3 rounded-xl">Gollar kiritilmagan yoki ma'lumot yo'q</p>
        `}
      </div>

      <!-- Cards Section -->
      ${cards.length > 0 ? `
        <div class="space-y-2">
          <h4 class="text-sm font-black text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
            <span>🟨</span>
            <span>Ogohlantirishlar</span>
          </h4>
          <div class="space-y-1.5 bg-slate-900/60 p-3 rounded-2xl border border-slate-800">
            ${cards.map(c => `
              <div class="flex items-center justify-between text-xs sm:text-sm font-semibold py-0.5">
                <div class="flex items-center gap-2">
                  <span>${c.card === 'red' ? '🟥' : '🟨'} ${c.minute}'</span>
                  <span class="text-slate-200">${c.player}</span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Close Button -->
      <button onclick="closeMatchDetailsModal()" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-2xl shadow-lg">
        Yopish
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

function closeMatchDetailsModal() {
  const modal = document.getElementById('match-details-modal');
  if (modal) modal.classList.add('hidden');
}

// ==================== STANDINGS VIEW ====================
function renderStandings() {
  const container = document.getElementById('content-area');
  if (!container) return;

  if (state.standings.length === 0) {
    container.innerHTML = `
      <div class="text-center py-16 px-4 bg-slate-900/60 rounded-2xl border border-slate-800">
        <div class="text-5xl mb-3">📊</div>
        <h3 class="text-xl font-bold text-slate-200">Jadval ma'lumotlari mavjud emas</h3>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="bg-slate-900/80 p-3 sm:p-4 rounded-2xl border border-slate-800 shadow-xl overflow-x-auto">
      <div class="flex items-center justify-between mb-3 px-2">
        <h3 class="font-extrabold text-base sm:text-lg text-emerald-400 flex items-center gap-2">
          <span>🏆</span>
          <span>Turnir Jadvali (2026/2027)</span>
        </h3>
        <button onclick="setTab('stats')" class="text-xs text-amber-400 font-bold bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
          🎯 To'purarlar 👉
        </button>
      </div>

      <table class="standings-table">
        <thead>
          <tr class="text-xs text-slate-400 uppercase font-semibold">
            <th class="text-center w-8">№</th>
            <th class="text-left">Klub</th>
            <th class="text-center w-10">O'</th>
            <th class="text-center w-10">G</th>
            <th class="text-center w-12 text-emerald-400 font-black">Ochko</th>
          </tr>
        </thead>
        <tbody>
          ${state.standings.map(t => {
            const isTop4 = t.rank <= 4;
            const isRelegation = t.rank >= state.standings.length - 2;
            const isFav = state.favorites.includes(t.id);

            return `
              <tr class="border-b border-slate-800/40 hover:bg-slate-800/50 transition">
                <td class="text-center font-bold text-sm ${
                  isTop4 ? 'text-emerald-400' : isRelegation ? 'text-rose-400' : 'text-slate-400'
                }">
                  ${t.rank}
                </td>
                <td>
                  <div class="flex items-center gap-2.5">
                    <img src="${t.badge}" onerror="this.src='https://images.fotmob.com/image_resources/logo/leaguelogo/dark/47.png'" class="w-6 h-6 object-contain" alt="${t.name}" />
                    <span class="font-bold text-sm sm:text-base text-slate-100">${t.name}</span>
                    <button onclick="toggleFavorite(${t.id}, '${t.name.replace(/'/g, "\\'")}')" class="text-xs">
                      ${isFav ? '❤️' : '🤍'}
                    </button>
                  </div>
                </td>
                <td class="text-center text-sm font-semibold text-slate-300">${t.played}</td>
                <td class="text-center text-xs font-medium text-slate-400">${t.scoresStr || t.goalDiff}</td>
                <td class="text-center font-black text-base sm:text-lg text-emerald-400 bg-emerald-950/40">${t.points}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ==================== STATS VIEW (TOP SCORERS & ASSISTS) ====================
function renderStats() {
  const container = document.getElementById('content-area');
  if (!container) return;

  const scorers = state.stats.topScorers || [];
  const assists = state.stats.topAssists || [];

  container.innerHTML = `
    <div class="space-y-4">
      <!-- Top Scorers (To'purarlar) -->
      <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 shadow-xl">
        <h3 class="font-extrabold text-base sm:text-lg text-amber-400 mb-3 flex items-center gap-2">
          <span>🎯</span>
          <span>To'purarlar Ro'yxati</span>
        </h3>
        <div class="space-y-2">
          ${scorers.length > 0 ? scorers.map((p, idx) => `
            <div class="flex items-center justify-between p-2.5 bg-slate-800/60 rounded-xl border border-slate-700/60">
              <div class="flex items-center gap-3">
                <span class="font-black text-sm ${idx < 3 ? 'text-amber-400' : 'text-slate-400'} w-5 text-center">${idx + 1}</span>
                <div>
                  <h4 class="font-black text-sm sm:text-base text-white">${p.player_name}</h4>
                  <p class="text-xs font-semibold text-emerald-400">${p.team_name} • ${p.matches} o'yin</p>
                </div>
              </div>
              <div class="text-right">
                <span class="text-xl sm:text-2xl font-black text-amber-400">${p.goals}</span>
                <span class="text-xs text-slate-400 block font-bold">gol</span>
              </div>
            </div>
          `).join('') : '<p class="text-center text-slate-400 py-4">To\'purarlar ma\'lumoti mavjud emas</p>'}
        </div>
      </div>

      <!-- Top Assists (Eng ko'p golli uzatma) -->
      <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 shadow-xl">
        <h3 class="font-extrabold text-base sm:text-lg text-emerald-400 mb-3 flex items-center gap-2">
          <span>👟</span>
          <span>Eng Ko'p Golli Uzatma (Assist)</span>
        </h3>
        <div class="space-y-2">
          ${assists.length > 0 ? assists.map((p, idx) => `
            <div class="flex items-center justify-between p-2.5 bg-slate-800/60 rounded-xl border border-slate-700/60">
              <div class="flex items-center gap-3">
                <span class="font-black text-sm ${idx < 3 ? 'text-emerald-400' : 'text-slate-400'} w-5 text-center">${idx + 1}</span>
                <div>
                  <h4 class="font-black text-sm sm:text-base text-white">${p.player_name}</h4>
                  <p class="text-xs font-semibold text-slate-300">${p.team_name}</p>
                </div>
              </div>
              <div class="text-right">
                <span class="text-xl sm:text-2xl font-black text-emerald-400">${p.assists}</span>
                <span class="text-xs text-slate-400 block font-bold">assist</span>
              </div>
            </div>
          `).join('') : '<p class="text-center text-slate-400 py-4">Assistlar ma\'lumoti mavjud emas</p>'}
        </div>
      </div>
    </div>
  `;
}

// ==================== TABS NAVIGATION ====================
function setTab(tabName) {
  state.currentTab = tabName;

  ['matches', 'standings', 'stats', 'favorites'].forEach(t => {
    const btn = document.getElementById(`nav-${t}`);
    if (btn) {
      if (t === tabName) {
        btn.classList.add('text-emerald-400', 'font-black');
        btn.classList.remove('text-slate-400');
      } else {
        btn.classList.remove('text-emerald-400', 'font-black');
        btn.classList.add('text-slate-400');
      }
    }
  });

  const leagueSelector = document.getElementById('league-selector-wrapper');
  const roundControls = document.getElementById('round-controls-wrapper');

  if (tabName === 'matches') {
    if (leagueSelector) leagueSelector.classList.remove('hidden');
    if (roundControls) roundControls.classList.remove('hidden');
    renderRoundControls();
    renderMatches();
  } else if (tabName === 'standings') {
    if (leagueSelector) leagueSelector.classList.remove('hidden');
    if (roundControls) roundControls.classList.add('hidden');
    loadStandings(state.currentLeagueId);
  } else if (tabName === 'stats') {
    if (leagueSelector) leagueSelector.classList.remove('hidden');
    if (roundControls) roundControls.classList.add('hidden');
    loadStats(state.currentLeagueId);
  } else if (tabName === 'favorites') {
    if (leagueSelector) leagueSelector.classList.add('hidden');
    if (roundControls) roundControls.classList.add('hidden');
    loadUpcomingMatches().then(() => renderFavorites());
  }
}

// ==================== HELPERS ====================
function showLoader(show) {
  const loader = document.getElementById('loading-spinner');
  if (loader) {
    if (show) loader.classList.remove('hidden');
    else loader.classList.add('hidden');
  }
}

function renderError(message) {
  const container = document.getElementById('content-area');
  if (container) {
    container.innerHTML = `
      <div class="text-center py-12 px-4 bg-rose-950/40 rounded-2xl border border-rose-800">
        <div class="text-4xl mb-2">⚠️</div>
        <p class="text-rose-200 font-bold">${message}</p>
        <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-rose-700 text-white font-bold rounded-xl">
          Qayta yuklash
        </button>
      </div>
    `;
  }
}

function installPWA() {
  if (state.deferredPrompt) {
    state.deferredPrompt.prompt();
    state.deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        const btn = document.getElementById('pwa-install-btn');
        if (btn) btn.classList.add('hidden');
      }
      state.deferredPrompt = null;
    });
  }
}

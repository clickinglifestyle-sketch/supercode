import { useState, useMemo, useCallback, useRef } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

// ─── Constants ────────────────────────────────────────────────────────────────

const POOL = Array.from({ length: 24 }, (_, i) => i + 1);
const PRIZES = [250000, 500, 50, 10, 2, 0, 0, 0, 2, 10, 50, 500, 250000];
const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MON_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const TOTAL_COMBOS = 2704156; // C(24,12)
const CHUNK_SIZE = 13521;     // 200 chunks

// ─── Seeded LCG ───────────────────────────────────────────────────────────────

function makeLCG(seed) {
  let s = ((seed ^ 0xdeadbeef) >>> 0) || 1;
  return () => {
    s = (Math.imul(1664525, s) + 1013904223) >>> 0;
    return s / 0x100000000;
  };
}

// ─── Historical data (synthetic, Aug 1 2025 – May 6 2026) ────────────────────
// Draws are generated deterministically via a seeded shuffle.
// Replace this array with real draw data if available.

function genData() {
  const data = [];
  const base = new Date(2025, 7, 1); // Aug 1, 2025
  for (let i = 0; i < 261; i++) {
    const d = new Date(base);
    d.setDate(d.getDate() + i);
    const label = `${DAY_NAMES[d.getDay()]} ${MON_NAMES[d.getMonth()]} ${String(d.getDate()).padStart(2, '0')}, ${d.getFullYear()}`;
    const rng = makeLCG(i * 7919 + 314159);
    const arr = [...POOL];
    // Partial Fisher-Yates: shuffle last 12 positions
    for (let j = 23; j >= 12; j--) {
      const k = Math.floor(rng() * (j + 1));
      [arr[j], arr[k]] = [arr[k], arr[j]];
    }
    data.unshift({ date: label, numbers: arr.slice(12).sort((a, b) => a - b) });
  }
  return data; // most-recent-first
}

const lotteryData = genData();

// ─── Bitmask utilities (fast 24-bit operations) ───────────────────────────────

function toBitmask(nums) {
  return nums.reduce((m, n) => m | (1 << (n - 1)), 0);
}

function popcount(x) {
  x -= (x >> 1) & 0x55555555;
  x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
  x = (x + (x >> 4)) & 0x0f0f0f0f;
  return Math.imul(x, 0x01010101) >>> 24;
}

function maskToNums(mask) {
  const r = [];
  for (let i = 0; i < 24; i++) if (mask & (1 << i)) r.push(i + 1);
  return r;
}

// Partial Fisher-Yates: returns a bitmask of 12 random bits from positions 0-23
function randMask(rng) {
  const arr = Array.from({ length: 24 }, (_, i) => i);
  for (let i = 23; i >= 12; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr.slice(12).reduce((m, b) => m | (1 << b), 0);
}

// Pre-compute draw bitmasks once
const drawMasks = lotteryData.map(d => toBitmask(d.numbers));
const N = lotteryData.length;

// ─── Scoring (used during Find Best search) ───────────────────────────────────

function score(mask) {
  let net = -N;
  let wins = 0;
  let prev = -1;
  let totalGap = 0;
  let gaps = 0;
  for (let i = 0; i < N; i++) {
    const prize = PRIZES[popcount(drawMasks[i] & mask)];
    net += prize;
    if (prize > 0) {
      if (prev >= 0) { totalGap += i - prev; gaps++; }
      prev = i;
      wins++;
    }
  }
  return { net, wins, avgGap: gaps > 0 ? totalGap / gaps : Infinity };
}

// ─── Full analysis (used for results display) ─────────────────────────────────

function analyze(selMask) {
  const rows = lotteryData.map((d, i) => {
    const matches = popcount(drawMasks[i] & selMask);
    const prize = PRIZES[matches];
    return { date: d.date, numbers: d.numbers, matches, prize, won: prize > 0 };
  });
  const spent = N;
  const won = rows.reduce((s, r) => s + r.prize, 0);
  const winCount = rows.filter(r => r.won).length;
  const winIdx = rows.map((r, i) => (r.won ? i : -1)).filter(x => x >= 0);
  let avgGap = null;
  if (winIdx.length > 1) {
    const gapList = winIdx.slice(1).map((v, i) => v - winIdx[i]);
    avgGap = Math.round(gapList.reduce((a, b) => a + b, 0) / gapList.length);
  }
  const dist = Array.from({ length: 13 }, (_, m) => ({
    m,
    count: rows.filter(r => r.matches === m).length,
  }));
  return {
    rows,
    spent,
    won,
    net: won - spent,
    roi: ((won - spent) / spent) * 100,
    winCount,
    winRate: (winCount / N) * 100,
    avgGap,
    dist,
  };
}

// ─── Strategy helpers ─────────────────────────────────────────────────────────

function computeFreqs(draws) {
  const f = new Array(25).fill(0);
  draws.forEach(d => d.numbers.forEach(n => f[n]++));
  return f;
}

function predictNext() {
  const recent = lotteryData.slice(0, 30);
  const f = computeFreqs(recent);
  const ranked = POOL.slice().sort((a, b) => f[b] - f[a]);
  // 6 hottest + 6 coldest
  return [...ranked.slice(0, 6), ...ranked.slice(18)].sort((a, b) => a - b);
}

function suggestNumbers() {
  const f = computeFreqs(lotteryData);
  const ranked = POOL.slice().sort((a, b) => f[b] - f[a]);
  // 4 most + 4 medium + 4 least frequent (non-overlapping slices)
  return [...ranked.slice(0, 4), ...ranked.slice(10, 14), ...ranked.slice(20)].sort((a, b) => a - b);
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const [selected, setSelected] = useState(new Set());
  const [showDetails, setShowDetails] = useState(false);
  const [filter50, setFilter50] = useState(false);
  const [searching, setSearching] = useState(false);
  const [progress, setProgress] = useState(0);
  const [strategy, setStrategy] = useState(null);   // null | 'trend' | 'suggest' | 'best'
  const [stratNums, setStratNums] = useState(null);
  const searchGen = useRef(0);

  const selMask = useMemo(
    () => (selected.size === 12 ? toBitmask([...selected]) : 0),
    [selected],
  );
  const stats = useMemo(() => (selMask !== 0 ? analyze(selMask) : null), [selMask]);
  const maxDist = stats ? Math.max(...stats.dist.map(d => d.count), 1) : 1;

  function toggle(n) {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(n)) next.delete(n);
      else if (next.size < 12) next.add(n);
      return next;
    });
    setStrategy(null);
    setStratNums(null);
  }

  function clearAll() {
    searchGen.current++;
    setSelected(new Set());
    setStrategy(null);
    setStratNums(null);
    setSearching(false);
    setProgress(0);
  }

  function applyStrategy(nums, strat) {
    searchGen.current++; // cancel any running search
    setSelected(new Set(nums));
    setStrategy(strat);
    setStratNums(nums);
    setSearching(false);
  }

  const handleFindBest = useCallback(() => {
    searchGen.current++;
    const myGen = searchGen.current;
    setSearching(true);
    setProgress(0);
    setStrategy('best');
    setStratNums(null);

    const f = computeFreqs(lotteryData);
    const byFreq = POOL.slice().sort((a, b) => f[b] - f[a]);

    // Seed the search with 6 strategic fixed candidates
    const seeds = [
      toBitmask(POOL.filter(n => n % 2 === 1)),  // all odd
      toBitmask(POOL.filter(n => n % 2 === 0)),  // all even
      toBitmask(POOL.slice(0, 12)),               // low 1-12
      toBitmask(POOL.slice(12)),                  // high 13-24
      toBitmask(byFreq.slice(0, 12)),             // most frequent
      toBitmask(byFreq.slice(12)),                // least frequent
    ];

    let best = { net: -Infinity, wins: 0, mask: seeds[0] };
    seeds.forEach(m => {
      const s = score(m);
      if (s.net > best.net || (s.net === best.net && s.wins > best.wins)) {
        best = { ...s, mask: m };
      }
    });

    let done = 0;
    const rng = makeLCG(Date.now() & 0xffffff);

    const tick = () => {
      if (searchGen.current !== myGen) return;
      const end = Math.min(done + CHUNK_SIZE, TOTAL_COMBOS);
      for (let i = done; i < end; i++) {
        const m = randMask(rng);
        const s = score(m);
        if (s.net > best.net || (s.net === best.net && s.wins > best.wins)) {
          best = { ...s, mask: m };
        }
      }
      done = end;
      setProgress(Math.round((done / TOTAL_COMBOS) * 100));
      if (done < TOTAL_COMBOS) {
        setTimeout(tick, 0);
      } else {
        if (searchGen.current !== myGen) return;
        const bestNums = maskToNums(best.mask);
        setSearching(false);
        setStratNums(bestNums);
        setSelected(new Set(bestNums));
      }
    };

    setTimeout(tick, 0);
  }, []);

  const displayRows = useMemo(() => {
    if (!stats) return [];
    return filter50 ? stats.rows.filter(r => r.prize >= 50) : stats.rows;
  }, [stats, filter50]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 md:p-8">
      <div className="max-w-3xl mx-auto space-y-4">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Texas All or Nothing</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            {N} historical draws · Aug 1, 2025 – May 6, 2026
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Win: <span className="text-green-500">0–3 or 9–12</span> matches ·
            Break even: <span className="text-gray-400">4 or 8</span> ·
            Lose: <span className="text-red-700">5–7</span>
          </p>
        </div>

        {/* Number grid */}
        <div className="bg-gray-900 rounded-2xl p-4">
          <div className="flex justify-between items-center mb-3">
            <span className="text-xs font-medium text-gray-400 tracking-widest uppercase">
              Select 12 Numbers
            </span>
            <span className={`text-sm font-bold ${selected.size === 12 ? 'text-green-400' : 'text-amber-400'}`}>
              {selected.size}/12
            </span>
          </div>
          <div className="grid grid-cols-8 gap-2">
            {POOL.map(n => {
              const isSel = selected.has(n);
              const disabled = !isSel && selected.size >= 12;
              return (
                <button
                  key={n}
                  onClick={() => toggle(n)}
                  disabled={disabled}
                  className={`
                    aspect-square rounded-xl text-sm font-bold transition-all duration-100 select-none
                    ${isSel
                      ? 'bg-blue-500 text-white shadow-md ring-2 ring-blue-400'
                      : disabled
                      ? 'bg-gray-800 text-gray-700 cursor-not-allowed'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700 active:scale-95'}
                  `}
                >
                  {n}
                </button>
              );
            })}
          </div>
        </div>

        {/* Strategy buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => applyStrategy(predictNext(), 'trend')}
            className="px-4 py-2.5 bg-orange-600 hover:bg-orange-500 rounded-xl text-sm font-semibold transition-colors"
          >
            🎯 Predict Next
          </button>
          <button
            onClick={() => applyStrategy(suggestNumbers(), 'suggest')}
            className="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 rounded-xl text-sm font-semibold transition-colors"
          >
            💡 Suggest Numbers
          </button>
          <button
            onClick={handleFindBest}
            disabled={searching}
            className="px-4 py-2.5 bg-emerald-700 hover:bg-emerald-600 disabled:opacity-60 disabled:cursor-not-allowed rounded-xl text-sm font-semibold transition-colors"
          >
            {searching ? `🔍 Searching… ${progress}%` : '🔍 Find Best'}
          </button>
          <button
            onClick={clearAll}
            className="px-4 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-xl text-sm font-semibold transition-colors ml-auto"
          >
            Clear All
          </button>
        </div>

        {/* Progress bar */}
        {searching && (
          <div className="bg-gray-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Strategy info box */}
        {strategy && stratNums && (
          <div className={`rounded-2xl p-4 border ${
            strategy === 'trend'
              ? 'bg-orange-950/50 border-orange-800'
              : strategy === 'suggest'
              ? 'bg-purple-950/50 border-purple-800'
              : 'bg-emerald-950/50 border-emerald-800'
          }`}>
            <div className={`text-sm font-semibold mb-2 ${
              strategy === 'trend' ? 'text-orange-400' :
              strategy === 'suggest' ? 'text-purple-400' :
              'text-emerald-400'
            }`}>
              {strategy === 'trend' && '🎯 Trend Prediction — 6 hottest + 6 coldest (last 30 draws)'}
              {strategy === 'suggest' && '💡 Balanced Suggestion — 4 most + 4 medium + 4 least frequent (all history)'}
              {strategy === 'best' && `🔍 Best Found — searched ${TOTAL_COMBOS.toLocaleString()} combinations`}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {stratNums.map(n => (
                <span
                  key={n}
                  className={`px-2.5 py-0.5 rounded-lg text-xs font-mono font-bold ${
                    strategy === 'trend' ? 'bg-orange-900/60 text-orange-200' :
                    strategy === 'suggest' ? 'bg-purple-900/60 text-purple-200' :
                    'bg-emerald-900/60 text-emerald-200'
                  }`}
                >
                  {n}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Empty states */}
        {selected.size === 0 && !searching && (
          <p className="text-center text-gray-600 py-8 text-sm">
            Select 12 numbers or use a strategy button to see analysis
          </p>
        )}
        {selected.size > 0 && selected.size < 12 && (
          <p className="text-center text-amber-700 py-8 text-sm">
            {12 - selected.size} more number{12 - selected.size !== 1 ? 's' : ''} needed
          </p>
        )}

        {/* Analysis results */}
        {stats && (
          <>
            {/* Financial summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Total Spent', val: `$${stats.spent.toLocaleString()}`, color: 'text-white' },
                { label: 'Total Won', val: `$${stats.won.toLocaleString()}`, color: 'text-green-400' },
                {
                  label: 'Net Profit',
                  val: `${stats.net >= 0 ? '+' : ''}$${stats.net.toLocaleString()}`,
                  color: stats.net >= 0 ? 'text-green-400' : 'text-red-400',
                },
                {
                  label: 'ROI',
                  val: `${stats.roi.toFixed(1)}%`,
                  color: stats.roi >= 0 ? 'text-green-400' : 'text-red-400',
                },
              ].map(({ label, val, color }) => (
                <div key={label} className="bg-gray-900 rounded-2xl p-4">
                  <div className="text-xs text-gray-500 mb-1">{label}</div>
                  <div className={`text-lg font-bold ${color}`}>{val}</div>
                </div>
              ))}
            </div>

            {/* Win stats */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Total Wins', val: stats.winCount, color: 'text-green-400' },
                { label: 'Total Losses', val: N - stats.winCount, color: 'text-red-400' },
                { label: 'Win Rate', val: `${stats.winRate.toFixed(1)}%`, color: 'text-amber-400' },
              ].map(({ label, val, color }) => (
                <div key={label} className="bg-gray-900 rounded-2xl p-4">
                  <div className="text-xs text-gray-500 mb-1">{label}</div>
                  <div className={`text-lg font-bold ${color}`}>{val}</div>
                </div>
              ))}
            </div>

            {/* Win frequency */}
            <div className="bg-gray-900 rounded-2xl p-4">
              <div className="text-xs text-gray-500 mb-1">Win Frequency</div>
              <div className="text-lg font-bold text-amber-400">
                {stats.avgGap ? `Every ~${stats.avgGap} draws` : 'No consecutive wins'}
              </div>
            </div>

            {/* Match distribution */}
            <div className="bg-gray-900 rounded-2xl p-4">
              <div className="text-sm font-semibold text-gray-300 mb-4">Match Distribution</div>
              <div className="space-y-2">
                {stats.dist.map(({ m, count }) => {
                  const prize = PRIZES[m];
                  const isBig = prize >= 250000;
                  const isWin = prize > 0;
                  const isBreak = prize === 2;
                  const barColor = isBig
                    ? 'bg-amber-500'
                    : isWin && !isBreak
                    ? 'bg-emerald-600'
                    : isBreak
                    ? 'bg-gray-600'
                    : 'bg-red-900';
                  return (
                    <div key={m} className="flex items-center gap-3">
                      <span className="text-xs text-gray-500 w-14 text-right font-mono">
                        {m} {isBig ? '🏆' : isWin && !isBreak ? '✓' : isBreak ? '±' : '✗'}
                      </span>
                      <div className="flex-1 bg-gray-800 rounded-full h-3 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${barColor} transition-all`}
                          style={{ width: `${(count / maxDist) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-6 text-right font-mono">{count}</span>
                      <span className="text-xs text-gray-700 w-20 text-right font-mono">
                        ${prize.toLocaleString()}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Detailed results table */}
            <div className="bg-gray-900 rounded-2xl p-4">
              <div className="flex items-center justify-between mb-3">
                <button
                  onClick={() => setShowDetails(v => !v)}
                  className="text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors"
                >
                  {showDetails ? '▾ Hide Details' : '▸ Show Details'}
                </button>
                {showDetails && (
                  <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={filter50}
                      onChange={e => setFilter50(e.target.checked)}
                      className="accent-blue-500"
                    />
                    $50+ wins only
                  </label>
                )}
              </div>

              {showDetails && (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse">
                    <thead>
                      <tr className="text-gray-500 border-b border-gray-800">
                        <th className="text-left py-2 pr-4 font-medium">Date</th>
                        <th className="text-center py-2 pr-4 font-medium">Matches</th>
                        <th className="text-right py-2 pr-4 font-medium">Prize</th>
                        <th className="text-center py-2 font-medium">Result</th>
                      </tr>
                    </thead>
                    <tbody>
                      {displayRows.map((r, i) => (
                        <tr
                          key={i}
                          className="border-b border-gray-800/40 hover:bg-gray-800/20 transition-colors"
                        >
                          <td className="py-2 pr-4 text-gray-400">{r.date}</td>
                          <td className="py-2 pr-4 text-center font-mono">{r.matches}</td>
                          <td className="py-2 pr-4 text-right font-mono">
                            {r.prize > 0 ? (
                              <span className={r.prize >= 500 ? 'text-amber-400 font-bold' : 'text-green-400'}>
                                ${r.prize.toLocaleString()}
                              </span>
                            ) : (
                              <span className="text-gray-700">$0</span>
                            )}
                          </td>
                          <td className="py-2 text-center">
                            {r.prize >= 250000 ? (
                              '🏆'
                            ) : r.prize >= 50 ? (
                              <CheckCircle className="inline w-3.5 h-3.5 text-green-500" />
                            ) : r.won ? (
                              <CheckCircle className="inline w-3.5 h-3.5 text-green-800" />
                            ) : (
                              <XCircle className="inline w-3.5 h-3.5 text-red-900" />
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {displayRows.length === 0 && (
                    <p className="text-center text-gray-600 py-6 text-xs">No draws match the filter</p>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

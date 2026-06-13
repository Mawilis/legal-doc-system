/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                  SPORTS DASHBOARD - TEAM MANAGEMENT & PERFORMANCE                                                                     ║
 * ║                              BIBLICAL WORTH BILLIONS | FORTUNE 500 READY                                                              ║
 * ║                                   NO COMPETITION. NO COMPROMISE. THE FUTURE, NOW.                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * * 🏛️ WILSY OS - SPORTS DASHBOARD v13.0.0-SPORTS-INTELLIGENCE
 * * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/industry/SportsDashboard.jsx
 * VERSION: 13.0.0-SPORTS-INTELLIGENCE
 * CREATED: 2026-04-05
 * * [COLLABORATION: EPITOME]
 * This component represents the pinnacle of Sports Operations UI.
 * It manages complex, multi-tiered arrays of player metrics and live matches.
 * Rogue JSX tags have been surgically purged.
 * This is a billion-dollar codebase. No child's place.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Trophy, Users, Calendar, DollarSign, TrendingUp, Loader2,
  Activity, Heart, Clock, AlertCircle, RefreshCw, Plus, Search,
  XCircle, Target, Shield, Brain, Cpu, Bell, Gauge
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5050';
const DEFAULT_WILSY_LOGO = '/src/assets/logo/wilsy.jpeg';


/**
 * @function SportsDashboard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const SportsDashboard = ({ onLogout, tenantConfig, roleView = 'OPERATIONS_VIEW' }) => {
  // [COLLABORATION: STATE MATRIX]
  // Segregated state management to prevent cross-contamination during re-renders.
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  const [metrics, setMetrics] = useState({
    squadSize: 0,
    avgAge: 0,
    totalValue: 0,
    upcomingMatches: 0,
    winRate: 0,
    leaguePosition: 0,
    goalsScored: 0,
    goalsConceded: 0,
    possessionAvg: 0,
    passAccuracy: 0,
    injuryCount: 0,
    avgAttendance: 0,
    youthPlayers: 0
  });

  const [players, setPlayers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [injuries, setInjuries] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // [COLLABORATION: TENANT MEMORIZATION]
  // Prevents deep-object comparison triggers in React Strict Mode.
  const tenantBranding = useMemo(() => {
    const branding = tenantConfig?.branding || {};
    return {
      logo: branding.logo || DEFAULT_WILSY_LOGO,
      clubName: branding.clubName || tenantConfig?.name || 'Football Club'
    };
  }, [tenantConfig]);

  // [COLLABORATION: UNIVERSAL FETCH PROTOCOL]
  // Abstracted fetch mechanism with tenant isolation headers.
  const fetchAPI = useCallback(async (endpoint) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-Tenant-Id': tenantConfig?.tenantId || 'MASTER'
    };
    const response = await fetch(url, { headers });
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
  }, [tenantConfig]);

  // [COLLABORATION: BATCH DATA RESOLVER]
  // Executes parallel asynchronous calls to the Citadel. Fault-tolerant arrays.
  const loadSportsData = useCallback(async () => {
    try {
      setError(null);
      const [metricsData, playersData, matchesData, standingsData, injuriesData, alertsData] = await Promise.all([
        fetchAPI('/api/sports/metrics').catch(() => null),
        fetchAPI('/api/sports/players').catch(() => []),
        fetchAPI('/api/sports/matches').catch(() => []),
        fetchAPI('/api/sports/standings').catch(() => []),
        fetchAPI('/api/sports/injuries').catch(() => []),
        fetchAPI('/api/sports/alerts').catch(() => [])
      ]);
      if (metricsData) setMetrics(metricsData);
      if (playersData) setPlayers(Array.isArray(playersData) ? playersData : []);
      if (matchesData) setMatches(Array.isArray(matchesData) ? matchesData : []);
      if (standingsData) setStandings(Array.isArray(standingsData) ? standingsData : []);
      if (injuriesData) setInjuries(Array.isArray(injuriesData) ? injuriesData : []);
      if (alertsData) setAlerts(Array.isArray(alertsData) ? alertsData : []);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [fetchAPI]);

  useEffect(() => { loadSportsData(); }, [loadSportsData]);

  
/**
 * @function handleRefresh
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadSportsData();
  };

  
/**
 * @function getWinRateColor
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const getWinRateColor = (rate) => {
    if (rate >= 65) return 'text-emerald-400';
    if (rate >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  
/**
 * @function getStatusColor
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'FIT': return 'text-emerald-400 bg-emerald-950/30';
      case 'MINOR': return 'text-yellow-400 bg-yellow-950/30';
      case 'MAJOR': return 'text-red-400 bg-red-950/30';
      default: return 'text-stone-400';
    }
  };

  const filteredPlayers = useMemo(() => {
    if (!searchTerm) return players;
    const term = searchTerm.toLowerCase();
    return players.filter(p => p.name?.toLowerCase().includes(term));
  }, [players, searchTerm]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-yellow-500 animate-spin mx-auto mb-4" />
          <p className="text-stone-500 text-xs">Loading Sports Intelligence Suite...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-black overflow-auto p-6">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="flex items-center gap-3">
            <Trophy className="w-8 h-8 text-yellow-500" />
            <h1 className="text-2xl font-black text-white">SPORTS <span className="text-yellow-500">DASHBOARD</span></h1>
            <div className="px-2 py-1 bg-yellow-500/20 rounded-full">
              <span className="text-[9px] text-yellow-400 font-black">{tenantBranding.clubName}</span>
            </div>
          </div>
          <p className="text-stone-500 text-xs mt-1">Squad Management • Performance Analytics • Injury Tracking</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleRefresh} disabled={isRefreshing} className="px-3 py-2 bg-stone-800 text-white text-xs rounded-md flex items-center gap-2">
            <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            {isRefreshing ? 'SYNCING...' : 'SYNC'}
          </button>
          <button onClick={onLogout} className="px-4 py-2 border border-red-800 text-red-400 text-xs font-black rounded-md">EXIT</button>
        </div>
      </div>

      {error && (
        <div className="bg-red-950/30 border border-red-800 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-red-500" />
            <p className="text-red-400 text-sm">{error}</p>
            <button onClick={loadSportsData} className="ml-auto text-red-400 text-xs underline">RETRY</button>
          </div>
        </div>
      )}

      {/* PRIMARY KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Users size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">SQUAD SIZE</span></div>
          <p className="text-2xl font-black text-white">{metrics.squadSize}</p>
          <p className="text-stone-500 text-[10px]">Youth: {metrics.youthPlayers}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><TrendingUp size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">AVERAGE AGE</span></div>
          <p className="text-2xl font-black text-white">{metrics.avgAge}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><DollarSign size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">SQUAD VALUE</span></div>
          <p className="text-2xl font-black text-emerald-400">€{(metrics.totalValue / 1000000).toFixed(0)}M</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Calendar size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">UPCOMING MATCHES</span></div>
          <p className="text-2xl font-black text-white">{metrics.upcomingMatches}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Trophy size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">WIN RATE</span></div>
          <p className={`text-2xl font-black ${getWinRateColor(metrics.winRate)}`}>{metrics.winRate}%</p>
        </div>
      </div>

      {/* SECONDARY KPIs */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Trophy size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">LEAGUE POS</p>
          <p className="text-xl font-black text-white">{metrics.leaguePosition}</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Activity size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">GOALS (F/A)</p>
          <p className="text-xl font-black text-white">{metrics.goalsScored}/{metrics.goalsConceded}</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Gauge size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">POSSESSION</p>
          <p className="text-xl font-black text-white">{metrics.possessionAvg}%</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Target size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">PASS ACC</p>
          <p className="text-xl font-black text-white">{metrics.passAccuracy}%</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Heart size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">INJURIES</p>
          <p className="text-xl font-black text-red-400">{metrics.injuryCount}</p>
        </div>
      </div>

      {/* TABS */}
      <div className="flex gap-1 border-b border-stone-800 mb-6">
        <button onClick={() => setActiveTab('overview')} className={`px-4 py-2 text-xs font-black uppercase ${activeTab === 'overview' ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500'}`}>PLAYERS</button>
        <button onClick={() => setActiveTab('matches')} className={`px-4 py-2 text-xs font-black uppercase ${activeTab === 'matches' ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500'}`}>MATCHES</button>
        <button onClick={() => setActiveTab('standings')} className={`px-4 py-2 text-xs font-black uppercase ${activeTab === 'standings' ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500'}`}>STANDINGS</button>
        <button onClick={() => setActiveTab('injuries')} className={`px-4 py-2 text-xs font-black uppercase ${activeTab === 'injuries' ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500'}`}>INJURIES</button>
        <button onClick={() => setActiveTab('alerts')} className={`px-4 py-2 text-xs font-black uppercase ${activeTab === 'alerts' ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500'}`}>ALERTS</button>
      </div>

      {/* PLAYERS TAB */}
      {activeTab === 'overview' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-yellow-900/30 flex justify-between items-center">
            <h3 className="text-yellow-500 text-xs font-black uppercase">PLAYER ROSTER</h3>
            <div className="relative">
              <Search size={12} className="absolute left-2 top-1/2 transform -translate-y-1/2 text-stone-500" />
              <input type="text" placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-48 pl-7 pr-2 py-1 bg-black border border-stone-700 rounded text-white text-xs" />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-stone-800/50">
                <tr><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Name</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Position</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Age</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Nationality</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Apps</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Goals</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Value</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Status</th></tr>
              </thead>
              <tbody>
                {filteredPlayers.length === 0 ? (
                  <tr><td colSpan={8} className="text-center py-8 text-stone-500 text-xs">No player data available</td></tr>
                ) : (
                  filteredPlayers.map((player) => (
                    <tr key={player.id} className="border-t border-stone-800 cursor-pointer hover:bg-stone-800/30" onClick={() => setSelectedPlayer(player)}>
                      <td className="px-4 py-2 text-white text-sm">{player.name}</td>
                      <td className="px-4 py-2 text-white text-xs">{player.position}</td>
                      <td className="px-4 py-2 text-white text-xs">{player.age}</td>
                      <td className="px-4 py-2 text-white text-xs">{player.nationality}</td>
                      <td className="px-4 py-2 text-white text-xs">{player.appearances}</td>
                      <td className="px-4 py-2 text-white text-xs">{player.goals}</td>
                      <td className="px-4 py-2 text-emerald-400 text-xs">€{(player.value / 1000000).toFixed(1)}M</td>
                      <td className="px-4 py-2"><span className={`px-2 py-1 rounded-full text-[9px] font-bold ${getStatusColor(player.fitness)}`}>{player.fitness}</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MATCHES TAB */}
      {activeTab === 'matches' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4">UPCOMING FIXTURES</h3>
          <div className="space-y-3">
            {matches.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No upcoming matches</p>
            ) : (
              matches.map((match, idx) => (
                <div key={idx} className="bg-black/30 rounded p-2 flex justify-between">
                  <div><p className="text-white text-xs">{match.competition}</p><p className="text-stone-400 text-[9px]">{match.date}</p></div>
                  <div className="text-right"><p className="text-yellow-400 text-[10px]">vs {match.opponent}</p></div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* STANDINGS TAB */}
      {activeTab === 'standings' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-yellow-900/30"><h3 className="text-yellow-500 text-xs font-black uppercase">LEAGUE TABLE</h3></div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-stone-800/50"><tr><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Pos</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Team</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Pld</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">W</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">D</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">L</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">GF</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">GA</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">GD</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Pts</th></tr></thead>
              <tbody>
                {standings.length === 0 ? (
                  <tr><td colSpan={10} className="text-center py-8 text-stone-500 text-xs">No standings available</td></tr>
                ) : (
                  standings.map((team, idx) => (
                    <tr key={idx} className={`border-t border-stone-800 ${team.isUserTeam ? 'bg-yellow-500/10' : ''}`}>
                      <td className="px-4 py-2 text-white text-xs">{team.position}</td>
                      <td className="px-4 py-2 text-white text-sm">{team.name}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.played}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.won}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.drawn}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.lost}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.goalsFor}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.goalsAgainst}</td>
                      <td className="px-4 py-2 text-white text-xs">{team.goalDifference}</td>
                      <td className="px-4 py-2 text-yellow-400 font-bold">{team.points}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* INJURIES TAB */}
      {activeTab === 'injuries' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4">INJURY REPORT</h3>
          <div className="space-y-3">
            {injuries.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No current injuries</p>
            ) : (
              injuries.map((injury, idx) => (
                <div key={idx} className="bg-black/30 rounded p-2 border-l-2 border-yellow-500">
                  <div className="flex justify-between"><p className="text-white text-xs">{injury.player}</p><p className="text-yellow-400 text-[10px]">{injury.expectedReturn}</p></div>
                  <p className="text-stone-400 text-[9px]">{injury.type}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ALERTS TAB */}
      {activeTab === 'alerts' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4">SPORTS ALERTS</h3>
          <div className="space-y-2">
            {alerts.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No active alerts</p>
            ) : (
              alerts.map((alert, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-black/30 rounded border-l-2 border-yellow-500">
                  <div><p className="text-[10px] font-bold text-yellow-400">{alert.type}</p><p className="text-white text-[10px]">{alert.message}</p></div>
                  <button className="text-yellow-500 text-[8px]">DISMISS</button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* PLAYER DETAIL MODAL */}
      {selectedPlayer && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-stone-900 border border-yellow-900/30 rounded-xl max-w-md w-full">
            <div className="flex justify-between items-center p-4 border-b border-yellow-900/30">
              <h2 className="text-white font-black text-lg">{selectedPlayer.name}</h2>
              <button onClick={() => setSelectedPlayer(null)} className="text-stone-400 hover:text-white"><XCircle size={20} /></button>
            </div>
            <div className="p-5">
              <div className="space-y-3">
                <div><p className="text-stone-400 text-[10px]">Position</p><p className="text-white text-lg font-bold">{selectedPlayer.position}</p></div>
                <div className="grid grid-cols-2 gap-2">
                  <div><p className="text-stone-400 text-[10px]">Age</p><p className="text-white">{selectedPlayer.age}</p></div>
                  <div><p className="text-stone-400 text-[10px]">Nationality</p><p className="text-white">{selectedPlayer.nationality}</p></div>
                  <div><p className="text-stone-400 text-[10px]">Appearances</p><p className="text-white">{selectedPlayer.appearances}</p></div>
                  <div><p className="text-stone-400 text-[10px]">Goals</p><p className="text-white">{selectedPlayer.goals}</p></div>
                  <div><p className="text-stone-400 text-[10px]">Value</p><p className="text-emerald-400">€{(selectedPlayer.value / 1000000).toFixed(1)}M</p></div>
                </div>
                <div className="flex gap-3 pt-4">
                  <button className="flex-1 px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md">VIEW STATS</button>
                  <button className="flex-1 px-4 py-2 border border-stone-700 text-stone-400 text-xs rounded-md">CLOSE</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <div className="mt-6 pt-4 border-t border-stone-800 text-center">
        <p className="text-stone-600 text-[7px]">WILSY OS v13.0.0-SPORTS-INTELLIGENCE | UEFA/FIFA 2026 Standards</p>
      </div>
    </div>
  );
};

export default SportsDashboard;
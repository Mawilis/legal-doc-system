/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║   ██████╗ ██╗   ██╗██████╗ ██╗     ██╗ ██████╗    ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████║         ║
 * ║   ██╔══██╗██║   ██║██╔══██╗██║     ██║██╔════╝    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██║         ║
 * ║   ██████╔╝██║   ██║██████╔╝██║     ██║██║         ██║  ██║███████║███████╗███████║██████╔╝██║  ██║███████║██████╔╝██║  ██║         ║
 * ║   ██╔══██╗██║   ██║██╔══██╗██║     ██║██║         ██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║  ██║██╔══██║██╔══██╗██║  ██║         ║
 * ║   ██████╔╝╚██████╔╝██████╔╝███████╗██║╚██████╗    ██████╔╝██║  ██║███████║██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║██████╔╝         ║
 * ║   ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝          ║
 * ║                                                                                                                                    ║
 * ║                  PUBLIC DASHBOARD - GOVERNMENT SERVICES MANAGEMENT                                                                 ║
 * ║                              BIBLICAL WORTH BILLIONS | FORTUNE 500 READY                                                            ║
 * ║                                   NO COMPETITION. NO COMPROMISE. THE FUTURE, NOW.                                                  ║
 * ║                                                                                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * 🏛️ WILSY OS - PUBLIC DASHBOARD v11.0.0-GOVERNMENT-INTELLIGENCE
 *
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/industry/PublicDashboard.jsx
 * VERSION: 11.0.0-GOVERNMENT-INTELLIGENCE
 * CREATED: 2026-04-04
 * LAST_MODIFIED: 2026-04-04
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Building2, Users, DollarSign, TrendingUp, Calendar, Loader2,
  Plus, Search, Eye, Shield, FileText, Clock, AlertCircle,
  CheckCircle, RefreshCw, Download, Filter, BarChart3,
  Phone, Mail, MapPin, Award, Target, Heart, Bell,
  XCircle, Activity, Gauge, Brain, Cpu, Zap, Globe,
  MessageCircle, ThumbsUp, ThumbsDown, Flag, BookOpen,
  Home, Trash2, Car, TreePine, Droplets, Wifi, Battery
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5050';
const DEFAULT_WILSY_LOGO = '/src/assets/logo/wilsy.jpeg';

const WORLD_CLASS_STANDARDS = {
  citizenSatisfaction: 85,
  serviceResolution: 95,
  budgetTransparency: 100,
  responseTime: 24,
  foiaCompliance: 100,
  digitalAdoption: 75,
  emergencyResponse: 15,
  openDataCompliance: 100
};

const PublicDashboard = ({ onLogout, tenantConfig, roleView = 'OPERATIONS_VIEW' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedRequest, setSelectedRequest] = useState(null);

  const [metrics, setMetrics] = useState({
    citizens: 0,
    services: 0,
    budget: 0,
    satisfaction: 0,
    activeProjects: 0,
    pendingRequests: 0,
    resolvedRequests: 0,
    avgResponseTime: 0,
    employeeCount: 0,
    digitalAdoption: 0,
    openDataScore: 0,
    foiaRequests: 0,
    emergencyAlerts: 0,
    budgetTransparency: 0,
    resolutionRate: 0
  });

  const [services, setServices] = useState([]);
  const [serviceRequests, setServiceRequests] = useState([]);
  const [budgetItems, setBudgetItems] = useState([]);
  const [projects, setProjects] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [alerts, setAlerts] = useState([]);

  const tenantBranding = useMemo(() => {
    const branding = tenantConfig?.branding || {};
    return {
      logo: branding.logo || DEFAULT_WILSY_LOGO,
      primaryColor: branding.primaryColor || '#EAB308',
      secondaryColor: branding.secondaryColor || '#1E293B',
      accentColor: branding.accentColor || '#10B981',
      companyName: branding.companyName || tenantConfig?.name || 'WILSY OS',
      supportEmail: branding.supportEmail || 'support@wilsy.com',
      supportPhone: branding.supportPhone || '+27 87 012 3456',
      governmentName: branding.governmentName || tenantConfig?.name || 'Municipal Government'
    };
  }, [tenantConfig]);

  const publicConfig = useMemo(() => {
    const config = tenantConfig?.public || {};
    return {
      satisfactionTarget: config.satisfactionTarget || WORLD_CLASS_STANDARDS.citizenSatisfaction,
      resolutionTarget: config.resolutionTarget || WORLD_CLASS_STANDARDS.serviceResolution,
      responseTarget: config.responseTarget || WORLD_CLASS_STANDARDS.responseTime,
      transparencyTarget: config.transparencyTarget || WORLD_CLASS_STANDARDS.budgetTransparency,
      digitalTarget: config.digitalTarget || WORLD_CLASS_STANDARDS.digitalAdoption
    };
  }, [tenantConfig]);

  const fetchAPI = useCallback(async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-Tenant-Id': tenantConfig?.tenantId || 'MASTER',
      ...options.headers
    };
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }, [tenantConfig]);

  const loadPublicData = useCallback(async () => {
    try {
      setError(null);

      const [
        metricsData,
        servicesData,
        requestsData,
        budgetData,
        projectsData,
        sentimentData,
        alertsData
      ] = await Promise.allSettled([
        fetchAPI('/api/public/metrics'),
        fetchAPI('/api/public/services'),
        fetchAPI('/api/public/requests'),
        fetchAPI('/api/public/budget'),
        fetchAPI('/api/public/projects'),
        fetchAPI('/api/public/analytics'),
        fetchAPI('/api/public/alerts')
      ]);

      if (metricsData.status === 'fulfilled' && metricsData.value) setMetrics(metricsData.value);
      if (servicesData.status === 'fulfilled' && servicesData.value) setServices(Array.isArray(servicesData.value) ? servicesData.value : servicesData.value.data || []);
      if (requestsData.status === 'fulfilled' && requestsData.value) setServiceRequests(Array.isArray(requestsData.value) ? requestsData.value : requestsData.value.data || []);
      if (budgetData.status === 'fulfilled' && budgetData.value) setBudgetItems(Array.isArray(budgetData.value) ? budgetData.value : budgetData.value.data || []);
      if (projectsData.status === 'fulfilled' && projectsData.value) setProjects(Array.isArray(projectsData.value) ? projectsData.value : projectsData.value.data || []);
      if (sentimentData.status === 'fulfilled' && sentimentData.value) setSentiment(sentimentData.value);
      if (alertsData.status === 'fulfilled' && alertsData.value) setAlerts(Array.isArray(alertsData.value) ? alertsData.value : alertsData.value.data || []);

      setLastUpdated(new Date());
    } catch (err) {
      console.error('[PUBLIC] Error loading public data:', err);
      setError(err.message || 'Failed to load government data');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [fetchAPI]);

  useEffect(() => {
    loadPublicData();
  }, [loadPublicData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadPublicData();
  };

  const getSatisfactionColor = (score) => {
    if (score >= 85) return 'text-emerald-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getStatusColor = (status) => {
    switch(status?.toUpperCase()) {
      case 'OPERATIONAL': return 'text-emerald-400 bg-emerald-950/30';
      case 'IN_PROGRESS': return 'text-yellow-400 bg-yellow-950/30';
      case 'PENDING': return 'text-blue-400 bg-blue-950/30';
      case 'RESOLVED': return 'text-purple-400 bg-purple-950/30';
      case 'COMPLETED': return 'text-emerald-400 bg-emerald-950/30';
      case 'EMERGENCY': return 'text-red-400 bg-red-950/30';
      default: return 'text-stone-400';
    }
  };

  const getBudgetUtilizationColor = (percentage) => {
    if (percentage <= 85) return 'text-emerald-400';
    if (percentage <= 95) return 'text-yellow-400';
    return 'text-red-400';
  };

  const filteredRequests = useMemo(() => {
    let filtered = serviceRequests;
    if (statusFilter !== 'all') {
      filtered = filtered.filter(r => r.status === statusFilter);
    }
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(r =>
        r.id?.toLowerCase().includes(term) ||
        r.type?.toLowerCase().includes(term) ||
        r.location?.toLowerCase().includes(term)
      );
    }
    return filtered;
  }, [serviceRequests, statusFilter, searchTerm]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-yellow-500 animate-spin mx-auto mb-4" />
          <p className="text-stone-500 text-xs">Loading WILSY OS Government Intelligence Suite...</p>
          <p className="text-stone-600 text-[9px] mt-2">Fetching live government data from {API_BASE_URL}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-black overflow-auto p-6">

      {/* HEADER SECTION */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="flex items-center gap-3">
            {tenantBranding.logo !== DEFAULT_WILSY_LOGO ? (
              <img src={tenantBranding.logo} alt="Government Logo" className="w-8 h-8 object-contain" />
            ) : (
              <Building2 className="w-8 h-8 text-yellow-500" />
            )}
            <h1 className="text-2xl font-black text-white">
              PUBLIC <span className="text-yellow-500">DASHBOARD</span>
            </h1>
            <div className="px-2 py-1 bg-yellow-500/20 border border-yellow-500/50 rounded-full flex items-center gap-1">
              <Shield size={10} className="text-yellow-500" />
              <span className="text-[9px] text-yellow-400 font-black">OGP v11.0 - GOVERNMENT INTELLIGENCE</span>
            </div>
          </div>
          <p className="text-stone-500 text-xs mt-1">
            Citizen Services • Budget Transparency • Performance Analytics • Open Government Data
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[8px] text-stone-600">
              Last sync: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'} |
              Standards: ACSI/OGP 2024
            </span>
            <Target size={8} className="text-yellow-500" />
          </div>
        </div>
        <div className="flex gap-3">
          <button onClick={handleRefresh} disabled={isRefreshing} className="px-3 py-2 bg-stone-800 text-white text-xs rounded-md flex items-center gap-2 hover:bg-stone-700">
            <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            {isRefreshing ? 'SYNCING...' : 'SYNC NOW'}
          </button>
          <button className="px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md flex items-center gap-2">
            <Plus size={14} /> SERVICE REQUEST
          </button>
          <button onClick={onLogout} className="px-4 py-2 border border-red-800 text-red-400 text-xs font-black rounded-md">
            EXIT
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-950/30 border border-red-800 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-red-500" />
            <p className="text-red-400 text-sm">{error}</p>
            <button onClick={loadPublicData} className="ml-auto text-red-400 text-xs underline">RETRY</button>
          </div>
        </div>
      )}

      {/* PRIMARY KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Users size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">CITIZENS SERVED</span></div>
          <p className="text-2xl font-black text-white">{metrics.citizens.toLocaleString()}</p>
          <p className="text-emerald-400 text-[10px]">Digital adoption: {metrics.digitalAdoption}%</p>
        </div>

        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Building2 size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">ACTIVE SERVICES</span></div>
          <p className="text-2xl font-black text-white">{metrics.services}</p>
          <p className="text-stone-500 text-[10px]">24/7 Operations</p>
        </div>

        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Heart size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">CITIZEN SATISFACTION</span></div>
          <p className={`text-2xl font-black ${getSatisfactionColor(metrics.satisfaction)}`}>{metrics.satisfaction}%</p>
          <p className="text-stone-500 text-[10px]">Target: {publicConfig.satisfactionTarget}%</p>
          <div className="mt-2 h-1.5 bg-stone-700 rounded-full overflow-hidden">
            <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${metrics.satisfaction}%` }} />
          </div>
        </div>

        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Clock size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">RESPONSE TIME</span></div>
          <p className={`text-2xl font-black ${metrics.avgResponseTime <= publicConfig.responseTarget ? 'text-emerald-400' : 'text-yellow-400'}`}>{metrics.avgResponseTime} hrs</p>
          <p className="text-stone-500 text-[10px]">Target: {publicConfig.responseTarget} hrs</p>
        </div>

        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><CheckCircle size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">RESOLUTION RATE</span></div>
          <p className="text-2xl font-black text-emerald-400">{metrics.resolutionRate}%</p>
          <p className="text-stone-500 text-[10px]">Target: {publicConfig.resolutionTarget}%</p>
        </div>
      </div>

      {/* SECONDARY KPIs */}
      <div className="grid grid-cols-6 gap-3 mb-6">
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <DollarSign size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">ANNUAL BUDGET</p>
          <p className="text-xl font-black text-white">R{(metrics.budget / 1000000).toFixed(0)}M</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Target size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">ACTIVE PROJECTS</p>
          <p className="text-xl font-black text-white">{metrics.activeProjects}</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Flag size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">PENDING REQUESTS</p>
          <p className="text-xl font-black text-yellow-400">{metrics.pendingRequests}</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <FileText size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">FOIA REQUESTS</p>
          <p className="text-xl font-black text-white">{metrics.foiaRequests}</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Shield size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">OPEN DATA SCORE</p>
          <p className="text-xl font-black text-emerald-400">{metrics.openDataScore}%</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center">
          <Bell size={12} className="text-yellow-500 mx-auto mb-1" />
          <p className="text-stone-400 text-[8px]">EMERGENCY ALERTS</p>
          <p className="text-xl font-black text-red-400">{metrics.emergencyAlerts}</p>
        </div>
      </div>

      {/* NAVIGATION TABS */}
      <div className="flex gap-1 border-b border-stone-800 mb-6">
        {[
          { id: 'overview', label: 'OVERVIEW', icon: Building2 },
          { id: 'services', label: 'SERVICES', icon: Shield },
          { id: 'requests', label: 'REQUESTS', icon: FileText },
          { id: 'budget', label: 'BUDGET', icon: DollarSign },
          { id: 'projects', label: 'PROJECTS', icon: Target },
          { id: 'alerts', label: 'ALERTS', icon: Bell }
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2 text-xs font-black uppercase transition-all ${activeTab === tab.id ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500 hover:text-stone-300'}`}>
            <tab.icon size={12} /> {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB - SERVICES TABLE */}
      {activeTab === 'overview' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-yellow-900/30">
            <h3 className="text-yellow-500 text-xs font-black uppercase flex items-center gap-2"><Shield size={12} /> GOVERNMENT SERVICES PERFORMANCE</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-stone-800/50">
                <tr>
                  <th className="px-4 py-2 text-left text-stone-400 text-[10px]">Service</th>
                  <th className="px-4 py-2 text-left text-stone-400 text-[10px]">Requests</th>
                  <th className="px-4 py-2 text-left text-stone-400 text-[10px]">Satisfaction</th>
                  <th className="px-4 py-2 text-left text-stone-400 text-[10px]">Budget Utilization</th>
                  <th className="px-4 py-2 text-left text-stone-400 text-[10px]">Status</th>
                </tr>
              </thead>
              <tbody>
                {services.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-8 text-stone-500 text-xs">No service data available</td></tr>
                ) : (
                  services.map((service) => (
                    <tr key={service.id} className="border-t border-stone-800">
                      <td className="px-4 py-2 text-white text-sm font-medium">{service.name}</td>
                      <td className="px-4 py-2 text-white text-sm">{service.requests?.toLocaleString()}</td>
                      <td className="px-4 py-2"><span className={getSatisfactionColor(service.satisfaction)}>{service.satisfaction}%</span></td>
                      <td className="px-4 py-2">
                        <div className="w-32">
                          <div className="flex justify-between text-[9px] mb-0.5">
                            <span className="text-stone-400">R{(service.spent / 1000000).toFixed(0)}M</span>
                            <span className="text-stone-500">/ R{(service.budget / 1000000).toFixed(0)}M</span>
                          </div>
                          <div className="h-1.5 bg-stone-700 rounded-full overflow-hidden">
                            <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${(service.spent / service.budget) * 100}%` }} />
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-2"><span className={`px-2 py-1 rounded-full text-[9px] font-bold ${getStatusColor(service.status)}`}>{service.status}</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SERVICE REQUESTS TAB */}
      {activeTab === 'requests' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><FileText size={12} /> SERVICE REQUESTS TRACKING</h3>
          <div className="flex gap-2 mb-4">
            <div className="flex-1 relative"><Search size={12} className="absolute left-2 top-1/2 transform -translate-y-1/2 text-stone-500" /><input type="text" placeholder="Search requests..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full pl-7 pr-2 py-1 bg-black border border-stone-700 rounded text-white text-xs" /></div>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-2 py-1 bg-black border border-stone-700 rounded text-white text-xs">
              <option value="all">All Status</option>
              <option value="PENDING">Pending</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {filteredRequests.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No service requests found</p>
            ) : (
              filteredRequests.map((request) => (
                <div key={request.id} className="flex justify-between items-center p-2 bg-black/30 rounded cursor-pointer hover:bg-black/50" onClick={() => setSelectedRequest(request)}>
                  <div>
                    <p className="text-white text-xs font-medium">{request.type}</p>
                    <p className="text-stone-500 text-[9px]">{request.location}</p>
                    <p className="text-stone-500 text-[8px]">Submitted: {request.submitted}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-[10px] font-bold ${getStatusColor(request.status)}`}>{request.status}</p>
                    {request.eta && <p className="text-stone-500 text-[8px]">ETA: {request.eta}</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* BUDGET TAB */}
      {activeTab === 'budget' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><DollarSign size={12} /> BUDGET TRANSPARENCY & SPENDING</h3>
          <div className="mb-4 p-3 bg-yellow-500/10 rounded border border-yellow-500/30">
            <p className="text-[10px] text-stone-300 flex items-center gap-2"><Shield size={12} className="text-yellow-500" /> Open Government Data Compliance: {metrics.openDataScore}% | Transparency Score: {metrics.budgetTransparency}%</p>
          </div>
          <div className="space-y-3">
            {budgetItems.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No budget data available</p>
            ) : (
              budgetItems.map((item) => (
                <div key={item.category}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-white">{item.category}</span>
                    <span className={getBudgetUtilizationColor(item.percentage)}>{item.percentage}% utilized</span>
                  </div>
                  <div className="h-1.5 bg-stone-700 rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${item.percentage}%` }} />
                  </div>
                  <div className="flex justify-between text-[9px] mt-0.5">
                    <span className="text-stone-500">Spent: R{(item.spent / 1000000).toFixed(0)}M</span>
                    <span className="text-emerald-400">Remaining: R{(item.remaining / 1000000).toFixed(0)}M</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* PROJECTS TAB */}
      {activeTab === 'projects' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Target size={12} /> ACTIVE GOVERNMENT PROJECTS</h3>
          <div className="space-y-3">
            {projects.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No project data available</p>
            ) : (
              projects.map((project) => (
                <div key={project.id} className="bg-black/30 rounded p-2 border-l-2 border-yellow-500">
                  <div className="flex justify-between">
                    <p className="text-white text-xs font-medium">{project.name}</p>
                    <p className="text-emerald-400 text-[10px]">{project.progress}% complete</p>
                  </div>
                  <p className="text-stone-400 text-[9px] mt-1">{project.description}</p>
                  <div className="mt-1 h-1.5 bg-stone-700 rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${project.progress}%` }} />
                  </div>
                  <div className="flex justify-between text-[8px] mt-1">
                    <span className="text-stone-500">Budget: R{(project.budget / 1000000).toFixed(0)}M</span>
                    <span className="text-stone-500">Timeline: {project.startDate} → {project.endDate}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ALERTS TAB */}
      {activeTab === 'alerts' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Bell size={12} /> PUBLIC NOTIFICATIONS & EMERGENCY ALERTS</h3>
          <div className="space-y-2">
            {alerts.length === 0 ? (
              <p className="text-stone-500 text-xs text-center py-4">No active alerts</p>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id} className={`flex justify-between items-center p-2 bg-black/30 rounded border-l-2 ${alert.severity === 'EMERGENCY' ? 'border-red-500' : alert.severity === 'HIGH' ? 'border-orange-500' : 'border-yellow-500'}`}>
                  <div>
                    <p className={`text-[10px] font-bold ${alert.severity === 'EMERGENCY' ? 'text-red-400' : alert.severity === 'HIGH' ? 'text-orange-400' : 'text-yellow-400'}`}>{alert.severity}</p>
                    <p className="text-white text-[10px]">{alert.message}</p>
                    <p className="text-stone-500 text-[8px]">{alert.timestamp}</p>
                  </div>
                  <button className="text-yellow-500 text-[8px]">ACKNOWLEDGE</button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* REQUEST DETAIL MODAL */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-stone-900 border border-yellow-900/30 rounded-xl max-w-md w-full">
            <div className="flex justify-between items-center p-4 border-b border-yellow-900/30">
              <h2 className="text-white font-black text-lg">Service Request Details</h2>
              <button onClick={() => setSelectedRequest(null)} className="text-stone-400 hover:text-white"><XCircle size={20} /></button>
            </div>
            <div className="p-5">
              <div className="space-y-3">
                <div><p className="text-stone-400 text-[10px]">Request ID</p><p className="text-white font-mono">{selectedRequest.id}</p></div>
                <div><p className="text-stone-400 text-[10px]">Type</p><p className="text-white text-lg font-bold">{selectedRequest.type}</p></div>
                <div><p className="text-stone-400 text-[10px]">Location</p><p className="text-white">{selectedRequest.location}</p></div>
                <div><p className="text-stone-400 text-[10px]">Status</p><p className={`font-bold ${getStatusColor(selectedRequest.status)}`}>{selectedRequest.status}</p></div>
                <div><p className="text-stone-400 text-[10px]">Submitted</p><p className="text-white">{selectedRequest.submitted}</p></div>
                {selectedRequest.resolved && <div><p className="text-stone-400 text-[10px]">Resolved</p><p className="text-white">{selectedRequest.resolved}</p></div>}
                {selectedRequest.eta && <div><p className="text-stone-400 text-[10px]">Estimated Resolution</p><p className="text-emerald-400">{selectedRequest.eta}</p></div>}
                <div className="flex gap-3 pt-4">
                  <button className="flex-1 px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md">TRACK PROGRESS</button>
                  <button className="flex-1 px-4 py-2 border border-stone-700 text-stone-400 text-xs rounded-md">CLOSE</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <div className="mt-6 pt-4 border-t border-stone-800 text-center">
        <div className="flex justify-center items-center gap-4 text-[8px] text-stone-500">
          <span className="flex items-center gap-1"><Shield size={10} className="text-emerald-400" /> OGP Certified</span>
          <span className="flex items-center gap-1"><Award size={10} className="text-emerald-400" /> ACSI Standards</span>
          <span className="flex items-center gap-1"><Target size={10} className="text-emerald-400" /> Open Data Compliant</span>
          <span className="flex items-center gap-1"><Brain size={10} className="text-yellow-500" /> AI Citizen Sentiment</span>
          <span className="flex items-center gap-1"><Cpu size={10} className="text-yellow-500" /> Predictive Analytics</span>
        </div>
        <p className="text-stone-600 text-[7px] mt-2">WILSY OS v11.0.0-GOVERNMENT-INTELLIGENCE | OGP Standards | ACSI Citizen Satisfaction Metrics</p>
      </div>
    </div>
  );
};

export default PublicDashboard;

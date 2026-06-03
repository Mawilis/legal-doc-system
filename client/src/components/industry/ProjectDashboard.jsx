/* eslint-disable */
/**
 * ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
 * 🏗️ PROJECT DASHBOARD - WILSY OS CONSTRUCTION & PROJECT INTELLIGENCE SUITE
 * ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
 *
 * FORTUNE 500 GRADE | BIBLICAL WORTH BILLIONS | 10/10 ENGINEERING EXCELLENCE
 *
 * 🏛️ WILSY OS - PROJECT DASHBOARD v9.0.0-CONSTRUCTION-INTELLIGENCE
 *
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/industry/ProjectDashboard.jsx
 * VERSION: 9.0.0-CONSTRUCTION-INTELLIGENCE
 * CREATED: 2026-04-03
 * LAST_MODIFIED: 2026-04-03
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Building2, Calendar, DollarSign, TrendingUp, Users, Loader2,
  Clock, AlertTriangle, CheckCircle, XCircle, RefreshCw, Plus,
  Search, Filter, Eye, Edit2, Trash2, Target, Award, Shield,
  Brain, Activity, BarChart3, PieChart, LineChart, Gauge,
  Zap, Cpu, Bell, MapPin, HardHat, Truck, FileText, Settings,
  Phone, Mail, MessageCircle, Globe, Lock, Cloud, Smartphone
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5050';
const DEFAULT_WILSY_LOGO = '/src/assets/logo/wilsy.jpeg';

const WORLD_CLASS_STANDARDS = {
  successRate: 85,
  onTimeDelivery: 90,
  onBudget: 85,
  projectMargin: 25,
  spi: 1.0,
  cpi: 1.0,
  riskMitigation: 90
};

const ProjectDashboard = ({ onLogout, tenantConfig, roleView = 'OPERATIONS_VIEW' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProject, setSelectedProject] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');

  const [metrics, setMetrics] = useState({
    activeProjects: 0,
    totalValue: 0,
    onTrack: 0,
    atRisk: 0,
    completed: 0,
    totalProjects: 0,
    successRate: 0,
    onTimeDelivery: 0,
    onBudget: 0,
    averageMargin: 0,
    spi: 0,
    cpi: 0,
    resourceUtilization: 0,
    openRisks: 0,
    overdueMilestones: 0,
    upcomingMilestones: 0
  });

  const [projects, setProjects] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [risks, setRisks] = useState([]);
  const [resources, setResources] = useState([]);
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
      supportPhone: branding.supportPhone || '+27 87 012 3456'
    };
  }, [tenantConfig]);

  const projectConfig = useMemo(() => {
    const config = tenantConfig?.project || {};
    return {
      successTarget: config.successTarget || WORLD_CLASS_STANDARDS.successRate,
      spiTarget: config.spiTarget || WORLD_CLASS_STANDARDS.spi,
      cpiTarget: config.cpiTarget || WORLD_CLASS_STANDARDS.cpi,
      marginTarget: config.marginTarget || WORLD_CLASS_STANDARDS.projectMargin,
      riskMitigationTarget: config.riskMitigationTarget || WORLD_CLASS_STANDARDS.riskMitigation
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

  const loadProjectData = useCallback(async () => {
    try {
      setError(null);

      const [
        metricsData,
        projectsData,
        milestonesData,
        risksData,
        resourcesData,
        alertsData
      ] = await Promise.allSettled([
        fetchAPI('/api/project/metrics'),
        fetchAPI('/api/project/list'),
        fetchAPI('/api/project/milestones'),
        fetchAPI('/api/project/risks'),
        fetchAPI('/api/project/resources'),
        fetchAPI('/api/project/alerts')
      ]);

      if (metricsData.status === 'fulfilled' && metricsData.value) setMetrics(metricsData.value);
      if (projectsData.status === 'fulfilled' && projectsData.value) setProjects(Array.isArray(projectsData.value) ? projectsData.value : projectsData.value.data || []);
      if (milestonesData.status === 'fulfilled' && milestonesData.value) setMilestones(Array.isArray(milestonesData.value) ? milestonesData.value : milestonesData.value.data || []);
      if (risksData.status === 'fulfilled' && risksData.value) setRisks(Array.isArray(risksData.value) ? risksData.value : risksData.value.data || []);
      if (resourcesData.status === 'fulfilled' && resourcesData.value) setResources(Array.isArray(resourcesData.value) ? resourcesData.value : resourcesData.value.data || []);
      if (alertsData.status === 'fulfilled' && alertsData.value) setAlerts(Array.isArray(alertsData.value) ? alertsData.value : alertsData.value.data || []);

      setLastUpdated(new Date());
    } catch (err) {
      console.error('[PROJECT] Error loading project data:', err);
      setError(err.message || 'Failed to load project data');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [fetchAPI]);

  useEffect(() => {
    loadProjectData();
  }, [loadProjectData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadProjectData();
  };

  const getStatusColor = (status) => {
    switch(status?.toUpperCase()) {
      case 'ON_TRACK': return 'text-emerald-400 bg-emerald-950/30';
      case 'AT_RISK': return 'text-red-400 bg-red-950/30';
      case 'DELAYED': return 'text-yellow-400 bg-yellow-950/30';
      case 'COMPLETED': return 'text-blue-400 bg-blue-950/30';
      default: return 'text-stone-400';
    }
  };

  const getSeverityColor = (severity) => {
    switch(severity?.toUpperCase()) {
      case 'CRITICAL': return 'text-red-400';
      case 'HIGH': return 'text-orange-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'LOW': return 'text-blue-400';
      default: return 'text-stone-400';
    }
  };

  const getSPIColor = (spi) => {
    if (spi >= 1.0) return 'text-emerald-400';
    if (spi >= 0.9) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getCPIColor = (cpi) => {
    if (cpi >= 1.0) return 'text-emerald-400';
    if (cpi >= 0.9) return 'text-yellow-400';
    return 'text-red-400';
  };

  const filteredProjects = useMemo(() => {
    let filtered = projects;
    if (statusFilter !== 'all') {
      filtered = filtered.filter(p => p.status === statusFilter);
    }
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(p =>
        p.name?.toLowerCase().includes(term) ||
        p.id?.toLowerCase().includes(term) ||
        p.manager?.toLowerCase().includes(term)
      );
    }
    return filtered;
  }, [projects, statusFilter, searchTerm]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-yellow-500 animate-spin mx-auto mb-4" />
          <p className="text-stone-500 text-xs">Loading WILSY OS Project Intelligence Suite...</p>
          <p className="text-stone-600 text-[9px] mt-2">Fetching live project data from {API_BASE_URL}</p>
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
              <img src={tenantBranding.logo} alt="Tenant Logo" className="w-8 h-8 object-contain" />
            ) : (
              <Building2 className="w-8 h-8 text-yellow-500" />
            )}
            <h1 className="text-2xl font-black text-white">
              PROJECT <span className="text-yellow-500">DASHBOARD</span>
            </h1>
            <div className="px-2 py-1 bg-yellow-500/20 border border-yellow-500/50 rounded-full flex items-center gap-1">
              <Cpu size={10} className="text-yellow-500" />
              <span className="text-[9px] text-yellow-400 font-black">EVM v9.0 - CONSTRUCTION INTELLIGENCE</span>
            </div>
          </div>
          <p className="text-stone-500 text-xs mt-1">
            Earned Value Management • Risk Register • Resource Optimization • PMBOK 7th Edition
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[8px] text-stone-600">
              Last sync: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'} |
              Standards: PMI Pulse 2024
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
            <Plus size={14} /> NEW PROJECT
          </button>
          <button onClick={onLogout} className="px-4 py-2 border border-red-800 text-red-400 text-xs font-black rounded-md">
            EXIT
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-950/30 border border-red-800 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-500" />
            <p className="text-red-400 text-sm">{error}</p>
            <button onClick={loadProjectData} className="ml-auto text-red-400 text-xs underline">RETRY</button>
          </div>
        </div>
      )}

      {/* PRIMARY KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Building2 size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">ACTIVE PROJECTS</span></div>
          <p className="text-2xl font-black text-white">{metrics.activeProjects}</p>
          <p className="text-stone-500 text-[10px]">Total: {metrics.totalProjects} projects</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><DollarSign size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">TOTAL VALUE</span></div>
          <p className="text-2xl font-black text-white">R{(metrics.totalValue / 1000000).toFixed(1)}M</p>
          <p className="text-emerald-400 text-[10px]">Portfolio margin: {metrics.averageMargin}%</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><CheckCircle size={14} className="text-emerald-500" /><span className="text-stone-400 text-[10px]">ON TRACK</span></div>
          <p className="text-2xl font-black text-emerald-400">{metrics.onTrack}</p>
          <p className="text-stone-500 text-[10px]">Success rate: {metrics.successRate}%</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><AlertTriangle size={14} className="text-red-500" /><span className="text-stone-400 text-[10px]">AT RISK</span></div>
          <p className="text-2xl font-black text-red-400">{metrics.atRisk}</p>
          <p className="text-stone-500 text-[10px]">Open risks: {metrics.openRisks}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Calendar size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">MILESTONES</span></div>
          <p className="text-2xl font-black text-white">{metrics.completed}</p>
          <p className="text-stone-500 text-[10px]">Upcoming: {metrics.upcomingMilestones}</p>
        </div>
      </div>

      {/* SECONDARY KPIs */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Gauge size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">SPI (Schedule)</p><p className={`text-xl font-black ${getSPIColor(metrics.spi)}`}>{metrics.spi?.toFixed(2) || '--'}</p><p className="text-stone-500 text-[7px]">Target: ≥1.0</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><DollarSign size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">CPI (Cost)</p><p className={`text-xl font-black ${getCPIColor(metrics.cpi)}`}>{metrics.cpi?.toFixed(2) || '--'}</p><p className="text-stone-500 text-[7px]">Target: ≥1.0</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Clock size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">ON-TIME DELIVERY</p><p className="text-xl font-black text-white">{metrics.onTimeDelivery}%</p><p className="text-stone-500 text-[7px]">Target: 90%</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Target size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">ON-BUDGET</p><p className="text-xl font-black text-white">{metrics.onBudget}%</p><p className="text-stone-500 text-[7px]">Target: 85%</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Users size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">RESOURCE UTIL.</p><p className="text-xl font-black text-white">{metrics.resourceUtilization}%</p><p className="text-stone-500 text-[7px]">Optimal: 80-85%</p></div>
      </div>

      {/* NAVIGATION TABS */}
      <div className="flex gap-1 border-b border-stone-800 mb-6">
        {[
          { id: 'overview', label: 'OVERVIEW', icon: Building2 },
          { id: 'projects', label: 'PROJECTS', icon: Target },
          { id: 'milestones', label: 'MILESTONES', icon: Calendar },
          { id: 'risks', label: 'RISK REGISTER', icon: AlertTriangle },
          { id: 'resources', label: 'RESOURCES', icon: Users },
          { id: 'alerts', label: 'ALERTS', icon: Bell }
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2 text-xs font-black uppercase transition-all ${activeTab === tab.id ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500 hover:text-stone-300'}`}>
            <tab.icon size={12} /> {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-yellow-900/30 flex justify-between items-center">
            <h3 className="text-yellow-500 text-xs font-black uppercase flex items-center gap-2"><Target size={12} /> ACTIVE PROJECTS (LIVE)</h3>
            <div className="flex gap-2">
              <div className="relative"><Search size={12} className="absolute left-2 top-1/2 transform -translate-y-1/2 text-stone-500" /><input type="text" placeholder="Search projects..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-48 pl-7 pr-2 py-1 bg-black border border-stone-700 rounded text-white text-xs" /></div>
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-2 py-1 bg-black border border-stone-700 rounded text-white text-xs">
                <option value="all">All Status</option>
                <option value="ON_TRACK">On Track</option>
                <option value="AT_RISK">At Risk</option>
                <option value="DELAYED">Delayed</option>
                <option value="COMPLETED">Completed</option>
              </select>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-stone-800/50">
                <tr><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Project Name</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Manager</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Budget</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Progress</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">SPI</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">CPI</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Status</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Due Date</th></tr>
              </thead>
              <tbody>
                {filteredProjects.length === 0 ? (
                  <tr><td colSpan={8} className="text-center py-8 text-stone-500 text-xs">No projects found</td></tr>
                ) : (
                  filteredProjects.map((project) => (
                    <tr key={project.id} className="border-t border-stone-800 hover:bg-stone-800/30 cursor-pointer" onClick={() => setSelectedProject(project)}>
                      <td className="px-4 py-2 text-white text-sm font-medium">{project.name}</td>
                      <td className="px-4 py-2 text-white text-xs">{project.manager}</td>
                      <td className="px-4 py-2 text-emerald-400 text-xs">R{(project.budget / 1000000).toFixed(1)}M</td>
                      <td className="px-4 py-2"><div className="flex items-center gap-2"><div className="w-16 h-1.5 bg-stone-700 rounded-full overflow-hidden"><div className="h-full bg-yellow-500 rounded-full" style={{ width: `${project.progress}%` }} /></div><span className="text-white text-xs">{project.progress}%</span></div></td>
                      <td className="px-4 py-2"><span className={getSPIColor(project.spi)}>{project.spi?.toFixed(2)}</span></td>
                      <td className="px-4 py-2"><span className={getCPIColor(project.cpi)}>{project.cpi?.toFixed(2)}</span></td>
                      <td className="px-4 py-2"><span className={`px-2 py-1 rounded-full text-[9px] font-bold ${getStatusColor(project.status)}`}>{project.status}</span></td>
                      <td className="px-4 py-2 text-white text-xs">{project.dueDate}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MILESTONES TAB */}
      {activeTab === 'milestones' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Calendar size={12} /> PROJECT MILESTONES</h3>
          <div className="space-y-3">
            {milestones.length === 0 ? <p className="text-stone-500 text-xs text-center py-4">No milestone data available</p> : milestones.map((milestone, idx) => (
              <div key={idx} className="bg-black/30 rounded p-2 flex justify-between items-center">
                <div><p className="text-white text-xs font-medium">{milestone.name}</p><p className="text-stone-500 text-[8px]">{milestone.project} • Due: {milestone.dueDate}</p></div>
                <div className="text-right"><span className={`px-2 py-1 rounded-full text-[8px] font-bold ${milestone.status === 'COMPLETED' ? 'text-emerald-400 bg-emerald-950/30' : milestone.status === 'OVERDUE' ? 'text-red-400 bg-red-950/30' : 'text-yellow-400 bg-yellow-950/30'}`}>{milestone.status}</span></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RISK REGISTER TAB */}
      {activeTab === 'risks' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><AlertTriangle size={12} /> RISK REGISTER (ISO 31000:2024)</h3>
          <div className="space-y-3">
            {risks.length === 0 ? <p className="text-stone-500 text-xs text-center py-4">No risk data available</p> : risks.map((risk, idx) => (
              <div key={idx} className="bg-black/30 rounded p-2 border-l-2 border-yellow-500">
                <div className="flex justify-between"><p className="text-white text-xs font-medium">{risk.name}</p><p className={`text-[10px] font-bold ${getSeverityColor(risk.severity)}`}>{risk.severity}</p></div>
                <p className="text-stone-400 text-[9px] mt-1">Mitigation: {risk.mitigation}</p>
                <p className="text-stone-500 text-[8px] mt-1">Owner: {risk.owner} • Probability: {risk.probability}%</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RESOURCES TAB */}
      {activeTab === 'resources' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Users size={12} /> RESOURCE ALLOCATION</h3>
          <div className="grid grid-cols-2 gap-4">
            {resources.length === 0 ? <p className="text-stone-500 text-xs text-center py-4 col-span-2">No resource data available</p> : resources.map((resource, idx) => (
              <div key={idx} className="bg-black/30 rounded p-2">
                <div className="flex justify-between"><p className="text-white text-xs font-medium">{resource.name}</p><p className="text-emerald-400 text-[10px]">{resource.utilization}%</p></div>
                <div className="mt-1 h-1.5 bg-stone-700 rounded-full overflow-hidden"><div className="h-full bg-yellow-500 rounded-full" style={{ width: `${resource.utilization}%` }} /></div>
                <p className="text-stone-500 text-[8px] mt-1">Role: {resource.role} • Projects: {resource.projectCount}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ALERTS TAB */}
      {activeTab === 'alerts' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Bell size={12} /> PROJECT ALERTS & NOTIFICATIONS</h3>
          <div className="space-y-2">
            {alerts.length === 0 ? <p className="text-stone-500 text-xs text-center py-4">No active alerts</p> : alerts.map((alert) => (
              <div key={alert.id} className={`flex justify-between items-center p-2 bg-black/30 rounded border-l-2 ${alert.severity === 'CRITICAL' ? 'border-red-500' : alert.severity === 'HIGH' ? 'border-orange-500' : alert.severity === 'MEDIUM' ? 'border-yellow-500' : 'border-blue-500'}`}>
                <div><p className={`text-[10px] font-bold ${getSeverityColor(alert.severity)}`}>{alert.severity}</p><p className="text-white text-[10px]">{alert.message}</p><p className="text-stone-500 text-[8px]">{alert.project} • {alert.timestamp}</p></div>
                <button className="text-yellow-500 text-[8px]">ACKNOWLEDGE</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PROJECT DETAIL MODAL */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-stone-900 border border-yellow-900/30 rounded-xl max-w-lg w-full">
            <div className="flex justify-between items-center p-4 border-b border-yellow-900/30"><h2 className="text-white font-black text-lg">{selectedProject.name}</h2><button onClick={() => setSelectedProject(null)} className="text-stone-400 hover:text-white"><XCircle size={20} /></button></div>
            <div className="p-5"><div className="space-y-3">
              <div><p className="text-stone-400 text-[10px]">Project Manager</p><p className="text-white">{selectedProject.manager}</p></div>
              <div><p className="text-stone-400 text-[10px]">Budget</p><p className="text-emerald-400 text-xl font-bold">R{(selectedProject.budget / 1000000).toFixed(1)}M</p></div>
              <div><p className="text-stone-400 text-[10px]">Progress</p><div className="mt-1 h-2 bg-stone-700 rounded-full overflow-hidden"><div className="h-full bg-yellow-500 rounded-full" style={{ width: `${selectedProject.progress}%` }} /></div><p className="text-white text-xs mt-1">{selectedProject.progress}% Complete</p></div>
              <div className="grid grid-cols-2 gap-2"><div><p className="text-stone-400 text-[10px]">SPI</p><p className={`text-lg font-bold ${getSPIColor(selectedProject.spi)}`}>{selectedProject.spi?.toFixed(2)}</p></div><div><p className="text-stone-400 text-[10px]">CPI</p><p className={`text-lg font-bold ${getCPIColor(selectedProject.cpi)}`}>{selectedProject.cpi?.toFixed(2)}</p></div></div>
              <div><p className="text-stone-400 text-[10px]">Status</p><p className={`px-2 py-1 inline-block rounded-full text-[9px] font-bold ${getStatusColor(selectedProject.status)}`}>{selectedProject.status}</p></div>
              <div className="flex gap-3 pt-4"><button className="flex-1 px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md">VIEW DETAILS</button><button className="flex-1 px-4 py-2 border border-stone-700 text-stone-400 text-xs rounded-md">CLOSE</button></div>
            </div></div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <div className="mt-6 pt-4 border-t border-stone-800 text-center">
        <div className="flex justify-center items-center gap-4 text-[8px] text-stone-500">
          <span className="flex items-center gap-1"><Shield size={10} className="text-emerald-400" /> PMBOK 7th Ed</span>
          <span className="flex items-center gap-1"><Award size={10} className="text-emerald-400" /> PMI Registered</span>
          <span className="flex items-center gap-1"><Target size={10} className="text-emerald-400" /> EVM Certified</span>
          <span className="flex items-center gap-1"><Brain size={10} className="text-yellow-500" /> AI Risk Prediction</span>
          <span className="flex items-center gap-1"><Cpu size={10} className="text-yellow-500" /> Resource Optimization</span>
        </div>
        <p className="text-stone-600 text-[7px] mt-2">WILSY OS v9.0.0-CONSTRUCTION-INTELLIGENCE | PMI Pulse Standards | Earned Value Management</p>
      </div>
    </div>
  );
};

export default ProjectDashboard;

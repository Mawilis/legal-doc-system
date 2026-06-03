/* eslint-disable */
/**
 * LOGISTICS DASHBOARD - WILSY OS LIVE DATA INTEGRATION
 * FORTUNE 500 GRADE | BIBLICAL WORTH BILLIONS
 * * 🏛️ WILSY OS - LOGISTICS DASHBOARD v7.0.0-LIVE-DATA
 * * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/industry/LogisticsDashboard.jsx
 * VERSION: 7.0.0-LIVE-DATA
 * CREATED: 2026-04-03
 * * EPITOME: The definitive logistics intelligence nexus. Engineered for zero-latency tracking,
 * cross-border metric aggregation, and predictive fleet analytics.
 * CLASSIFICATION: biblical worth billions no child's place
 * * COLLABORATION COMMENTS:
 * - Wilson: Removed invalid 'Cargo' import from lucide-react which was causing fatal Vite module execution failures.
 * - Wilson: Validated remaining icon imports to ensure strict compatibility with the environment.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Ship, Truck, Package, Map, Clock, AlertTriangle, DollarSign, Loader2,
  RefreshCw, Plus, Search, Filter, Eye, Edit2, Trash2, XCircle,
  Award, Target, Zap, Brain, Shield, BarChart3, PieChart, LineChart,
  Activity, Gift, CreditCard, Globe, Lock, Cloud, Users, Phone,
  Mail, MessageCircle, Navigation, Anchor, Warehouse,
  Tractor, Car, Wrench, Sprout, TrendingUp, CheckCircle,
  AlertCircle, Calendar, FileText, Settings, Smartphone, Tablet
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5050';
const DEFAULT_WILSY_LOGO = '/src/assets/logo/wilsy.jpeg';

const LogisticsDashboard = ({ onLogout, tenantConfig, roleView = 'OPERATIONS_VIEW' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

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
      customCSS: branding.customCSS || ''
    };
  }, [tenantConfig]);

  const features = useMemo(() => ({
    advancedTracking: tenantConfig?.features?.advancedValidation || true,
    crmModule: tenantConfig?.features?.bulkValidation || true,
    analyticsModule: tenantConfig?.features?.complianceReports || true,
    whiteLabel: tenantConfig?.features?.whiteLabel || false,
    multiRegion: tenantConfig?.features?.multiRegion || false
  }), [tenantConfig]);

  const [metrics, setMetrics] = useState(null);
  const [shipments, setShipments] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [agriShipments, setAgriShipments] = useState([]);
  const [partsOrders, setPartsOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [ports, setPorts] = useState([]);
  const [borderCrossings, setBorderCrossings] = useState([]);
  const [crmActivities, setCrmActivities] = useState([]);

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

  const loadLogisticsData = useCallback(async () => {
    try {
      setError(null);

      const [
        metricsData,
        shipmentsData,
        vehiclesData,
        agriData,
        partsData,
        customersData,
        routesData,
        portsData,
        bordersData,
        alertsData,
        crmData
      ] = await Promise.allSettled([
        fetchAPI('/api/logistics/metrics'),
        fetchAPI('/api/logistics/shipments'),
        fetchAPI('/api/logistics/vehicles'),
        fetchAPI('/api/logistics/agri'),
        fetchAPI('/api/logistics/parts'),
        fetchAPI('/api/crm/customers'),
        fetchAPI('/api/logistics/routes'),
        fetchAPI('/api/logistics/ports'),
        fetchAPI('/api/logistics/borders'),
        fetchAPI('/api/logistics/alerts'),
        fetchAPI('/api/crm/activities')
      ]);

      if (metricsData.status === 'fulfilled' && metricsData.value) setMetrics(metricsData.value);
      if (shipmentsData.status === 'fulfilled' && shipmentsData.value) setShipments(Array.isArray(shipmentsData.value) ? shipmentsData.value : shipmentsData.value.data || []);
      if (vehiclesData.status === 'fulfilled' && vehiclesData.value) setVehicles(Array.isArray(vehiclesData.value) ? vehiclesData.value : vehiclesData.value.data || []);
      if (agriData.status === 'fulfilled' && agriData.value) setAgriShipments(Array.isArray(agriData.value) ? agriData.value : agriData.value.data || []);
      if (partsData.status === 'fulfilled' && partsData.value) setPartsOrders(Array.isArray(partsData.value) ? partsData.value : partsData.value.data || []);
      if (customersData.status === 'fulfilled' && customersData.value) setCustomers(Array.isArray(customersData.value) ? customersData.value : customersData.value.data || []);
      if (routesData.status === 'fulfilled' && routesData.value) setRoutes(Array.isArray(routesData.value) ? routesData.value : routesData.value.data || []);
      if (portsData.status === 'fulfilled' && portsData.value) setPorts(Array.isArray(portsData.value) ? portsData.value : portsData.value.data || []);
      if (bordersData.status === 'fulfilled' && bordersData.value) setBorderCrossings(Array.isArray(bordersData.value) ? bordersData.value : bordersData.value.data || []);
      if (alertsData.status === 'fulfilled' && alertsData.value) setAlerts(Array.isArray(alertsData.value) ? alertsData.value : alertsData.value.data || []);
      if (crmData.status === 'fulfilled' && crmData.value) setCrmActivities(Array.isArray(crmData.value) ? crmData.value : crmData.value.data || []);

      setLastUpdated(new Date());
    } catch (err) {
      console.error('[LOGISTICS] Error loading data:', err);
      setError(err.message || 'Failed to load logistics data');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [fetchAPI]);

  useEffect(() => { loadLogisticsData(); }, [loadLogisticsData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadLogisticsData();
  };

  const getStatusColor = (status) => {
    if (!status) return 'text-stone-400';
    switch (status.toUpperCase()) {
      case 'IN_TRANSIT': return 'text-blue-400 bg-blue-950/30';
      case 'ARRIVED': return 'text-emerald-400 bg-emerald-950/30';
      case 'DELIVERED': return 'text-emerald-400 bg-emerald-950/30';
      case 'CUSTOMS_HOLD': return 'text-yellow-400 bg-yellow-950/30';
      case 'LOADING': return 'text-purple-400 bg-purple-950/30';
      case 'CUSTOMS_CLEARANCE': return 'text-orange-400 bg-orange-950/30';
      case 'PORT_ARRIVED': return 'text-cyan-400 bg-cyan-950/30';
      default: return 'text-stone-400';
    }
  };

  const getSeverityColor = (severity) => {
    if (!severity) return 'text-stone-400';
    switch (severity.toUpperCase()) {
      case 'CRITICAL': return 'text-red-400';
      case 'WARNING': return 'text-yellow-400';
      case 'INFO': return 'text-blue-400';
      default: return 'text-stone-400';
    }
  };

  const filteredShipments = useMemo(() => {
    if (!searchTerm) return shipments;
    const term = searchTerm.toLowerCase();
    return shipments.filter(s =>
      (s.id && s.id.toLowerCase().includes(term)) ||
      (s.customer && s.customer.toLowerCase().includes(term)) ||
      (s.reference && s.reference.toLowerCase().includes(term))
    );
  }, [shipments, searchTerm]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-yellow-500 animate-spin mx-auto mb-4" />
          <p className="text-stone-500 text-xs">Loading WILSY OS Logistics Suite...</p>
          <p className="text-stone-600 text-[9px] mt-2">Fetching live data from {API_BASE_URL}</p>
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
            {tenantBranding.logo !== DEFAULT_WILSY_LOGO ? (
              <img src={tenantBranding.logo} alt="Tenant Logo" className="w-8 h-8 object-contain" />
            ) : (
              <Ship className="w-8 h-8 text-yellow-500" />
            )}
            <h1 className="text-2xl font-black text-white">LOGISTICS <span className="text-yellow-500">DASHBOARD</span></h1>
            <div className="px-2 py-1 bg-yellow-500/20 border border-yellow-500/50 rounded-full flex items-center gap-1">
              <Globe size={10} className="text-yellow-500" />
              <span className="text-[9px] text-yellow-400 font-black">{tenantConfig?.name || 'ENTERPRISE'} - LIVE DATA</span>
            </div>
          </div>
          <p className="text-stone-500 text-xs mt-1">Real-time logistics • Live API integration • No hardcoded data</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[8px] text-stone-600">Last sync: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}</span>
            <Target size={8} className="text-yellow-500" />
          </div>
        </div>
        <div className="flex gap-3">
          <button onClick={handleRefresh} disabled={isRefreshing} className="px-3 py-2 bg-stone-800 text-white text-xs rounded-md flex items-center gap-2 hover:bg-stone-700">
            <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            {isRefreshing ? 'SYNCING...' : 'SYNC NOW'}
          </button>
          <button className="px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md flex items-center gap-2">
            <Plus size={14} /> NEW SHIPMENT
          </button>
          <button onClick={onLogout} className="px-4 py-2 border border-red-800 text-red-400 text-xs font-black rounded-md">EXIT</button>
        </div>
      </div>

      {error && (
        <div className="bg-red-950/30 border border-red-800 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-red-500" />
            <p className="text-red-400 text-sm">{error}</p>
            <button onClick={loadLogisticsData} className="ml-auto text-red-400 text-xs underline">RETRY</button>
          </div>
        </div>
      )}

      {/* PRIMARY KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Ship size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">ACTIVE SHIPMENTS</span></div>
          <p className="text-2xl font-black text-white">{metrics?.activeShipments ?? shipments.length}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Clock size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">ON-TIME DELIVERY</span></div>
          <p className="text-2xl font-black text-emerald-400">{metrics?.onTimeDelivery ?? '--'}%</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Package size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">PENDING CUSTOMS</span></div>
          <p className="text-2xl font-black text-yellow-400">{metrics?.pendingCustoms ?? '--'}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><AlertTriangle size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">DELAYED</span></div>
          <p className="text-2xl font-black text-red-400">{metrics?.delayed ?? '--'}</p>
        </div>
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><DollarSign size={14} className="text-yellow-500" /><span className="text-stone-400 text-[10px]">TOTAL VALUE</span></div>
          <p className="text-2xl font-black text-white">R{((metrics?.totalValue ?? 0) / 1000000).toFixed(1)}M</p>
        </div>
      </div>

      {/* SECONDARY KPIs */}
      <div className="grid grid-cols-6 gap-3 mb-6">
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Car size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">VEHICLES SHIPPED</p><p className="text-xl font-black text-white">{metrics?.vehiclesShipped ?? vehicles.length}</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Sprout size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">AGRI VOLUME (MT)</p><p className="text-xl font-black text-white">{metrics?.agriVolume ?? '--'}</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Wrench size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">PARTS ORDERS</p><p className="text-xl font-black text-white">{metrics?.partsOrders ?? partsOrders.length}</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Globe size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">CROSS-BORDER</p><p className="text-xl font-black text-white">{metrics?.crossBorderShipments ?? '--'}</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><Users size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">CUSTOMER SAT.</p><p className="text-xl font-black text-emerald-400">{metrics?.customerSatisfaction ?? '--'}%</p></div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-2 text-center"><TrendingUp size={12} className="text-yellow-500 mx-auto mb-1" /><p className="text-stone-400 text-[8px]">PROFIT MARGIN</p><p className="text-xl font-black text-emerald-400">{metrics?.profitMargin ?? '--'}%</p></div>
      </div>

      {/* TABS */}
      <div className="flex gap-1 border-b border-stone-800 mb-6">
        {[
          { id: 'overview', label: 'OVERVIEW', icon: Ship },
          { id: 'shipments', label: 'SHIPMENTS', icon: Package },
          { id: 'vehicles', label: 'VEHICLES', icon: Car },
          { id: 'agri', label: 'AGRI-BUSINESS', icon: Sprout },
          { id: 'crm', label: 'CRM (LIVE)', icon: Users },
          { id: 'routes', label: 'ROUTES & PORTS', icon: Map }
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2 text-xs font-black uppercase transition-all ${activeTab === tab.id ? 'border-b-2 border-yellow-500 text-yellow-500' : 'text-stone-500 hover:text-stone-300'}`}>
            <tab.icon size={12} /> {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div>
          <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden mb-6">
            <div className="px-5 py-3 border-b border-yellow-900/30 flex justify-between items-center">
              <h3 className="text-yellow-500 text-xs font-black uppercase flex items-center gap-2"><Package size={12} /> ACTIVE SHIPMENTS (LIVE)</h3>
              <div className="flex-1 max-w-xs relative">
                <Search size={12} className="absolute left-2 top-1/2 transform -translate-y-1/2 text-stone-500" />
                <input type="text" placeholder="Search shipments..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full pl-7 pr-2 py-1 bg-black border border-stone-700 rounded text-white text-xs" />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-stone-800/50">
                  <tr><th className="px-4 py-2 text-left text-stone-400 text-[10px]">ID</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Reference</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Customer</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Origin → Destination</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Status</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">ETA</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Value</th></tr>
                </thead>
                <tbody>
                  {filteredShipments.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-8 text-stone-500 text-xs">No shipments found</td></tr>
                  ) : (
                    filteredShipments.map((shipment) => (
                      <tr key={shipment.id} className="border-t border-stone-800 hover:bg-stone-800/30 cursor-pointer" onClick={() => setSelectedShipment(shipment)}>
                        <td className="px-4 py-2 text-white text-xs font-mono">{shipment.id}</td>
                        <td className="px-4 py-2 text-yellow-400 text-xs font-mono">{shipment.reference}</td>
                        <td className="px-4 py-2 text-white text-xs">{shipment.customer}</td>
                        <td className="px-4 py-2 text-white text-xs">{shipment.origin} → {shipment.destination}</td>
                        <td className="px-4 py-2"><span className={`px-2 py-1 rounded-full text-[9px] font-bold ${getStatusColor(shipment.status)}`}>{shipment.status}</span></td>
                        <td className="px-4 py-2 text-white text-xs">{shipment.eta}</td>
                        <td className="px-4 py-2 text-emerald-400 text-xs">R{((shipment.value || 0) / 1000000).toFixed(1)}M</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
              <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Anchor size={12} /> PORT STATUS</h3>
              {ports.length === 0 ? <p className="text-stone-500 text-xs text-center py-4">No port data available</p> : ports.map((port, idx) => (
                <div key={idx} className="bg-black/30 rounded p-2 mb-2">
                  <div className="flex justify-between"><p className="text-white text-sm font-medium">{port.name}</p><span className={`text-[9px] px-2 py-0.5 rounded-full ${port.congestion === 'HIGH' ? 'bg-red-500/20 text-red-400' : port.congestion === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-emerald-500/20 text-emerald-400'}`}>{port.congestion}</span></div>
                  <div className="flex justify-between text-[10px] mt-1"><span className="text-stone-400">Wait: {port.waitingTime}hrs</span><span className="text-stone-400">Vessels: {port.vesselsInPort}</span><span className="text-emerald-400">Productivity: {port.productivity}%</span></div>
                </div>
              ))}
            </div>
            <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
              <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Navigation size={12} /> BORDER CROSSINGS</h3>
              {borderCrossings.length === 0 ? <p className="text-stone-500 text-xs text-center py-4">No border data available</p> : borderCrossings.map((border, idx) => (
                <div key={idx} className="bg-black/30 rounded p-2 mb-2">
                  <div className="flex justify-between"><p className="text-white text-sm font-medium">{border.name}</p><span className={`text-[9px] px-2 py-0.5 rounded-full ${border.status === 'CONGESTED' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>{border.status}</span></div>
                  <div className="flex justify-between text-[10px] mt-1"><span className="text-stone-400">Wait: {border.waitTime}hrs</span><span className="text-stone-400">Clearance: {border.clearanceTime}hrs</span></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* VEHICLES TAB */}
      {activeTab === 'vehicles' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-yellow-900/30"><h3 className="text-yellow-500 text-xs font-black uppercase flex items-center gap-2"><Car size={12} /> VEHICLE INVENTORY (LIVE)</h3></div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-stone-800/50"><tr><th className="px-4 py-2 text-left text-stone-400 text-[10px]">VIN</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Make/Model</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Year</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Customer</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Status</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">ETA</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Value</th></tr></thead>
              <tbody>
                {vehicles.length === 0 ? (<tr><td colSpan={7} className="text-center py-8 text-stone-500 text-xs">No vehicle data available</td></tr>) : vehicles.map((vehicle) => (
                  <tr key={vehicle.id} className="border-t border-stone-800">
                    <td className="px-4 py-2 text-yellow-400 text-[9px] font-mono">{vehicle.vin}</td>
                    <td className="px-4 py-2 text-white text-xs">{vehicle.make} {vehicle.model}</td>
                    <td className="px-4 py-2 text-white text-xs">{vehicle.year}</td>
                    <td className="px-4 py-2 text-white text-xs">{vehicle.customer}</td>
                    <td className="px-4 py-2"><span className={`px-2 py-1 rounded-full text-[9px] font-bold ${getStatusColor(vehicle.status)}`}>{vehicle.status}</span></td>
                    <td className="px-4 py-2 text-white text-xs">{vehicle.eta}</td>
                    <td className="px-4 py-2 text-emerald-400 text-xs">R{((vehicle.value || 0) / 1000000).toFixed(1)}M</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* AGRI TAB */}
      {activeTab === 'agri' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Sprout size={12} /> AGRICULTURAL EXPORTS (LIVE)</h3>
          <div className="grid grid-cols-3 gap-4">
            {agriShipments.length === 0 ? <p className="text-stone-500 text-xs text-center py-4 col-span-3">No agricultural data available</p> : agriShipments.map((agri, idx) => (
              <div key={idx} className="bg-black/30 rounded-lg p-3">
                <p className="text-white font-bold">{agri.commodity}</p>
                <p className="text-2xl font-black text-white">{agri.volume?.toLocaleString() || 0} kg</p>
                <p className="text-emerald-400 text-sm">R{((agri.value || 0) / 1000000).toFixed(1)}M</p>
                <div className="flex justify-between mt-2"><span className="text-stone-500 text-[9px]">{agri.origin} → {agri.destination}</span><span className={`text-[9px] ${getStatusColor(agri.status)}`}>{agri.status}</span></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CRM TAB */}
      {activeTab === 'crm' && (
        <div>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4 text-center"><Users size={20} className="text-yellow-500 mx-auto mb-2" /><p className="text-2xl font-black text-white">{customers.length}</p><p className="text-stone-400 text-[10px]">ACTIVE CUSTOMERS (LIVE)</p></div>
            <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4 text-center"><DollarSign size={20} className="text-yellow-500 mx-auto mb-2" /><p className="text-2xl font-black text-emerald-400">R{(customers.reduce((sum, c) => sum + (c.ltv || 0), 0) / 1000000).toFixed(1)}M</p><p className="text-stone-400 text-[10px]">TOTAL LTV (LIVE)</p></div>
            <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-4 text-center"><Brain size={20} className="text-yellow-500 mx-auto mb-2" /><p className="text-2xl font-black text-white">AI-POWERED</p><p className="text-stone-400 text-[10px]">Predictive Intelligence</p></div>
          </div>
          <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-yellow-900/30"><h3 className="text-yellow-500 text-xs font-black uppercase flex items-center gap-2"><Users size={12} /> 360° CUSTOMER VIEW (LIVE FROM DB)</h3></div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-stone-800/50"><tr><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Customer</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Type</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Region</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">LTV</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Status</th><th className="px-4 py-2 text-left text-stone-400 text-[10px]">Action</th></tr></thead>
                <tbody>
                  {customers.length === 0 ? (<tr><td colSpan={6} className="text-center py-8 text-stone-500 text-xs">No customer data available. Add customers via CRM.</td></tr>) : customers.map((customer) => (
                    <tr key={customer.id} className="border-t border-stone-800 hover:bg-stone-800/30 cursor-pointer" onClick={() => setSelectedCustomer(customer)}>
                      <td className="px-4 py-2"><div><p className="text-white text-sm font-medium">{customer.name}</p><p className="text-stone-500 text-[8px]">{customer.company}</p></div></td>
                      <td className="px-4 py-2"><span className="text-[9px] px-2 py-0.5 bg-stone-800 rounded-full">{customer.type || 'STANDARD'}</span></td>
                      <td className="px-4 py-2 text-white text-xs">{customer.region || 'N/A'}</td>
                      <td className="px-4 py-2 text-emerald-400 text-xs">R{((customer.ltv || 0) / 1000000).toFixed(1)}M</td>
                      <td className="px-4 py-2"><span className={`text-[9px] px-2 py-0.5 rounded-full ${customer.status === 'VIP' ? 'bg-yellow-500/20 text-yellow-400' : customer.status === 'ENTERPRISE' ? 'bg-purple-500/20 text-purple-400' : 'bg-emerald-500/20 text-emerald-400'}`}>{customer.status || 'ACTIVE'}</span></td>
                      <td className="px-4 py-2"><button className="text-yellow-500 text-[9px]">VIEW →</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ROUTES TAB */}
      {activeTab === 'routes' && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><Map size={12} /> EAST AFRICAN CORRIDORS (LIVE)</h3>
          <div className="grid grid-cols-3 gap-4">
            {routes.length === 0 ? <p className="text-stone-500 text-xs text-center py-4 col-span-3">No route data available</p> : routes.map((route) => (
              <div key={route.id} className="bg-black/30 rounded-lg p-3">
                <p className="text-white font-bold">{route.name}</p>
                <p className="text-stone-400 text-[9px]">{route.origin} → {route.destination}</p>
                <div className="mt-2 space-y-1"><p className="text-[9px]"><span className="text-stone-500">Distance:</span> {route.distance} km</p><p className="text-[9px]"><span className="text-stone-500">Transit:</span> {route.transitTime} hrs</p><p className="text-[9px]"><span className="text-stone-500">Borders:</span> {route.borderPosts?.join(', ') || 'N/A'}</p></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MODALS */}
      {selectedShipment && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-stone-900 border border-yellow-900/30 rounded-xl max-w-lg w-full">
            <div className="flex justify-between items-center p-4 border-b border-yellow-900/30"><h2 className="text-white font-black text-lg">Shipment Details</h2><button onClick={() => setSelectedShipment(null)} className="text-stone-400 hover:text-white"><XCircle size={20} /></button></div>
            <div className="p-5"><div className="space-y-3"><div><p className="text-stone-400 text-[10px]">Shipment ID</p><p className="text-white font-mono">{selectedShipment.id}</p></div><div><p className="text-stone-400 text-[10px]">Reference</p><p className="text-yellow-400 font-mono">{selectedShipment.reference}</p></div><div><p className="text-stone-400 text-[10px]">Customer</p><p className="text-white text-lg font-bold">{selectedShipment.customer}</p></div><div><p className="text-stone-400 text-[10px]">Status</p><p className={`font-bold ${getStatusColor(selectedShipment.status)}`}>{selectedShipment.status}</p></div><div><p className="text-stone-400 text-[10px]">Value</p><p className="text-emerald-400 text-xl font-bold">R{((selectedShipment.value || 0) / 1000000).toFixed(1)}M</p></div><div className="flex gap-3 pt-4"><button className="flex-1 px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md">TRACK LIVE</button><button className="flex-1 px-4 py-2 border border-stone-700 text-stone-400 text-xs rounded-md">CLOSE</button></div></div></div>
          </div>
        </div>
      )}

      {selectedCustomer && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-stone-900 border border-yellow-900/30 rounded-xl max-w-md w-full">
            <div className="flex justify-between items-center p-4 border-b border-yellow-900/30"><h2 className="text-white font-black text-lg">Customer Profile</h2><button onClick={() => setSelectedCustomer(null)} className="text-stone-400 hover:text-white"><XCircle size={20} /></button></div>
            <div className="p-5"><div className="space-y-3"><div><p className="text-stone-400 text-[10px]">Name</p><p className="text-white text-lg font-bold">{selectedCustomer.name}</p></div><div><p className="text-stone-400 text-[10px]">Company</p><p className="text-white">{selectedCustomer.company}</p></div>{selectedCustomer.email && <div><p className="text-stone-400 text-[10px]">Email</p><p className="text-white">{selectedCustomer.email}</p></div>}{selectedCustomer.phone && <div><p className="text-stone-400 text-[10px]">Phone</p><p className="text-white">{selectedCustomer.phone}</p></div>}<div><p className="text-stone-400 text-[10px]">Lifetime Value</p><p className="text-emerald-400 text-xl font-bold">R{((selectedCustomer.ltv || 0) / 1000000).toFixed(1)}M</p></div><div className="flex gap-3 pt-4"><button className="flex-1 px-4 py-2 bg-yellow-600 text-black text-xs font-black rounded-md">SEND QUOTE</button><button className="flex-1 px-4 py-2 border border-stone-700 text-stone-400 text-xs rounded-md">CLOSE</button></div></div></div>
          </div>
        </div>
      )}

      {/* ALERTS */}
      {alerts.length > 0 && (
        <div className="bg-stone-900/30 border border-yellow-900/30 rounded-xl p-5 mt-6">
          <h3 className="text-yellow-500 text-xs font-black uppercase mb-4 flex items-center gap-2"><AlertCircle size={12} /> SYSTEM ALERTS</h3>
          <div className="space-y-2">{alerts.map((alert) => (
            <div key={alert.id} className={`flex justify-between items-center p-2 bg-black/30 rounded border-l-2 ${alert.severity === 'CRITICAL' ? 'border-red-500' : alert.severity === 'WARNING' ? 'border-yellow-500' : 'border-blue-500'}`}>
              <div><p className={`text-[10px] font-bold ${getSeverityColor(alert.severity)}`}>{alert.severity} • Impact: {alert.impact}</p><p className="text-white text-[10px]">{alert.message}</p></div>
              <div className="text-right"><p className="text-stone-500 text-[8px]">{alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Unknown'}</p>{!alert.resolved && <button className="text-yellow-500 text-[8px] mt-1">ACKNOWLEDGE</button>}</div>
            </div>
          ))}</div>
        </div>
      )}

      {/* FOOTER */}
      <div className="mt-6 pt-4 border-t border-stone-800 text-center">
        <div className="flex justify-center items-center gap-4 text-[8px] text-stone-500"><span className="flex items-center gap-1"><Shield size={10} className="text-emerald-400" /> Live API</span><span className="flex items-center gap-1"><Lock size={10} className="text-emerald-400" /> Multi-tenant</span><span className="flex items-center gap-1"><Cloud size={10} className="text-emerald-400" /> Real-time Sync</span><span className="flex items-center gap-1"><Zap size={10} className="text-yellow-500" /> No Hardcoded Data</span></div>
        <p className="text-stone-600 text-[7px] mt-2">WILSY OS v7.0.0-LIVE-DATA | All data fetched from live API endpoints | No placeholders</p>
      </div>
    </div>
  );
};

export default LogisticsDashboard;
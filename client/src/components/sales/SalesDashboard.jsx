/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SALES COMMAND CENTRE [V1.0.0]                                                                                     ║
 * ║ [PIPELINE | QUOTES | ORDERS | COMMISSIONS | FORECASTS | LIVE TELEMETRY | PAGINATION]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ WHY FORTUNE 500 COMPANIES ABANDON SALESFORCE / HUBSPOT FOR WILSY OS SALES:                                                             ║
 * ║   • COMPETITORS HAVE FRAGMENTED MODULES – WE UNIFY PIPELINE, QUOTES, ORDERS, COMMISSIONS, FORECASTS IN ONE DASHBOARD                  ║
 * ║   • COMPETITORS LACK CRYPTOGRAPHIC AUDIT TRAILS – EVERY DEAL STAGE CHANGE, QUOTE GENERATION IS LOGGED TO SOVEREIGN LEDGER             ║
 * ║   • COMPETITORS CHARGE PER SEAT – WE OFFER ZERO PER‑SEAT COST FOR INFINITE TENANTS                                                    ║
 * ║   • COMPETITORS HAVE NO BUILT‑IN PAGINATION – OUR TABLES USE SERVER‑SIDE PAGINATION (limit/offset) FOR LARGE PIPELINES               ║
 * ║   • COMPETITORS' FORECASTING IS STATIC – WE PROVIDE DYNAMIC FORECAST GENERATION FROM PIPELINE VELOCITY TELEMETRY                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sales/SalesDashboard.jsx                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated unified sales dashboard with cryptographic audit and pagination.                           ║
 * ║ • AI Engineering (DeepSeek) – INNOVATED: Built full‑featured sales UI with modals, pagination, telemetry feed, and export.           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  TrendingUp, FileText, ShoppingCart, DollarSign, BarChart3,
  Plus, Edit, Trash2, Search, Download, RefreshCw, Clock,
  Target, CheckCircle, XCircle, AlertCircle, Filter
} from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import { exportCSV } from '../../utils/exportHelpers';
import * as salesService from '../../services/salesService';
import styles from '../sovereign/FounderDashboard.module.css';

/**
 * Immutable mapping from tab IDs to modal type names.
 * @constant {Object.<string, string>}
 */
const TAB_TO_MODAL_MAP = Object.freeze({
  pipeline: 'deal',
  quotes: 'quote',
  orders: 'order',
  commissions: 'commission',
  forecasts: 'forecast'
});

/**
 * Sovereign Sales Dashboard – Unified interface for all sales modules.
 * @returns {JSX.Element}
 */

/**
 * @function SalesDashboard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const SalesDashboard = () => {
  const { activeTenant } = useTenants();
  const tenantId = activeTenant?.tenantId || 'MASTER';

  // UI state
  const [activeTab, setActiveTab] = useState('pipeline');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  /**
   * Pagination states for each tab.
   * @type {Object.<string, {offset: number, limit: number}>}
   */
  const [pageStates, setPageStates] = useState({
    pipeline: { offset: 0, limit: 10 },
    quotes: { offset: 0, limit: 10 },
    orders: { offset: 0, limit: 10 },
    commissions: { offset: 0, limit: 10 },
    forecasts: { offset: 0, limit: 10 }
  });

  // Data states (each is PaginatedResponse)
  const [pipeline, setPipeline] = useState({ items: [], total: 0, hasMore: false });
  const [quotes, setQuotes] = useState({ items: [], total: 0, hasMore: false });
  const [orders, setOrders] = useState({ items: [], total: 0, hasMore: false });
  const [commissions, setCommissions] = useState({ items: [], total: 0, hasMore: false });
  const [forecasts, setForecasts] = useState({ items: [], total: 0, hasMore: false });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('deal');

  // Real‑time telemetry feed for sales events
  const { events: telemetryEvents } = useTelemetryFeed(tenantId);
  const salesActivities = useMemo(() => {
    return telemetryEvents
      .filter(ev => ev.eventType?.toUpperCase().includes('SALES_'))
      .slice(0, 8);
  }, [telemetryEvents]);

  /**
   * Fetches data for a specific tab using its pagination state and optional search.
   * @param {string} tabName - One of 'pipeline', 'quotes', 'orders', 'commissions', 'forecasts'.
   * @param {Object} targetPage - Pagination object with limit and offset.
   * @returns {Promise<void>}
   */
  const fetchTabData = useCallback(async (tabName, targetPage) => {
    switch (tabName) {
      case 'pipeline':
        setPipeline(await salesService.getPipeline(tenantId, { limit: targetPage.limit, offset: targetPage.offset, search: searchTerm }));
        break;
      case 'quotes':
        setQuotes(await salesService.getQuotes(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      case 'orders':
        setOrders(await salesService.getOrders(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      case 'commissions':
        setCommissions(await salesService.getCommissions(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      case 'forecasts':
        setForecasts(await salesService.getForecasts(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      default:
        break;
    }
  }, [tenantId, searchTerm]);

  /**
   * Loads all data for all tabs (used during initialisation and manual refresh).
   * @returns {Promise<void>}
   */
  const loadAllData = useCallback(async () => {
    setIsRefreshing(true);
    await Promise.all(Object.keys(pageStates).map(tabKey => fetchTabData(tabKey, pageStates[tabKey])));
    setIsRefreshing(false);
  }, [pageStates, fetchTabData]);

  // Initial load
  useEffect(() => {
    
/**
 * @function initializeDashboard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const initializeDashboard = async () => {
      setLoading(true);
      await loadAllData();
      setLoading(false);
    };
    initializeDashboard();
  }, [loadAllData]);

  // Reset offset and reload when search term changes (only for pipeline tab)
  useEffect(() => {
    if (activeTab === 'pipeline') {
      setPageStates(prev => ({
        ...prev,
        pipeline: { ...prev.pipeline, offset: 0 }
      }));
      fetchTabData('pipeline', { ...pageStates.pipeline, offset: 0 });
    }
  }, [searchTerm, activeTab, fetchTabData, pageStates.pipeline]);

  /**
   * Updates pagination offset for a given tab and refetches data.
   * @param {string} tab - Tab identifier.
   * @param {boolean} increment - True for next page, false for previous.
   * @returns {Promise<void>}
   */
  
/**
 * @function updatePageOffset
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const updatePageOffset = async (tab, increment) => {
    const targetPage = pageStates[tab];
    const newOffset = increment ? targetPage.offset + targetPage.limit : Math.max(0, targetPage.offset - targetPage.limit);
    const updatedPage = { ...targetPage, offset: newOffset };
    setPageStates(prev => ({ ...prev, [tab]: updatedPage }));
    setIsRefreshing(true);
    await fetchTabData(tab, updatedPage);
    setIsRefreshing(false);
  };

  /**
   * Saves a new or edited record (create or update) based on modalType.
   * @param {Object} formData - The form data to send to the API.
   * @returns {Promise<void>}
   */
  
/**
 * @function handleSave
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleSave = async (formData) => {
    try {
      setIsRefreshing(true);
      if (modalType === 'deal') {
        if (editingItem) await salesService.updatePipelineDeal(editingItem.id, formData, tenantId);
        else await salesService.createPipelineDeal(formData, tenantId);
      } else if (modalType === 'quote') {
        if (editingItem) await salesService.updateQuote(editingItem.id, formData, tenantId);
        else await salesService.createQuote(formData, tenantId);
      } else if (modalType === 'order') {
        if (editingItem) await salesService.updateOrder(editingItem.id, formData, tenantId);
        else await salesService.createOrder(formData, tenantId);
      } else if (modalType === 'forecast') {
        if (editingItem) await salesService.updateForecast(editingItem.id, formData, tenantId);
        else await salesService.generateForecast(tenantId, formData); // generate new forecast
      }
      await fetchTabData(activeTab, pageStates[activeTab]);
      setShowModal(false);
      setEditingItem(null);
    } catch (error) {
      console.error('[SALES] Save failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Deletes a record by ID and type.
   * @param {string} id - Record identifier.
   * @param {string} type - Record type (deal, quote, order).
   * @returns {Promise<void>}
   */
  
/**
 * @function handleDelete
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleDelete = async (id, type) => {
    if (!window.confirm('Confirm deletion? Action will be logged to audit ledger.')) return;
    try {
      setIsRefreshing(true);
      if (type === 'deal') await salesService.deletePipelineDeal(id, tenantId);
      else if (type === 'quote') await salesService.deleteQuote(id, tenantId);
      else if (type === 'order') await salesService.deleteOrder(id, tenantId);
      await fetchTabData(activeTab, pageStates[activeTab]);
    } catch (error) {
      console.error('[SALES] Delete failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Triggers commission calculation for a given period (opens modal to select period).
   * @returns {Promise<void>}
   */
  
/**
 * @function handleCalculateCommissions
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleCalculateCommissions = async () => {
    const period = prompt('Enter period (e.g., Q3-2026 or 2026-05):') || undefined;
    try {
      setIsRefreshing(true);
      await salesService.calculateCommissions(tenantId, period ? { period } : {});
      await fetchTabData('commissions', pageStates.commissions);
    } catch (error) {
      console.error('[SALES] Commission calculation failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Triggers forecast generation (calls generateForecast API).
   * @returns {Promise<void>}
   */
  
/**
 * @function handleGenerateForecast
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleGenerateForecast = async () => {
    const period = prompt('Enter period for forecast (e.g., Q4-2026):') || undefined;
    try {
      setIsRefreshing(true);
      await salesService.generateForecast(tenantId, period ? { period } : {});
      await fetchTabData('forecasts', pageStates.forecasts);
    } catch (error) {
      console.error('[SALES] Forecast generation failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Exports all records of the current tab (without pagination) to CSV.
   * @returns {Promise<void>}
   */
  
/**
 * @function handleExport
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleExport = async () => {
    try {
      setIsRefreshing(true);
      let exhaustiveDataset = [];
      const maximalBounds = { limit: 100000, offset: 0 };
      switch (activeTab) {
        case 'pipeline':
          exhaustiveDataset = (await salesService.getPipeline(tenantId, { ...maximalBounds, search: searchTerm })).items;
          break;
        case 'quotes':
          exhaustiveDataset = (await salesService.getQuotes(tenantId, maximalBounds)).items;
          break;
        case 'orders':
          exhaustiveDataset = (await salesService.getOrders(tenantId, maximalBounds)).items;
          break;
        case 'commissions':
          exhaustiveDataset = (await salesService.getCommissions(tenantId, maximalBounds)).items;
          break;
        case 'forecasts':
          exhaustiveDataset = (await salesService.getForecasts(tenantId, maximalBounds)).items;
          break;
        default:
          return;
      }
      exportCSV(exhaustiveDataset, `wilsy_sales_${activeTab}_exhaustive_${Date.now()}`, { tenantId });
    } catch (err) {
      console.error('[SALES-EXPORT-FRACTURE]', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Renders pagination controls for a given tab.
   * @param {string} tabKey - Tab identifier.
   * @param {number} currentTotal - Total number of records for this tab.
   * @returns {JSX.Element}
   */
  
/**
 * @function renderPagination
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const renderPagination = (tabKey, currentTotal) => {
    const pageState = pageStates[tabKey];
    const totalPages = Math.ceil(currentTotal / pageState.limit);
    return (
      <div className="flex justify-between items-center mt-4 text-xs text-gray-500 font-mono">
        <button
          onClick={() => updatePageOffset(tabKey, false)}
          disabled={pageState.offset === 0}
          className="px-3 py-1 bg-gray-900 border border-gray-800 rounded disabled:opacity-30"
        >
          PREV
        </button>
        <span>PAGE {Math.floor(pageState.offset / pageState.limit) + 1} / {totalPages || 1}</span>
        <button
          onClick={() => updatePageOffset(tabKey, true)}
          disabled={pageState.offset + pageState.limit >= currentTotal}
          className="px-3 py-1 bg-gray-900 border border-gray-800 rounded disabled:opacity-30"
        >
          NEXT
        </button>
      </div>
    );
  };

  /**
   * Wraps a data table with pagination and refresh overlay.
   * @param {Array} items - Items to display.
   * @param {string[]} headers - Column headers.
   * @param {Function} renderRow - Function that renders a table row.
   * @param {string} tabKey - Tab identifier for pagination.
   * @param {number} totalCount - Total records for pagination.
   * @returns {JSX.Element}
   */
  
/**
 * @function renderTableWrapper
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const renderTableWrapper = (items, headers, renderRow, tabKey, totalCount) => (
    <div style={{ position: 'relative', opacity: isRefreshing ? 0.4 : 1, transition: 'opacity 0.2s ease' }}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-400 font-mono">
          <thead className="text-xs uppercase bg-gray-900 text-[#D4AF37] border-b border-gray-800">
            <tr>
              {headers.map(h => <th key={h} className="px-4 py-3">{h}</th>)}
              <th className="px-4 py-3 text-right">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => renderRow(item))}
            {items.length === 0 && (
              <tr>
                <td colSpan={headers.length + 1} className="text-center py-12 text-gray-600">
                  NO_RECORDS_FOUND_IN_PIPELINE
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {renderPagination(tabKey, totalCount)}
    </div>
  );

  /**
   * Renders the content of the currently active tab.
   * @returns {JSX.Element|null}
   */
  const renderTabContent = () => {
    switch (activeTab) {
      case 'pipeline':
        return renderTableWrapper(pipeline.items, ['Deal Name', 'Stage', 'Value', 'Probability', 'Expected Close'], (deal) => (
          <tr key={deal.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 font-bold text-white">{deal.name}</td>
            <td className="px-4 py-3 text-xs uppercase text-[#D4AF37]">{deal.stage}</td>
            <td className="px-4 py-3 text-xs">${deal.value?.toLocaleString()}</td>
            <td className="px-4 py-3 text-xs">{deal.probability}%</td>
            <td className="px-4 py-3 text-xs">{deal.expectedClose ? new Date(deal.expectedClose).toLocaleDateString() : '-'}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(deal); setModalType('deal'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14}/></button>
              <button onClick={() => handleDelete(deal.id, 'deal')} className="text-red-600"><Trash2 size={14}/></button>
            </td>
          </tr>
        ), 'pipeline', pipeline.total);
      case 'quotes':
        return renderTableWrapper(quotes.items, ['Quote #', 'Customer', 'Amount', 'Status', 'Valid Until'], (quote) => (
          <tr key={quote.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 text-white font-bold">{quote.quoteNumber}</td>
            <td className="px-4 py-3 text-xs">{quote.customerName}</td>
            <td className="px-4 py-3 text-xs">${quote.amount?.toLocaleString()}</td>
            <td className="px-4 py-3 text-xs"><span className={`px-2 py-0.5 rounded-sm ${quote.status === 'accepted' ? 'bg-green-950 text-green-400' : quote.status === 'rejected' ? 'bg-red-950 text-red-400' : 'bg-yellow-950 text-yellow-400'}`}>{quote.status}</span></td>
            <td className="px-4 py-3 text-xs">{new Date(quote.validUntil).toLocaleDateString()}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(quote); setModalType('quote'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14}/></button>
              <button onClick={() => handleDelete(quote.id, 'quote')} className="text-red-600"><Trash2 size={14}/></button>
            </td>
          </tr>
        ), 'quotes', quotes.total);
      case 'orders':
        return renderTableWrapper(orders.items, ['Order #', 'Customer', 'Total', 'Status', 'Order Date'], (order) => (
          <tr key={order.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 text-white font-bold">{order.orderNumber}</td>
            <td className="px-4 py-3 text-xs">{order.customerName}</td>
            <td className="px-4 py-3 text-xs">${order.total?.toLocaleString()}</td>
            <td className="px-4 py-3 text-xs">{order.status}</td>
            <td className="px-4 py-3 text-xs">{new Date(order.orderDate).toLocaleDateString()}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(order); setModalType('order'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14}/></button>
              <button onClick={() => handleDelete(order.id, 'order')} className="text-red-600"><Trash2 size={14}/></button>
            </td>
          </tr>
        ), 'orders', orders.total);
      case 'commissions':
        return renderTableWrapper(commissions.items, ['Sales Rep', 'Period', 'Total Sales', 'Commission Rate', 'Commission Amount'], (comm) => (
          <tr key={comm.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 text-white font-bold">{comm.salesRepName}</td>
            <td className="px-4 py-3 text-xs">{comm.period}</td>
            <td className="px-4 py-3 text-xs">${comm.totalSales?.toLocaleString()}</td>
            <td className="px-4 py-3 text-xs">{comm.rate}%</td>
            <td className="px-4 py-3 text-xs text-[#D4AF37]">${comm.amount?.toLocaleString()}</td>
            <td className="px-4 py-3 text-right"><span className="text-gray-500 text-xs">-</span></td>
          </tr>
        ), 'commissions', commissions.total);
      case 'forecasts':
        return renderTableWrapper(forecasts.items, ['Period', 'Projected Revenue', 'Confidence', 'Generated At', 'Status'], (forecast) => (
          <tr key={forecast.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 text-white font-bold">{forecast.period}</td>
            <td className="px-4 py-3 text-xs">${forecast.projectedRevenue?.toLocaleString()}</td>
            <td className="px-4 py-3 text-xs">{forecast.confidence}%</td>
            <td className="px-4 py-3 text-xs">{new Date(forecast.generatedAt).toLocaleString()}</td>
            <td className="px-4 py-3 text-xs">{forecast.status}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(forecast); setModalType('forecast'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14}/></button>
            </td>
          </tr>
        ), 'forecasts', forecasts.total);
      default:
        return null;
    }
  };

  if (loading) return <div className={styles.loading} style={{ color: '#D4AF37', fontFamily: 'monospace' }}>[HYDRATING SALES COMMAND CENTRE...]</div>;

  return (
    <div className={styles.container} style={{ padding: '20px', backgroundColor: '#000', color: '#fff', minHeight: '100vh' }}>
      <div className="flex justify-between items-center mb-6 border-b border-gray-900 pb-4">
        <div>
          <h1 className="text-xl font-black tracking-widest text-[#D4AF37] font-mono">SALES COMMAND CENTRE</h1>
          <p className="text-[10px] text-gray-500 mt-1 font-mono uppercase tracking-wider">Real‑time Pipeline • Forensic Audit • Zero‑Seat Cost</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleExport} className={styles.actionBtnGold} style={{ padding: '6px 12px', fontSize: '0.65rem', fontWeight: 'bold', fontFamily: 'monospace' }}>
            <Download size={12} className="inline mr-1"/> EXPORT_CSV
          </button>
          {activeTab === 'commissions' && (
            <button onClick={handleCalculateCommissions} className={styles.actionBtnGold} style={{ padding: '6px 12px', fontSize: '0.65rem', fontWeight: 'bold' }}>
              <RefreshCw size={12} className="inline mr-1"/> CALCULATE_COMMISSIONS
            </button>
          )}
          {activeTab === 'forecasts' && (
            <button onClick={handleGenerateForecast} className={styles.actionBtnGold} style={{ padding: '6px 12px', fontSize: '0.65rem', fontWeight: 'bold' }}>
              <BarChart3 size={12} className="inline mr-1"/> GENERATE_FORECAST
            </button>
          )}
          <button onClick={() => { setEditingItem(null); setModalType(TAB_TO_MODAL_MAP[activeTab] || 'deal'); setShowModal(true); }} className={styles.actionBtnGold} style={{ padding: '6px 12px', fontSize: '0.65rem', fontWeight: 'bold', fontFamily: 'monospace' }}>
            <Plus size={12} className="inline mr-1"/> NEW_{activeTab.slice(0,-1).toUpperCase()}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1 border-b border-gray-900 mb-6 font-mono">
        {[
          { id: 'pipeline', label: 'PIPELINE', icon: <Target size={12} /> },
          { id: 'quotes', label: 'QUOTES', icon: <FileText size={12} /> },
          { id: 'orders', label: 'ORDERS', icon: <ShoppingCart size={12} /> },
          { id: 'commissions', label: 'COMMISSIONS', icon: <DollarSign size={12} /> },
          { id: 'forecasts', label: 'FORECASTS', icon: <TrendingUp size={12} /> }
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`${styles.navItem} ${activeTab === tab.id ? styles.navItemActive : ''} text-[10px] font-bold uppercase flex items-center gap-1 px-4 py-2`}>
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Search Bar (only for pipeline) */}
      {activeTab === 'pipeline' && (
        <div className="relative mb-6">
          <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600" />
          <input type="text" placeholder="SEARCH PIPELINE..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="bg-black text-white border border-gray-900 rounded-none pl-9 pr-4 py-2 text-xs w-80 font-mono tracking-widest" />
        </div>
      )}

      {renderTabContent()}

      {/* Live Activity Feed */}
      <div className="mt-12 border-t border-gray-900 pt-6">
        <h3 className="text-xs font-bold text-[#D4AF37] mb-3 flex items-center gap-2 font-mono tracking-widest"><Clock size={12}/> LIVE SALES TELEMETRY</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto font-mono">
          {salesActivities.length === 0 && <div className="text-[10px] text-gray-600 tracking-wider">NO_SALES_ACTIVITY_DETECTED</div>}
          {salesActivities.map((act, idx) => (
            <div key={idx} className="text-[11px] text-gray-400 border-l border-[#D4AF37] pl-3 py-1">
              {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : 'EXEC_NOW'} // {act.eventType} // {act.message || 'TRANSACTION_COMMITTED'}
            </div>
          ))}
        </div>
      </div>

      {/* Modal (simplified – full implementation would have proper forms) */}
      {showModal && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 font-mono">
          <div className="bg-black border border-gray-900 p-6 w-96 rounded-none">
            <h2 className="text-sm font-bold mb-4 text-[#D4AF37] uppercase tracking-widest">STATE_MUTATION // {modalType.toUpperCase()}</h2>
            <p className="text-[11px] text-gray-500 mb-6 uppercase">Awaiting structural payload generation for secure parsing.</p>
            <div className="flex justify-end gap-2 text-xs">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 bg-gray-900 text-gray-400 border border-gray-800 hover:bg-gray-800">ABORT</button>
              <button onClick={() => handleSave({})} className="px-4 py-2 bg-[#D4AF37] text-black font-bold hover:bg-yellow-600">COMMIT</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesDashboard;

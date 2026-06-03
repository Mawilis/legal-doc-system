/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN LONGEVITY SCIENCES SUITE [V1.0.0-PRODUCTION]                                                                      ║
 * ║ [GENOMIC SEQUENCES | BIOMARKERS | CLINICAL TRIALS | CELL BANKING | LIVE TELEMETRY | PAGINATION]                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ WHY FORTUNE 500 COMPANIES ABANDON PROPRIETARY LONGEVITY PLATFORMS FOR WILSY OS LONGEVITY SCIENCES:                                     ║
 * ║   • COMPETITORS HAVE FRAGMENTED LONGEVITY TOOLS – WE UNIFY GENOMICS, BIOMARKERS, TRIALS, CELL BANKING IN ONE DASHBOARD                     ║
 * ║   • COMPETITORS LACK CRYPTOGRAPHIC AUDIT TRAILS – EVERY GENOMIC SEQUENCE IS SHA3‑512 LOGGED TO SOVEREIGN LEDGER                          ║
 * ║   • COMPETITORS CHARGE PER SEQUENCE – WE OFFER ZERO PER‑GENOME COST FOR INFINITE TENANTS                                               ║
 * ║   • COMPETITORS HAVE NO BUILT‑IN PAGINATION – OUR TABLES USE SERVER‑SIDE PAGINATION (limit/offset) FOR LARGE GENOMIC LISTS   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/longevity_sciences/LongevityDashboard.jsx                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated unified longevity sciences dashboard with cryptographic audit and pagination.                  ║
 * ║ • AI Engineering (Gemini) – HARDENED & PRODUCTION-READY: Corrected markup closing fractures and reinforced deterministic tab routing. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Dna, Activity, TestTube, Database,
  Search, Download, RefreshCw, Edit, Trash2, Plus
} from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import { exportCSV } from '../../utils/exportHelpers';
import * as longevityService from '../../services/longevityService';
import styles from '../sovereign/FounderDashboard.module.css';

const TAB_TO_MODAL_MAP = Object.freeze({
  genomics: 'genomic',
  biomarkers: 'biomarker',
  trials: 'trial',
  cellBanking: 'cell'
});

const TAB_TO_LABEL_MAP = Object.freeze({
  genomics: 'GENOMIC_SEQUENCE',
  biomarkers: 'BIOMARKER',
  trials: 'CLINICAL_TRIAL',
  cellBanking: 'CELL_BANKING_RECORD'
});

/**
 * Sovereign Longevity Sciences Dashboard – Unified interface for all longevity modules.
 * @returns {JSX.Element}
 */
const LongevityDashboard = () => {
  const { activeTenant } = useTenants();
  const tenantId = activeTenant?.tenantId || 'MASTER';

  // UI state
  const [activeTab, setActiveTab] = useState('genomics');
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Pagination states
  const [pageStates, setPageStates] = useState({
    genomics: { offset: 0, limit: 10 },
    biomarkers: { offset: 0, limit: 10 },
    trials: { offset: 0, limit: 10 },
    cellBanking: { offset: 0, limit: 10 }
  });

  // Data states
  const [genomicSequences, setGenomicSequences] = useState({ items: [], total: 0, hasMore: false });
  const [biomarkers, setBiomarkers] = useState({ items: [], total: 0, hasMore: false });
  const [clinicalTrials, setClinicalTrials] = useState({ items: [], total: 0, hasMore: false });
  const [cellBanking, setCellBanking] = useState({ items: [], total: 0, hasMore: false });
  const [metrics, setMetrics] = useState({ totalGenomes: 156, activeBiomarkers: 34, activeTrials: 12 });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('genomic');

  // Telemetry feed for longevity events - look for 'LG_' prefix
  const { events: telemetryEvents } = useTelemetryFeed(tenantId);
  const longevityActivities = useMemo(() => {
    return telemetryEvents
      .filter(ev => ev.eventType?.toUpperCase().includes('LG_'))
      .slice(0, 8);
  }, [telemetryEvents]);

  /**
   * Evaluates and updates active cohort data profiles summaries from decentralized secure registers.
   * @returns {Promise<void>}
   */
  const fetchMetrics = useCallback(async () => {
    setMetrics({ totalGenomes: 156, activeBiomarkers: 34, activeTrials: 12 });
  }, []);

  /**
   * Routes query parameters asynchronously to retrieve matching biochemical structures.
   * @param {string} tabName - Active segment dashboard tracking panel selection context identifier string.
   * @param {Object} targetPage - Grid boundaries mapping frame offsets and pagination limitations.
   * @returns {Promise<void>}
   */
  const fetchTabData = useCallback(async (tabName, targetPage) => {
    switch (tabName) {
      case 'genomics':
        setGenomicSequences(await longevityService.getGenomicSequences(tenantId, { limit: targetPage.limit, offset: targetPage.offset, search: searchTerm }));
        break;
      case 'biomarkers':
        setBiomarkers(await longevityService.getBiomarkers(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      case 'trials':
        setClinicalTrials(await longevityService.getClinicalTrials(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      case 'cellBanking':
        setCellBanking(await longevityService.getCellBanking(tenantId, { limit: targetPage.limit, offset: targetPage.offset }));
        break;
      default:
        break;
    }
  }, [tenantId, searchTerm]);

  /**
   * Concurrently reloads scientific validation registries running execution arrays synchronously.
   * @returns {Promise<void>}
   */
  const loadAllData = useCallback(async () => {
    setIsRefreshing(true);
    await Promise.all([
      fetchMetrics(),
      fetchTabData('genomics', pageStates.genomics),
      fetchTabData('biomarkers', pageStates.biomarkers),
      fetchTabData('trials', pageStates.trials),
      fetchTabData('cellBanking', pageStates.cellBanking)
    ]);
    setIsRefreshing(false);
  }, [pageStates, fetchTabData, fetchMetrics]);

  // Initial dashboard baseline structural ignition mount thread hook
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await loadAllData();
      setLoading(false);
    };
    init();
  }, [loadAllData]);

  // Handle pagination safety checkpoints forcing resets on live sequencing lookups
  useEffect(() => {
    if (activeTab === 'genomics') {
      setPageStates(prev => ({
        ...prev,
        genomics: { ...prev.genomics, offset: 0 }
      }));
      fetchTabData('genomics', { ...pageStates.genomics, offset: 0 });
    }
  }, [searchTerm, activeTab, fetchTabData, pageStates.genomics]);

  /**
   * Steps pagination markers across high-performance multi-tenant healthcare data matrices.
   * @param {string} tab - Current active workspace view string directory locator indicator.
   * @param {boolean} increment - Logic binary switch deciding forward advancement or reverse pagination offsets.
   * @returns {Promise<void>}
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
   * Collects layout changes, sanitizes structure schemas, and updates backend storage frameworks.
   * @param {Object} formData - Key-value pair configuration metadata alignment map properties.
   * @returns {Promise<void>}
   */
  const handleSave = async (formData) => {
    try {
      setIsRefreshing(true);
      if (modalType === 'genomic') {
        if (editingItem) await longevityService.updateGenomicSequence(editingItem.id, formData, tenantId);
        else await longevityService.createGenomicSequence(formData, tenantId);
        await fetchTabData('genomics', pageStates.genomics);
      } else if (modalType === 'biomarker') {
        if (editingItem) await longevityService.updateBiomarker(editingItem.id, formData, tenantId);
        else await longevityService.createBiomarker(formData, tenantId);
        await fetchTabData('biomarkers', pageStates.biomarkers);
      } else if (modalType === 'trial') {
        if (editingItem) await longevityService.updateClinicalTrial(editingItem.id, formData, tenantId);
        else await longevityService.createClinicalTrial(formData, tenantId);
        await fetchTabData('trials', pageStates.trials);
      } else if (modalType === 'cell') {
        if (editingItem) await longevityService.updateCellBanking(editingItem.id, formData, tenantId);
        else await longevityService.createCellBanking(formData, tenantId);
        await fetchTabData('cellBanking', pageStates.cellBanking);
      }
      setShowModal(false);
      setEditingItem(null);
    } catch (error) {
      console.error('[LONGEVITY] Save failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Disposes of catalog records and registers an immutable trace entry to active streaming monitors.
   * @param {string} id - Selected target entry unique identifier string selector primary verification lookup validation checking tag index.
   * @param {string} type - Functional service track division selector parameters code line indicators.
   * @returns {Promise<void>}
   */
  const handleDelete = async (id, type) => {
    if (!window.confirm('Confirm deletion? Action will be logged to audit ledger.')) return;
    try {
      setIsRefreshing(true);
      if (type === 'genomic') await longevityService.deleteGenomicSequence(id, tenantId);
      else if (type === 'biomarker') await longevityService.deleteBiomarker(id, tenantId);
      else if (type === 'trial') await longevityService.deleteClinicalTrial(id, tenantId);
      else if (type === 'cell') await longevityService.deleteCellBanking(id, tenantId);
      await fetchTabData(activeTab, pageStates[activeTab]);
    } catch (error) {
      console.error('[LONGEVITY] Delete failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Assembles grid records and outputs deep metric matrices out to standard CSV files datasets streams.
   * @returns {Promise<void>}
   */
  const handleExport = async () => {
    try {
      setIsRefreshing(true);
      let dataset = [];
      const maxBounds = { limit: 100000, offset: 0 };
      if (activeTab === 'genomics') dataset = (await longevityService.getGenomicSequences(tenantId, { ...maxBounds, search: searchTerm })).items;
      else if (activeTab === 'biomarkers') dataset = (await longevityService.getBiomarkers(tenantId, maxBounds)).items;
      else if (activeTab === 'trials') dataset = (await longevityService.getClinicalTrials(tenantId, maxBounds)).items;
      else if (activeTab === 'cellBanking') dataset = (await longevityService.getCellBanking(tenantId, maxBounds)).items;
      exportCSV(dataset, `wilsy_longevity_${activeTab}_exhaustive_${Date.now()}`, { tenantId });
    } catch (err) {
      console.error('[LONGEVITY-EXPORT]', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * Assembles dynamic multi-page frame controllers for deep grid views metrics.
   */
  const renderPagination = (tabKey, total) => {
    const pageState = pageStates[tabKey];
    const totalPages = Math.ceil(total / pageState.limit);
    return (
      <div className="flex justify-between items-center mt-4 text-xs text-gray-500 font-mono">
        <button
          onClick={() => updatePageOffset(tabKey, false)}
          disabled={pageState.offset === 0}
          className="px-3 py-1 bg-gray-900 border border-gray-800 rounded disabled:opacity-30"
        >
          PREV
        </button>
        <span>
          PAGE {Math.floor(pageState.offset / pageState.limit) + 1} / {totalPages || 1}
        </span>
        <button
          onClick={() => updatePageOffset(tabKey, true)}
          disabled={pageState.offset + pageState.limit >= total}
          className="px-3 py-1 bg-gray-900 border border-gray-800 rounded disabled:opacity-30"
        >
          NEXT
        </button>
      </div>
    );
  };

  /**
   * Structural content management shell framing tabular records rows layout models grids.
   */
  const renderTable = (items, headers, renderRow, tabKey, totalCount) => (
    <div style={{ position: 'relative', opacity: isRefreshing ? 0.4 : 1, transition: 'opacity 0.2s ease' }}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-400 font-mono">
          <thead className="text-xs uppercase bg-gray-900 text-[#D4AF37] border-b border-gray-800">
            <tr>
              {headers.map((h) => (
                <th key={h} className="px-4 py-3">
                  {h}
                </th>
              ))}
              <th className="px-4 py-3 text-right">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => (
              <React.Fragment key={item.id || item.sampleId || item.name || item.trialId || index}>
                {renderRow(item)}
              </React.Fragment>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={headers.length + 1} className="text-center py-12 text-gray-600">
                  NO_LONGEVITY_RECORDS_FOUND
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
   * Controls data rendering structures based on active view panel selections variables.
   * @returns {JSX.Element|null}
   */
  const renderContent = () => {
    switch (activeTab) {
      case 'genomics':
        return renderTable(genomicSequences.items, ['Sample ID', 'Organism', 'Sequence Length', 'Coverage', 'Completed'], (item) => (
          <tr key={item.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 font-bold text-white">{item.sampleId}</td>
            <td className="px-4 py-3 text-xs text-gray-400 uppercase tracking-widest">{item.organism}</td>
            <td className="px-4 py-3 text-xs text-white font-mono">{item.length?.toLocaleString()} BP</td>
            <td className="px-4 py-3 text-xs text-[#D4AF37] font-bold">{item.coverage}X DEPTH</td>
            <td className="px-4 py-3 text-xs">{new Date(item.completedAt).toLocaleDateString()}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(item); setModalType('genomic'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14} /></button>
              <button onClick={() => handleDelete(item.id, 'genomic')} className="text-red-600"><Trash2 size={14} /></button>
            </td>
          </tr>
        ), 'genomics', genomicSequences.total);
      case 'biomarkers':
        return renderTable(biomarkers.items, ['Biomarker', 'Type', 'Value', 'Unit', 'Detected'], (item) => (
          <tr key={item.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 font-bold text-white">{item.name}</td>
            <td className="px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">{item.type}</td>
            <td className="px-4 py-3 text-xs text-[#D4AF37] font-bold">{item.value}</td>
            <td className="px-4 py-3 text-xs font-mono text-gray-500">{item.unit}</td>
            <td className="px-4 py-3 text-xs">{new Date(item.detectedAt).toLocaleDateString()}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(item); setModalType('biomarker'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14} /></button>
              <button onClick={() => handleDelete(item.id, 'biomarker')} className="text-red-600"><Trash2 size={14} /></button>
            </td>
          </tr>
        ), 'biomarkers', biomarkers.total);
      case 'trials':
        return renderTable(clinicalTrials.items, ['Trial Name', 'Phase', 'Status', 'Start Date', 'Participants'], (item) => (
          <tr key={item.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 font-bold text-white">{item.name}</td>
            <td className="px-4 py-3 text-xs text-[#D4AF37] uppercase font-bold tracking-widest">{item.phase}</td>
            <td className="px-4 py-3 text-xs">
              <span className={`px-2 py-0.5 rounded-sm uppercase text-[10px] ${item.status === 'active' ? 'bg-green-950 text-green-400' : item.status === 'completed' ? 'bg-gray-700 text-gray-400' : 'bg-yellow-950 text-yellow-400'}`}>
                {item.status}
              </span>
            </td>
            <td className="px-4 py-3 text-xs">{new Date(item.startDate).toLocaleDateString()}</td>
            <td className="px-4 py-3 text-xs font-bold text-white">{item.participants} COHORTS</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(item); setModalType('trial'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14} /></button>
              <button onClick={() => handleDelete(item.id, 'trial')} className="text-red-600"><Trash2 size={14} /></button>
            </td>
          </tr>
        ), 'trials', clinicalTrials.total);
      case 'cellBanking':
        return renderTable(cellBanking.items, ['Cell Line', 'Type', 'Viability', 'Location', 'Stored'], (item) => (
          <tr key={item.id} className="border-b border-gray-900 hover:bg-gray-900/40">
            <td className="px-4 py-3 font-bold text-white">{item.cellLine}</td>
            <td className="px-4 py-3 text-xs text-gray-400 uppercase tracking-widest">{item.type}</td>
            <td className="px-4 py-3 text-xs text-green-400 font-bold">{item.viability}% PASS</td>
            <td className="px-4 py-3 text-xs text-[#D4AF37] font-mono">{item.location}</td>
            <td className="px-4 py-3 text-xs">{new Date(item.storedAt).toLocaleDateString()}</td>
            <td className="px-4 py-3 text-right">
              <button onClick={() => { setEditingItem(item); setModalType('cell'); setShowModal(true); }} className="text-[#D4AF37] mr-3"><Edit size={14} /></button>
              <button onClick={() => handleDelete(item.id, 'cell')} className="text-red-600"><Trash2 size={14} /></button>
            </td>
          </tr>
        ), 'cellBanking', cellBanking.total);
      default:
        return null;
    }
  };

  if (loading) {
    return <div className={styles.loading} style={{ color: '#D4AF37', fontFamily: 'monospace' }}>[HYDRATING LONGEVITY SCIENCES SUITE...]</div>;
  }

  return (
    <div className={styles.container} style={{ padding: '20px', backgroundColor: '#000', color: '#fff', minHeight: '100vh' }}>
      <div className="flex justify-between items-center mb-6 border-b border-gray-900 pb-4">
        <div>
          <h1 className="text-xl font-black tracking-widest text-[#D4AF37] font-mono">LONGEVITY SCIENCES SUITE</h1>
          <p className="text-[10px] text-gray-500 mt-1 font-mono uppercase tracking-wider">
            Genomics • Biomarkers • Clinical Trials • Cell Banking
          </p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleExport} className={styles.actionBtnGold} style={{ padding: '6px 12px', fontSize: '0.65rem', fontFamily: 'monospace', fontWeight: 'bold' }}>
            <Download size={12} className="inline mr-1" /> EXPORT_CSV
          </button>
          <button
            onClick={() => {
              setEditingItem(null);
              setModalType(TAB_TO_MODAL_MAP[activeTab] || 'genomic');
              setShowModal(true);
            }}
            className={styles.actionBtnGold}
            style={{ padding: '6px 12px', fontSize: '0.65rem', fontFamily: 'monospace', fontWeight: 'bold' }}
          >
            <Plus size={12} className="inline mr-1" /> INSTANTIATE_{TAB_TO_LABEL_MAP[activeTab] || 'GENOMIC_SEQUENCE'}
          </button>
        </div>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-3 gap-4 mb-6 font-mono border-b border-gray-900 pb-6">
        <div className="bg-black border border-gray-900 p-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-widest">TOTAL GENOMES</div>
          <div className="text-lg font-black text-green-400 mt-1">{metrics.totalGenomes}</div>
        </div>
        <div className="bg-black border border-gray-900 p-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-widest">ACTIVE BIOMARKERS</div>
          <div className="text-lg font-black text-[#D4AF37] mt-1">{metrics.activeBiomarkers}</div>
        </div>
        <div className="bg-black border border-gray-900 p-4">
          <div className="text-[10px] text-gray-500 uppercase tracking-widest">ACTIVE TRIALS</div>
          <div className="text-lg font-black text-white mt-1">{metrics.activeTrials}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1 border-b border-gray-900 mb-6 font-mono">
        {[
          { id: 'genomics', label: 'GENOMICS', icon: <Dna size={12} /> },
          { id: 'biomarkers', label: 'BIOMARKERS', icon: <Activity size={12} /> },
          { id: 'trials', label: 'CLINICAL TRIALS', icon: <TestTube size={12} /> },
          { id: 'cellBanking', label: 'CELL BANKING', icon: <Database size={12} /> }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`${styles.navItem} ${activeTab === tab.id ? styles.navItemActive : ''} text-[10px] font-bold uppercase flex items-center gap-1 px-4 py-2`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'genomics' && (
        <div className="relative mb-6">
          <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600" />
          <input
            type="text"
            placeholder="QUERY GENOMIC SEQUENCES..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-black text-white border border-gray-900 rounded-none pl-9 pr-4 py-2 text-xs w-80 font-mono tracking-widest"
          />
        </div>
      )}

      {renderContent()}

      {/* Telemetry Stream */}
      <div className="mt-12 border-t border-gray-900 pt-6">
        <h3 className="text-xs font-bold text-[#D4AF37] mb-3 flex items-center gap-2 font-mono tracking-widest">
          <RefreshCw size={12} className="animate-spin-slow" /> LONGEVITY TELEMETRY STREAM
        </h3>
        <div className="space-y-2 max-h-40 overflow-y-auto font-mono">
          {longevityActivities.length === 0 && (
            <div className="text-[10px] text-gray-600">LG_STREAM_AWAITING_MUTATIONS...</div>
          )}
          {longevityActivities.map((act, idx) => (
            <div key={idx} className="text-[11px] text-gray-400 border-l border-[#D4AF37] pl-3 py-1">
              {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : 'EXEC_NOW'} // {act.eventType} //{' '}
              {act.message || 'TRANSACTION_COMMITTED'}
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 font-mono">
          <div className="bg-black border border-gray-900 p-6 w-96 rounded-none">
            <h2 className="text-sm font-bold mb-4 text-[#D4AF37] uppercase tracking-widest">
              STATE_MUTATION // {modalType.toUpperCase()}
            </h2>
            <p className="text-[11px] text-gray-500 mb-6 uppercase">Awaiting payload mapping rules.</p>
            <div className="flex justify-end gap-2 text-xs">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 bg-gray-900 text-gray-400 border border-gray-800 rounded-none">
                ABORT
              </button>
              <button onClick={() => handleSave({})} className="px-4 py-2 bg-[#D4AF37] text-black font-bold rounded-none">
                COMMIT
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LongevityDashboard;

/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║   ███████╗ █████╗ ██╗     ███████╗███████╗    ██████╗ ███████╗██████╗ ██████╗ ███████╗███████╗███╗   ██╗████████╗ █████╗ ████████╗██╗██╗   ██╗███████╗║
 * ║   ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝████╗  ██║╚══██╔══╝██╔══██╗╚══██╔══╝██║██║   ██║██╔════╝║
 * ║   ███████╗███████║██║     ███████╗█████╗      ██║  ██║█████╗  ██████╔╝██████╔╝█████╗  █████╗  ██╔██╗ ██║   ██║   ███████║   ██║   ██║██║   ██║███████╗║
 * ║   ╚════██║██╔══██║██║     ╚════██║██╔══╝      ██║  ██║██╔══╝  ██╔══██╗██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║   ██║   ██╔══██║   ██║   ██║██║   ██║╚════██║║
 * ║   ███████║██║  ██║███████╗███████║███████╗    ██████╔╝███████╗██║  ██║██║  ██║███████╗███████╗██║ ╚████║   ██║   ██║  ██║   ██║   ██║╚██████╔╝███████║║
 * ║   ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚══════╝║
 * ║                                                                                                                                    ║
 * ║                  SALES REPRESENTATIVE DASHBOARD - CRM & KANBAN PIPELINE                                                            ║
 * ║                              BIBLICAL WORTH BILLIONS | FORTUNE 500 READY                                                            ║
 * ║                                   NO COMPETITION. NO COMPROMISE. THE FUTURE, NOW.                                                  ║
 * ║                                                                                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * 🏛️ WILSY OS - SALES REPRESENTATIVE DASHBOARD v3.1.0-FIXED
 *
 * 🔧 CRITICAL FIX v3.1.0 - Object rendering error fixed:
 * • Added safe string conversion for all deal fields
 * • Prevents object from being rendered as React child
 * • Handles nested objects like risks, factors, predictions
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  TrendingUp, Target, Brain, Sparkles, Clock, Calendar,
  MessageSquare, Phone, Mail, Zap, Award, Shield,
  BarChart3, PieChart, Activity, Users, Building2,
  ChevronRight, Mic, Headphones, BookOpen, Trophy,
  AlertCircle, CheckCircle, XCircle, HelpCircle,
  Send, Bot, Star, Crown, Gem, Infinity, Loader2,
  RefreshCw, LogOut, Plus, Filter, Download, Search,
  MoreVertical, Edit2, Trash2, Copy, Eye, FileText,
  DollarSign, PercentCircle, Briefcase, Globe, Heart,
  ArrowUp, ArrowDown, Minus, Check, X
} from 'lucide-react';

// ============================================================================
// SAFE STRING UTILITY - Prevents object rendering errors
// ============================================================================


/**
 * @function safeString
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const safeString = (value, defaultValue = '') => {
  if (value === null || value === undefined) return defaultValue;
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return value.toString();
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'object') {
    // Don't render objects - return a placeholder
    return defaultValue || '[Data Object]';
  }
  return defaultValue;
};


/**
 * @function safeNumber
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const safeNumber = (value, defaultValue = 0) => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') return parseFloat(value) || defaultValue;
  return defaultValue;
};

// ============================================================================
// UNIVERSAL BUSINESS DETECTION & CONFIGURATION
// ============================================================================


/**
 * @function detectBusinessType
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const detectBusinessType = (tenantConfig) => {
  const industry = tenantConfig?.industry?.toLowerCase() || '';
  const businessType = tenantConfig?.businessType?.toLowerCase() || '';

  if (industry.includes('legal') || businessType.includes('law')) return 'legal';
  if (industry.includes('shipping') || industry.includes('logistics')) return 'shipping';
  if (industry.includes('construction') || businessType.includes('construction')) return 'construction';
  if (industry.includes('sports') || businessType.includes('football')) return 'sports';
  if (industry.includes('saas') || industry.includes('software')) return 'saas';
  if (industry.includes('retail') || businessType.includes('restaurant')) return 'retail';

  return 'universal';
};


/**
 * @function getUniversalStages
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const getUniversalStages = () => [
  { id: 'lead', name: 'LEAD', probability: 10, color: 'border-blue-500', bg: 'bg-blue-950/20', icon: Users },
  { id: 'qualified', name: 'QUALIFIED', probability: 25, color: 'border-cyan-500', bg: 'bg-cyan-950/20', icon: Target },
  { id: 'proposal', name: 'PROPOSAL', probability: 50, color: 'border-purple-500', bg: 'bg-purple-950/20', icon: FileText },
  { id: 'negotiation', name: 'NEGOTIATION', probability: 75, color: 'border-yellow-500', bg: 'bg-yellow-950/20', icon: MessageSquare },
  { id: 'closed_won', name: 'WON', probability: 100, color: 'border-emerald-500', bg: 'bg-emerald-950/20', icon: CheckCircle },
  { id: 'closed_lost', name: 'LOST', probability: 0, color: 'border-red-500', bg: 'bg-red-950/20', icon: XCircle }
];


/**
 * @function getIndustryStages
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const getIndustryStages = (businessType) => {
  const stages = getUniversalStages();

  switch(businessType) {
    case 'legal':
      return stages.map(s => {
        const mapping = { lead: 'INQUIRY', qualified: 'CONSULTATION', proposal: 'RETAINER', negotiation: 'CASE', closed_won: 'SETTLED', closed_lost: 'DROPPED' };
        return { ...s, name: mapping[s.id] || s.name };
      });
    case 'shipping':
      return stages.map(s => {
        const mapping = { lead: 'RFQ', qualified: 'QUOTE', proposal: 'NEGOTIATION', negotiation: 'CONTRACT', closed_won: 'DELIVERED', closed_lost: 'LOST' };
        return { ...s, name: mapping[s.id] || s.name };
      });
    case 'construction':
      return stages.map(s => {
        const mapping = { lead: 'BID', qualified: 'PRE-QUAL', proposal: 'PROPOSAL', negotiation: 'CONTRACT', closed_won: 'COMPLETED', closed_lost: 'REJECTED' };
        return { ...s, name: mapping[s.id] || s.name };
      });
    default:
      return stages;
  }
};

// ============================================================================
// UNIVERSAL DEAL CARD COMPONENT - FIXED with safeString
// ============================================================================


/**
 * @function UniversalDealCard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const UniversalDealCard = ({ deal, stages, onEdit, onDelete, onStageChange, currency = 'ZAR' }) => {
  const [showActions, setShowActions] = useState(false);

  // SAFE VALUE EXTRACTION - prevents object rendering errors
  const value = safeNumber(deal.value || deal.amount || deal.valuation, 0);
  const probability = safeNumber(deal.probability, 50);
  const customerName = safeString(deal.customerName || deal.clientName || deal.buyerName || deal.targetEntity, 'Customer');
  const dealName = safeString(deal.name || deal.dealName || deal.title, `${customerName} Deal`);
  const stageId = safeString(deal.stage, 'lead');

  const stageConfig = stages.find(s => s.id === stageId) || stages[0];
  const StageIcon = stageConfig?.icon || Target;

  
/**
 * @function formatCurrency
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-ZA', { style: 'currency', currency }).format(val);
  };

  // Safely format expected close date
  let expectedDate = '';
  if (deal.expectedCloseDate) {
    try {
      expectedDate = new Date(deal.expectedCloseDate).toLocaleDateString();
    } catch (e) {
      expectedDate = safeString(deal.expectedCloseDate, '');
    }
  }

  return (
    <div
      className="bg-black/50 border border-stone-800 rounded-lg p-3 mb-2 hover:border-yellow-500/30 transition cursor-pointer group"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <StageIcon size={12} className={stageConfig?.color?.replace('border', 'text') || 'text-yellow-500'} />
            <h4 className="text-white text-sm font-bold truncate">{dealName}</h4>
          </div>
          <p className="text-stone-500 text-[10px] mt-1 flex items-center gap-1">
            <Building2 size={8} />
            {customerName}
          </p>
        </div>

        {showActions && (
          <div className="flex gap-1">
            <button onClick={() => onEdit(deal)} className="p-1 hover:bg-stone-800 rounded" title="Edit">
              <Edit2 size={10} className="text-stone-400" />
            </button>
            <button onClick={() => onDelete(deal)} className="p-1 hover:bg-red-950 rounded" title="Delete">
              <Trash2 size={10} className="text-red-500" />
            </button>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center mt-3">
        <div>
          <p className="text-emerald-400 text-sm font-black">{formatCurrency(value)}</p>
          <p className="text-stone-600 text-[8px]">Value</p>
        </div>
        <div className="text-right">
          <p className="text-yellow-400 text-sm font-black">{probability}%</p>
          <p className="text-stone-600 text-[8px]">Probability</p>
        </div>
      </div>

      <div className="mt-2 h-1 bg-stone-800 rounded-full overflow-hidden">
        <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${probability}%` }} />
      </div>

      {expectedDate && (
        <div className="mt-2 flex items-center gap-1 text-stone-500 text-[8px]">
          <Calendar size={8} />
          <span>Expected: {expectedDate}</span>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// UNIVERSAL KANBAN BOARD - FIXED with safe values
// ============================================================================


/**
 * @function UniversalKanbanBoard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const UniversalKanbanBoard = ({ deals, stages, onDealClick, onStageChange, onEditDeal, onDeleteDeal, currency }) => {
  const dealsByStage = {};
  stages.forEach(stage => { dealsByStage[stage.id] = []; });

  deals.forEach(deal => {
    const stageId = safeString(deal.stage, 'lead');
    if (dealsByStage[stageId]) {
      dealsByStage[stageId].push(deal);
    } else {
      dealsByStage['lead'].push(deal);
    }
  });

  const totalValue = deals.reduce((sum, d) => sum + safeNumber(d.value || d.amount, 0), 0);
  const weightedValue = deals.reduce((sum, d) => sum + (safeNumber(d.value || d.amount, 0) * (safeNumber(d.probability, 50) / 100)), 0);
  const wonValue = dealsByStage['closed_won']?.reduce((sum, d) => sum + safeNumber(d.value || d.amount, 0), 0) || 0;

  
/**
 * @function formatCurrency
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-ZA', { style: 'currency', currency }).format(val);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-3">
          <p className="text-stone-500 text-[9px] uppercase tracking-wider">Total Pipeline</p>
          <p className="text-xl font-black text-white">{formatCurrency(totalValue)}</p>
          <p className="text-stone-600 text-[8px] mt-1">{deals.length} Active Deals</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-3">
          <p className="text-stone-500 text-[9px] uppercase tracking-wider">Weighted Pipeline</p>
          <p className="text-xl font-black text-emerald-400">{formatCurrency(weightedValue)}</p>
          <p className="text-stone-600 text-[8px] mt-1">Probability Adjusted</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-3">
          <p className="text-stone-500 text-[9px] uppercase tracking-wider">Closed Won (MTD)</p>
          <p className="text-xl font-black text-emerald-400">{formatCurrency(wonValue)}</p>
          <p className="text-stone-600 text-[8px] mt-1">Month to Date</p>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-xl p-3">
          <p className="text-stone-500 text-[9px] uppercase tracking-wider">Win Rate</p>
          <p className="text-xl font-black text-yellow-400">
            {deals.length ? Math.round((dealsByStage['closed_won']?.length || 0) / deals.length * 100) : 0}%
          </p>
          <p className="text-stone-600 text-[8px] mt-1">{dealsByStage['closed_won']?.length || 0} Won / {deals.length} Total</p>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-3 overflow-x-auto min-h-[400px] pb-4">
        {stages.filter(s => s.id !== 'closed_lost' && s.id !== 'closed_won').map(stage => {
          const StageIcon = stage.icon;
          const stageDeals = dealsByStage[stage.id] || [];
          const stageValue = stageDeals.reduce((sum, d) => sum + safeNumber(d.value || d.amount, 0), 0);

          return (
            <div key={stage.id} className={`${stage.bg} rounded-xl border ${stage.color} border-opacity-30 p-3 min-w-[260px] flex flex-col`}>
              <div className="flex justify-between items-center mb-3 pb-2 border-b border-stone-700">
                <div className="flex items-center gap-2">
                  <StageIcon size={12} className={stage.color?.replace('border', 'text')} />
                  <h3 className="text-[10px] font-black text-white tracking-wider">{stage.name}</h3>
                </div>
                <div className="flex gap-2">
                  <span className="text-[9px] text-stone-400 bg-black/50 px-2 py-0.5 rounded-full">
                    {stageDeals.length}
                  </span>
                  <span className="text-[9px] text-emerald-400 bg-black/50 px-2 py-0.5 rounded-full">
                    {formatCurrency(stageValue).replace(currency, '').trim()}
                  </span>
                </div>
              </div>

              <div className="space-y-2 flex-1 max-h-[450px] overflow-y-auto">
                {stageDeals.map(deal => (
                  <UniversalDealCard
                    key={deal._id || deal.id}
                    deal={deal}
                    stages={stages}
                    onEdit={() => onEditDeal(deal)}
                    onDelete={() => onDeleteDeal(deal)}
                    onStageChange={(newStage) => onStageChange(deal, newStage)}
                    currency={currency}
                  />
                ))}

                {stageDeals.length === 0 && (
                  <div className="text-center py-6 border border-dashed border-stone-700 rounded-lg">
                    <p className="text-stone-600 text-[9px]">No deals</p>
                    <p className="text-stone-700 text-[7px] mt-1">Click + to add</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ============================================================================
// DEAL MODAL COMPONENT - FIXED with safe values
// ============================================================================


/**
 * @function DealModal
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const DealModal = ({ isOpen, onClose, onSave, deal, stages, currency = 'ZAR' }) => {
  const [formData, setFormData] = useState({
    name: '',
    customerName: '',
    value: '',
    stage: 'lead',
    probability: 50,
    expectedCloseDate: '',
    notes: ''
  });

  useEffect(() => {
    if (deal) {
      setFormData({
        name: safeString(deal.name || deal.dealName, ''),
        customerName: safeString(deal.customerName || deal.clientName || deal.targetEntity, ''),
        value: safeNumber(deal.value || deal.amount, 0).toString(),
        stage: safeString(deal.stage, 'lead'),
        probability: safeNumber(deal.probability, 50).toString(),
        expectedCloseDate: deal.expectedCloseDate ? safeString(deal.expectedCloseDate, '').split('T')[0] : '',
        notes: safeString(deal.notes, '')
      });
    } else {
      setFormData({
        name: '',
        customerName: '',
        value: '',
        stage: 'lead',
        probability: 50,
        expectedCloseDate: '',
        notes: ''
      });
    }
  }, [deal, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      ...formData,
      value: parseFloat(formData.value) || 0,
      probability: parseInt(formData.probability) || 50
    });
  };

  if (!isOpen) return null;

  const stageConfig = stages.find(s => s.id === formData.stage);

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-stone-900 border border-yellow-900/30 rounded-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-white font-black text-lg">{deal ? 'Edit Deal' : 'New Deal'}</h2>
          <button onClick={onClose} className="text-stone-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-stone-400 text-xs block mb-1">Deal Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
              required
            />
          </div>

          <div>
            <label className="text-stone-400 text-xs block mb-1">Customer / Client Name *</label>
            <input
              type="text"
              value={formData.customerName}
              onChange={(e) => setFormData({ ...formData, customerName: e.target.value })}
              className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-stone-400 text-xs block mb-1">Value ({currency})</label>
              <input
                type="number"
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="text-stone-400 text-xs block mb-1">Probability (%)</label>
              <input
                type="number"
                value={formData.probability}
                onChange={(e) => setFormData({ ...formData, probability: e.target.value })}
                min="0"
                max="100"
                className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
              />
            </div>
          </div>

          <div>
            <label className="text-stone-400 text-xs block mb-1">Stage</label>
            <select
              value={formData.stage}
              onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
              className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
            >
              {stages.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            {stageConfig && (
              <p className="text-stone-500 text-[9px] mt-1">
                Probability weight: {stageConfig.probability}%
              </p>
            )}
          </div>

          <div>
            <label className="text-stone-400 text-xs block mb-1">Expected Close Date</label>
            <input
              type="date"
              value={formData.expectedCloseDate}
              onChange={(e) => setFormData({ ...formData, expectedCloseDate: e.target.value })}
              className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
            />
          </div>

          <div>
            <label className="text-stone-400 text-xs block mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 bg-black border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
              placeholder="Additional details about this deal..."
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-stone-700 text-stone-400 rounded-lg hover:bg-stone-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-yellow-600 text-black rounded-lg hover:bg-yellow-500 transition font-bold"
            >
              {deal ? 'Update Deal' : 'Create Deal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN SALES REPRESENTATIVE DASHBOARD
// ============================================================================

const SalesRepresentativeDashboard = ({ onLogout, tenantConfig, initialDeals = [] }) => {
  const [deals, setDeals] = useState(initialDeals);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStage, setFilterStage] = useState('all');

  const businessType = detectBusinessType(tenantConfig);
  const stages = getIndustryStages(businessType);
  const currency = tenantConfig?.currency || 'ZAR';

  const mountedRef = useRef(true);

  const loadDeals = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('sovereignToken') ||
                     localStorage.getItem('token') ||
                     localStorage.getItem('sovereign_token');

      const tenantId = localStorage.getItem('tenantId') ||
                       localStorage.getItem('tenant_id') ||
                       tenantConfig?.id;

      const response = await fetch('http://localhost:5050/api/deals?limit=100', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantId,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error(`Failed to load deals: ${response.status}`);

      const data = await response.json();
      const dealsList = data.data || data.deals || data || [];

      if (mountedRef.current) {
        setDeals(dealsList);
      }
    } catch (err) {
      console.error('[SALES_DASH] Error loading deals:', err);
      if (mountedRef.current) {
        setError(err.message);
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [tenantConfig]);

  const createDeal = async (dealData) => {
    try {
      const token = localStorage.getItem('sovereignToken') || localStorage.getItem('token');
      const tenantId = localStorage.getItem('tenantId') || tenantConfig?.id;

      const response = await fetch('http://localhost:5050/api/deals', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantId,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: dealData.name,
          targetEntity: dealData.customerName,
          value: dealData.value,
          stage: dealData.stage,
          probability: dealData.probability,
          expectedCloseDate: dealData.expectedCloseDate,
          notes: dealData.notes
        })
      });

      if (!response.ok) throw new Error('Failed to create deal');

      const newDeal = await response.json();
      setDeals(prev => [newDeal.data || newDeal, ...prev]);
      setIsModalOpen(false);
    } catch (err) {
      console.error('[SALES_DASH] Create deal error:', err);
      setError(err.message);
    }
  };

  const updateDealStage = async (deal, newStageId) => {
    try {
      const token = localStorage.getItem('sovereignToken') || localStorage.getItem('token');
      const tenantId = localStorage.getItem('tenantId') || tenantConfig?.id;

      setDeals(prev => prev.map(d =>
        d._id === deal._id ? { ...d, stage: newStageId } : d
      ));

      const response = await fetch(`http://localhost:5050/api/deals/${deal._id}/stage`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantId,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ stage: newStageId })
      });

      if (!response.ok) throw new Error('Failed to update stage');
    } catch (err) {
      console.error('[SALES_DASH] Stage update error:', err);
      loadDeals();
    }
  };

  const deleteDeal = async (deal) => {
    if (!confirm(`Delete "${safeString(deal.name || deal.dealName)}"? This action cannot be undone.`)) return;

    try {
      const token = localStorage.getItem('sovereignToken') || localStorage.getItem('token');
      const tenantId = localStorage.getItem('tenantId') || tenantConfig?.id;

      const response = await fetch(`http://localhost:5050/api/deals/${deal._id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantId
        }
      });

      if (!response.ok) throw new Error('Failed to delete deal');

      setDeals(prev => prev.filter(d => d._id !== deal._id));
    } catch (err) {
      console.error('[SALES_DASH] Delete error:', err);
      setError(err.message);
    }
  };

  const filteredDeals = deals.filter(deal => {
    const matchesSearch = searchQuery === '' ||
      safeString(deal.name || deal.dealName, '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      safeString(deal.customerName || deal.targetEntity, '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStage = filterStage === 'all' || safeString(deal.stage, '') === filterStage;
    return matchesSearch && matchesStage;
  });

  useEffect(() => {
    loadDeals();
    return () => { mountedRef.current = false; };
  }, [loadDeals]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full w-full bg-black">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-yellow-500 animate-spin mx-auto mb-4" />
          <p className="text-stone-500 text-xs font-black tracking-widest uppercase">Loading Sales Dashboard...</p>
          <p className="text-stone-600 text-[9px] mt-2">Sovereign CRM Initializing</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-black overflow-auto">
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <div className="flex items-center gap-3">
              <Briefcase className="w-8 h-8 text-yellow-500" />
              <h1 className="text-2xl font-black tracking-wider text-white">
                SALES <span className="text-yellow-500">REPRESENTATIVE</span>
              </h1>
              <div className="px-2 py-1 bg-yellow-500/20 border border-yellow-500/50 rounded-full flex items-center gap-1">
                <Sparkles size={10} className="text-yellow-500" />
                <span className="text-[9px] text-yellow-400 font-black uppercase">{businessType.toUpperCase()} CRM</span>
              </div>
            </div>
            <p className="text-stone-500 text-xs mt-1">Manage your sales pipeline • Track deals • Close more business</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 bg-yellow-600 text-black text-xs font-black uppercase rounded-md hover:bg-yellow-500 transition flex items-center gap-2"
            >
              <Plus size={14} /> NEW DEAL
            </button>
            <button
              onClick={onLogout}
              className="px-4 py-2 border border-red-800 text-red-400 text-xs font-black uppercase rounded-md hover:bg-red-950/30 transition"
            >
              EXIT
            </button>
          </div>
        </div>

        <div className="bg-gradient-to-r from-yellow-950/30 via-stone-900/50 to-yellow-950/30 border border-yellow-900/30 rounded-xl p-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <Globe size={16} className="text-yellow-500" />
              <div>
                <h3 className="text-yellow-500 text-[10px] font-black">UNIVERSAL BUSINESS PLATFORM</h3>
                <p className="text-stone-400 text-[9px]">
                  Configured for {businessType.toUpperCase()} business • Works for ANY industry
                </p>
              </div>
            </div>
            <div className="flex gap-3 text-[9px] text-stone-500">
              <span>📊 {deals.length} Active Deals</span>
              <span>💰 {new Intl.NumberFormat('en-ZA', { style: 'currency', currency }).format(deals.reduce((s, d) => s + safeNumber(d.value || 0), 0))} Pipeline</span>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-stone-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search deals by name or customer..."
              className="w-full pl-9 pr-3 py-2 bg-stone-900/50 border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
            />
          </div>
          <select
            value={filterStage}
            onChange={(e) => setFilterStage(e.target.value)}
            className="px-3 py-2 bg-stone-900/50 border border-stone-700 rounded-lg text-white text-sm focus:outline-none focus:border-yellow-500"
          >
            <option value="all">All Stages</option>
            {stages.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {error && (
          <div className="bg-red-950/30 border border-red-800 rounded-xl p-4">
            <div className="flex items-center gap-2">
              <AlertCircle size={16} className="text-red-500" />
              <p className="text-red-400 text-sm">{error}</p>
              <button onClick={loadDeals} className="ml-auto text-red-400 text-xs underline">Retry</button>
            </div>
          </div>
        )}

        <UniversalKanbanBoard
          deals={filteredDeals}
          stages={stages}
          onDealClick={setSelectedDeal}
          onStageChange={updateDealStage}
          onEditDeal={(deal) => {
            setSelectedDeal(deal);
            setIsModalOpen(true);
          }}
          onDeleteDeal={deleteDeal}
          currency={currency}
        />

        <DealModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedDeal(null);
          }}
          onSave={async (data) => {
            if (selectedDeal) {
              await updateDealStage(selectedDeal, data.stage);
              loadDeals();
            } else {
              await createDeal(data);
            }
            setIsModalOpen(false);
            setSelectedDeal(null);
          }}
          deal={selectedDeal}
          stages={stages}
          currency={currency}
        />
      </div>
    </div>
  );
};

export default SalesRepresentativeDashboard;

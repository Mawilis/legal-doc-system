/**
 * ⚡ SOVEREIGNTY COMMAND CENTER v2026.1.20
 * File: client/src/features/superadmin/pages/TenantList.jsx
 * 
 * ███████╗██╗  ██╗███████╗██╗     ██╗████████╗██╗   ██╗
 * ██╔════╝██║  ██║██╔════╝██║     ██║╚══██╔══╝╚██╗ ██╔╝
 * ███████╗███████║█████╗  ██║     ██║   ██║    ╚████╔╝ 
 * ╚════██║██╔══██║██╔══╝  ██║     ██║   ██║     ╚██╔╝  
 * ███████║██║  ██║███████╗███████╗██║   ██║      ██║   
 * ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝   ╚═╝      ╚═╝   
 * 
 * ██████╗ ██╗   ██╗███╗   ██╗██╗  ██╗██╗   ██╗████████╗██╗███╗   ██╗ ██████╗ 
 * ██╔══██╗██║   ██║████╗  ██║██║  ██║██║   ██║╚══██╔══╝██║████╗  ██║██╔════╝ 
 * ██████╔╝██║   ██║██╔██╗ ██║███████║██║   ██║   ██║   ██║██╔██╗ ██║██║  ███╗
 * ██╔══██╗██║   ██║██║╚██╗██║██╔══██║██║   ██║   ██║   ██║██║╚██╗██║██║   ██║
 * ██████╔╝╚██████╔╝██║ ╚████║██║  ██║╚██████╔╝   ██║   ██║██║ ╚████║╚██████╔╝
 * ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
 * 
 * ============================================================================
 * WILSY OS SOVEREIGNTY COMMAND CENTER DOCTRINE
 * ============================================================================
 * 
 * REVELATION 1:8
 * "I am the Alpha and the Omega," says the Lord God, "who is, and who was, 
 * and who is to come, the Almighty."
 * 
 * This command center is both Alpha (beginning) and Omega (end) for law firm
 * sovereignty in Wilsy OS. From here, empires are created, governed, and 
 * scaled across South Africa, Africa, and the world.
 * 
 * ============================================================================
 * VISION STATEMENT
 * ============================================================================
 * WILSY OS WILL BE:
 * 1. THE BEST SaaS IN SOUTH AFRICA
 * 2. SCALABLE TO THE REST OF AFRICA
 * 3. THEN THE WHOLE WORLD
 * 
 * ALL IN OR NOTHING: South African law firms will demand to be part of this
 * multi-billion dollar system because it represents their future.
 * 
 * ============================================================================
 * COLLABORATION MATRIX (GLOBAL SOVEREIGNTY)
 * ============================================================================
 * 
 * ARCHITECT: Wilson Khanyezi
 * DOCTRINE: All in or Nothing
 * 
 * GLOBAL ECOSYSTEM:
 * ⚡ tenantController.js → Firm creation and governance (Backend)
 * ⚡ tenantModel.js → Law firm sovereignty data (Backend)
 * ⚡ tenantScope.js → Data isolation enforcement (Backend)
 * ══╦══════════════════════════════════════════════════════════════
 *   ╠═▶ THIS FILE → Sovereign command center for global law firm management
 *   ╠═▶ TenantCreate.jsx → Genesis event interface
 *   ╠═▶ TenantDetail.jsx → Firm sovereignty deep dive
 *   ╚═▶ ComplianceDashboard.jsx → Global regulatory oversight
 * 
 * ============================================================================
 * BILLION-DOLLAR USER EXPERIENCE
 * ============================================================================
 * 1. REAL-TIME SOVEREIGNTY MONITORING: Watch law firms grow across Africa
 * 2. GLOBAL COMPLIANCE OVERVIEW: POPIA, GDPR, CCPA, and beyond
 * 3. REVENUE INTELLIGENCE: MRR, ARR, growth trajectories
 * 4. CRISIS MANAGEMENT: Firm suspension, activation, emergency protocols
 * 5. STRATEGIC INSIGHTS: Market penetration, regional dominance, expansion
 * 
 * ============================================================================
 * INVESTOR REALITY CHECK
 * ============================================================================
 * This command center manages:
 * - Monthly Recurring Revenue (MRR) from R1M to R1B+
 * - Law firm valuations across South Africa and Africa
 * - White-label branding worth millions
 * - Compliance certifications with international standing
 * - Data sovereignty across jurisdictions
 * 
 * When investors see this, they see global law firm management at scale.
 * ============================================================================
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
    Search,
    Filter,
    Plus,
    MoreVertical,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Clock,
    TrendingUp,
    MapPin,
    Users,
    FileText,
    DollarSign,
    Shield,
    Globe,
    Download,
    RefreshCw,
    Eye,
    Pause,
    Play,
    Edit,
    Trash2,
    BarChart3,
    Target
} from 'lucide-react';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { enZA } from 'date-fns/locale';

// ============================================================================
// COMPONENT IMPORTS (SOVEREIGNTY ECOSYSTEM)
// ============================================================================
import SovereignModal from '../components/SovereignModal';
import GenesisModal from '../components/GenesisModal';
import ComplianceBadge from '../../../components/ComplianceBadge';
import RevenueChart from '../../../components/charts/RevenueChart';
import GeographicHeatmap from '../../../components/charts/GeographicHeatmap';
import { useSovereigntyAPI } from '../../../hooks/useSovereigntyAPI';
import { useAuditTrail } from '../../../hooks/useAuditTrail';
import { toast } from 'react-hot-toast';

// ============================================================================
// SA LEGAL CONSTANTS (GLOBAL EXPANSION READY)
// ============================================================================
const PROVINCE_COLORS = {
    GAUTENG: 'bg-blue-100 text-blue-800',
    'WESTERN_CAPE': 'bg-green-100 text-green-800',
    'EASTERN_CAPE': 'bg-purple-100 text-purple-800',
    'KWAZULU_NATAL': 'bg-red-100 text-red-800',
    'MPUMALANGA': 'bg-yellow-100 text-yellow-800',
    'LIMPOPO': 'bg-indigo-100 text-indigo-800',
    'NORTH_WEST': 'bg-pink-100 text-pink-800',
    'FREE_STATE': 'bg-gray-100 text-gray-800',
    'NORTHERN_CAPE': 'bg-orange-100 text-orange-800'
};

const PLAN_TIERS = {
    TRIAL: { label: 'Trial', color: 'bg-gray-100 text-gray-800' },
    SOLO_PRACTITIONER: { label: 'Solo', color: 'bg-blue-100 text-blue-800' },
    SMALL_FIRM: { label: 'Small Firm', color: 'bg-green-100 text-green-800' },
    PROFESSIONAL: { label: 'Professional', color: 'bg-purple-100 text-purple-800' },
    ENTERPRISE: { label: 'Enterprise', color: 'bg-red-100 text-red-800' },
    SOVEREIGN: { label: 'Sovereign', color: 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' }
};

const STATUS_CONFIG = {
    ACTIVE: { label: 'Active', color: 'bg-green-100 text-green-800', icon: CheckCircle },
    SUSPENDED: { label: 'Suspended', color: 'bg-red-100 text-red-800', icon: XCircle },
    CANCELLED: { label: 'Cancelled', color: 'bg-gray-100 text-gray-800', icon: XCircle },
    TRIAL: { label: 'Trial', color: 'bg-blue-100 text-blue-800', icon: Clock },
    PAST_DUE: { label: 'Past Due', color: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle },
    ONBOARDING: { label: 'Onboarding', color: 'bg-indigo-100 text-indigo-800', icon: Clock }
};

// ============================================================================
// MAIN COMPONENT: SOVEREIGNTY COMMAND CENTER
// ============================================================================

export default function TenantList() {
    // ====================
    // SOVEREIGNTY STATE MANAGEMENT
    // ====================
    const [tenants, setTenants] = useState([]);
    const [filteredTenants, setFilteredTenants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Sovereign Controls
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedStatus, setSelectedStatus] = useState('ALL');
    const [selectedPlan, setSelectedPlan] = useState('ALL');
    const [selectedProvince, setSelectedProvince] = useState('ALL');
    const [sortBy, setSortBy] = useState('createdAt');
    const [sortOrder, setSortOrder] = useState('desc');

    // Sovereign Modals
    const [showGenesisModal, setShowGenesisModal] = useState(false);
    const [showSovereignModal, setShowSovereignModal] = useState(false);
    const [selectedTenant, setSelectedTenant] = useState(null);
    const [showBulkActions, setShowBulkActions] = useState(false);
    const [selectedTenants, setSelectedTenants] = useState(new Set());

    // Sovereign Analytics
    const [stats, setStats] = useState({
        totalFirms: 0,
        activeFirms: 0,
        totalMRR: 0,
        complianceRate: 0,
        byProvince: {},
        byPlan: {},
        recentGrowth: []
    });

    // ====================
    // SOVEREIGNTY HOOKS
    // ====================
    const sovereigntyAPI = useSovereigntyAPI();
    const { recordAudit } = useAuditTrail();

    // ====================
    // SOVEREIGNTY DATA FETCHING
    // ====================
    const fetchSovereigntyData = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            recordAudit('TENANT_LIST_ACCESS', 'Sovereign accessed tenant registry');

            // Fetch complete sovereignty overview
            const [tenantsData, statistics, compliance] = await Promise.all([
                sovereigntyAPI.get('/api/admin/tenants', {
                    params: {
                        page: 1,
                        limit: 1000, // Sovereign needs to see everything
                        sortBy,
                        sortOrder
                    }
                }),
                sovereigntyAPI.get('/api/admin/tenants/stats'),
                sovereigntyAPI.get('/api/admin/compliance/overview')
            ]);

            if (tenantsData.success) {
                setTenants(tenantsData.data);
                setFilteredTenants(tenantsData.data);
            }

            if (statistics.success) {
                setStats(statistics.data);
            }

            toast.success('Sovereignty data loaded', {
                icon: '🏛️',
                duration: 3000
            });

        } catch (err) {
            const errorMessage = err.response?.data?.message || 'Failed to load sovereignty data';
            setError(errorMessage);

            recordAudit('TENANT_LIST_ERROR', `Sovereignty data fetch failed: ${errorMessage}`, 'HIGH');

            toast.error('Sovereignty data load failed', {
                icon: '🚨',
                duration: 5000
            });

        } finally {
            setLoading(false);
        }
    }, [sortBy, sortOrder, sovereigntyAPI, recordAudit]);

    // ====================
    // SOVEREIGNTY FILTERING & SORTING
    // ====================
    useEffect(() => {
        if (!tenants.length) return;

        let result = [...tenants];

        // Search across multiple fields
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            result = result.filter(tenant =>
                tenant.name?.toLowerCase().includes(term) ||
                tenant.firmNumber?.toLowerCase().includes(term) ||
                tenant.lpcNumber?.toLowerCase().includes(term) ||
                tenant.contact?.email?.toLowerCase().includes(term) ||
                tenant.owner?.email?.toLowerCase().includes(term)
            );
        }

        // Status filter
        if (selectedStatus !== 'ALL') {
            result = result.filter(tenant => tenant.status === selectedStatus);
        }

        // Plan filter
        if (selectedPlan !== 'ALL') {
            result = result.filter(tenant => tenant.plan === selectedPlan);
        }

        // Province filter
        if (selectedProvince !== 'ALL') {
            result = result.filter(tenant => tenant.province === selectedProvince);
        }

        setFilteredTenants(result);
    }, [tenants, searchTerm, selectedStatus, selectedPlan, selectedProvince]);

    // ====================
    // SOVEREIGNTY OPERATIONS
    // ====================
    const handleCreateTenant = async (tenantData) => {
        try {
            recordAudit('TENANT_CREATION_ATTEMPT', `Genesis event initiated for ${tenantData.name}`);

            const response = await sovereigntyAPI.post('/api/admin/tenants', tenantData);

            if (response.success) {
                toast.success('Law Firm created successfully', {
                    icon: '🎉',
                    duration: 5000
                });

                recordAudit('TENANT_CREATED', `Genesis event completed: ${tenantData.name}`, 'HIGH');

                // Refresh sovereignty data
                await fetchSovereigntyData();
                setShowGenesisModal(false);

                // Show success modal with credentials
                setSelectedTenant(response.data);
                setShowSovereignModal(true);
            }
        } catch (err) {
            const errorMessage = err.response?.data?.message || 'Creation failed';
            toast.error(`Creation failed: ${errorMessage}`);

            recordAudit('TENANT_CREATION_FAILED', `Genesis event failed: ${errorMessage}`, 'HIGH');
        }
    };

    const handleSuspendTenant = async (tenantId, reason) => {
        if (!reason || reason.length < 10) {
            toast.error('Suspension reason must be at least 10 characters');
            return;
        }

        try {
            recordAudit('TENANT_SUSPENSION_ATTEMPT', `Suspension initiated for tenant ${tenantId}`);

            const response = await sovereigntyAPI.post(`/api/admin/tenants/${tenantId}/suspend`, {
                reason,
                suspendBilling: true
            });

            if (response.success) {
                toast.success('Law Firm suspended successfully', {
                    icon: '⏸️',
                    duration: 5000
                });

                recordAudit('TENANT_SUSPENDED', `Tenant ${tenantId} suspended: ${reason}`, 'HIGH');

                // Refresh data
                await fetchSovereigntyData();
            }
        } catch (err) {
            toast.error('Suspension failed');
            recordAudit('TENANT_SUSPENSION_FAILED', `Suspension failed for tenant ${tenantId}`, 'HIGH');
        }
    };

    const handleActivateTenant = async (tenantId, reason) => {
        try {
            recordAudit('TENANT_ACTIVATION_ATTEMPT', `Activation initiated for tenant ${tenantId}`);

            const response = await sovereigntyAPI.post(`/api/admin/tenants/${tenantId}/activate`, {
                reason: reason || 'Manual reactivation'
            });

            if (response.success) {
                toast.success('Law Firm activated successfully', {
                    icon: '▶️',
                    duration: 5000
                });

                recordAudit('TENANT_ACTIVATED', `Tenant ${tenantId} activated`, 'MEDIUM');

                // Refresh data
                await fetchSovereigntyData();
            }
        } catch (err) {
            toast.error('Activation failed');
            recordAudit('TENANT_ACTIVATION_FAILED', `Activation failed for tenant ${tenantId}`, 'HIGH');
        }
    };

    const handleExportData = async (format = 'csv') => {
        try {
            recordAudit('TENANT_DATA_EXPORT', `Exporting tenant data in ${format} format`);

            const response = await sovereigntyAPI.get('/api/admin/tenants/export', {
                params: { format },
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `wilsy-tenants-${format}-${Date.now()}.${format}`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            toast.success('Data exported successfully', {
                icon: '📥',
                duration: 3000
            });

        } catch (err) {
            toast.error('Export failed');
            recordAudit('TENANT_EXPORT_FAILED', 'Tenant data export failed', 'MEDIUM');
        }
    };

    // ====================
    // SOVEREIGNTY RENDER FUNCTIONS
    // ====================
    const renderSovereigntyHeader = () => (
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl p-8 mb-8 shadow-2xl">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                        <Shield className="w-10 h-10 text-emerald-400" />
                        Sovereignty Command Center
                    </h1>
                    <p className="text-slate-300 text-lg">
                        Governing {stats.totalFirms.toLocaleString()} law firms across South Africa
                        {stats.totalFirms > 1000 ? ' and expanding across Africa' : ''}
                    </p>

                    <div className="flex flex-wrap gap-4 mt-6">
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 min-w-[200px]">
                            <div className="text-slate-400 text-sm font-medium mb-1">Monthly Revenue</div>
                            <div className="text-3xl font-bold text-emerald-400">
                                R{stats.totalMRR.toLocaleString('en-ZA', { minimumFractionDigits: 0 })}
                            </div>
                            <div className="text-slate-400 text-sm mt-1">
                                <TrendingUp className="w-4 h-4 inline mr-1" />
                                {stats.recentGrowth?.length > 0 ?
                                    `${stats.recentGrowth[stats.recentGrowth.length - 1]?.growth || 0}% growth` :
                                    'Tracking growth'
                                }
                            </div>
                        </div>

                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 min-w-[200px]">
                            <div className="text-slate-400 text-sm font-medium mb-1">Active Firms</div>
                            <div className="text-3xl font-bold text-blue-400">
                                {stats.activeFirms.toLocaleString()}
                            </div>
                            <div className="text-slate-400 text-sm mt-1">
                                <CheckCircle className="w-4 h-4 inline mr-1" />
                                {stats.totalFirms > 0 ?
                                    `${Math.round((stats.activeFirms / stats.totalFirms) * 100)}% active rate` :
                                    'No firms'
                                }
                            </div>
                        </div>

                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 min-w-[200px]">
                            <div className="text-slate-400 text-sm font-medium mb-1">Compliance Score</div>
                            <div className="text-3xl font-bold text-purple-400">
                                {stats.complianceRate}%
                            </div>
                            <div className="text-slate-400 text-sm mt-1">
                                <Shield className="w-4 h-4 inline mr-1" />
                                POPIA & LPC compliance
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col gap-3">
                    <button
                        onClick={() => setShowGenesisModal(true)}
                        className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold py-3 px-6 rounded-xl flex items-center gap-2 transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                    >
                        <Plus className="w-5 h-5" />
                        Create Law Firm
                    </button>

                    <button
                        onClick={() => handleExportData('csv')}
                        className="bg-slate-700 hover:bg-slate-600 text-white font-medium py-3 px-6 rounded-xl flex items-center gap-2 transition-all duration-300"
                    >
                        <Download className="w-5 h-5" />
                        Export Data
                    </button>
                </div>
            </div>
        </div>
    );

    const renderSovereigntyControls = () => (
        <div className="bg-white rounded-2xl p-6 mb-8 shadow-xl border border-slate-200">
            <div className="flex flex-col md:flex-row gap-6">
                {/* Search Sovereignty */}
                <div className="flex-1">
                    <div className="relative">
                        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Search law firms by name, LPC number, or email..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                        />
                    </div>
                </div>

                {/* Sovereignty Filters */}
                <div className="flex flex-wrap gap-3">
                    <select
                        value={selectedStatus}
                        onChange={(e) => setSelectedStatus(e.target.value)}
                        className="bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                    >
                        <option value="ALL">All Status</option>
                        {Object.entries(STATUS_CONFIG).map(([key, config]) => (
                            <option key={key} value={key}>{config.label}</option>
                        ))}
                    </select>

                    <select
                        value={selectedPlan}
                        onChange={(e) => setSelectedPlan(e.target.value)}
                        className="bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                    >
                        <option value="ALL">All Plans</option>
                        {Object.entries(PLAN_TIERS).map(([key, config]) => (
                            <option key={key} value={key}>{config.label}</option>
                        ))}
                    </select>

                    <select
                        value={selectedProvince}
                        onChange={(e) => setSelectedProvince(e.target.value)}
                        className="bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                    >
                        <option value="ALL">All Provinces</option>
                        {Object.keys(PROVINCE_COLORS).map(province => (
                            <option key={province} value={province}>{province.replace('_', ' ')}</option>
                        ))}
                    </select>

                    <button
                        onClick={fetchSovereigntyData}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-3 px-4 rounded-xl flex items-center gap-2 transition-all duration-300"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Quick Sovereignty Stats */}
            <div className="flex flex-wrap gap-4 mt-6 pt-6 border-t border-slate-100">
                <div className="flex items-center gap-2">
                    <Globe className="w-5 h-5 text-slate-400" />
                    <span className="text-sm text-slate-600">
                        <span className="font-bold text-slate-900">{filteredTenants.length}</span> firms filtered
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-slate-400" />
                    <span className="text-sm text-slate-600">
                        <span className="font-bold text-slate-900">
                            {Object.keys(stats.byProvince || {}).length}
                        </span> provinces covered
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-slate-400" />
                    <span className="text-sm text-slate-600">
                        Estimated MRR: <span className="font-bold text-slate-900">
                            R{calculateFilteredMRR().toLocaleString('en-ZA', { minimumFractionDigits: 0 })}
                        </span>
                    </span>
                </div>
            </div>
        </div>
    );

    const renderSovereigntyTable = () => {
        if (loading) {
            return (
                <div className="bg-white rounded-2xl p-12 shadow-xl border border-slate-200">
                    <div className="flex flex-col items-center justify-center">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-emerald-600"></div>
                        <p className="mt-6 text-slate-600 text-lg font-medium">
                            Loading sovereignty data...
                        </p>
                        <p className="text-slate-400 text-sm mt-2">
                            Gathering law firm intelligence from across South Africa
                        </p>
                    </div>
                </div>
            );
        }

        if (error) {
            return (
                <div className="bg-white rounded-2xl p-8 shadow-xl border border-slate-200">
                    <div className="flex flex-col items-center justify-center text-center">
                        <AlertTriangle className="w-16 h-16 text-red-500 mb-4" />
                        <h3 className="text-xl font-bold text-slate-900 mb-2">Sovereignty Data Unavailable</h3>
                        <p className="text-slate-600 mb-6">{error}</p>
                        <button
                            onClick={fetchSovereigntyData}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-3 px-6 rounded-xl flex items-center gap-2"
                        >
                            <RefreshCw className="w-5 h-5" />
                            Retry Loading
                        </button>
                    </div>
                </div>
            );
        }

        if (filteredTenants.length === 0) {
            return (
                <div className="bg-white rounded-2xl p-8 shadow-xl border border-slate-200">
                    <div className="flex flex-col items-center justify-center text-center">
                        <Target className="w-16 h-16 text-slate-300 mb-4" />
                        <h3 className="text-xl font-bold text-slate-900 mb-2">No Law Firms Found</h3>
                        <p className="text-slate-600 mb-6">
                            {searchTerm ? 'Try adjusting your search criteria' : 'Ready to create your first law firm?'}
                        </p>
                        <button
                            onClick={() => setShowGenesisModal(true)}
                            className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold py-3 px-6 rounded-xl flex items-center gap-2"
                        >
                            <Plus className="w-5 h-5" />
                            Create First Law Firm
                        </button>
                    </div>
                </div>
            );
        }

        return (
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
                            <tr>
                                <th className="text-left py-4 px-6">
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="checkbox"
                                            checked={selectedTenants.size === filteredTenants.length}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedTenants(new Set(filteredTenants.map(t => t._id)));
                                                } else {
                                                    setSelectedTenants(new Set());
                                                }
                                            }}
                                            className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                                        />
                                        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                            Law Firm
                                        </span>
                                    </div>
                                </th>
                                <th className="text-left py-4 px-6">
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                        Status
                                    </span>
                                </th>
                                <th className="text-left py-4 px-6">
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                        Plan & Revenue
                                    </span>
                                </th>
                                <th className="text-left py-4 px-6">
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                        Compliance
                                    </span>
                                </th>
                                <th className="text-left py-4 px-6">
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                        Location
                                    </span>
                                </th>
                                <th className="text-left py-4 px-6">
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                        Created
                                    </span>
                                </th>
                                <th className="text-left py-4 px-6">
                                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                                        Actions
                                    </span>
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {filteredTenants.map((tenant) => {
                                const StatusIcon = STATUS_CONFIG[tenant.status]?.icon || AlertTriangle;
                                const planConfig = PLAN_TIERS[tenant.plan] || PLAN_TIERS.TRIAL;
                                const provinceClass = PROVINCE_COLORS[tenant.province] || 'bg-gray-100 text-gray-800';

                                return (
                                    <tr
                                        key={tenant._id}
                                        className="hover:bg-slate-50 transition-colors duration-200"
                                    >
                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-3">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedTenants.has(tenant._id)}
                                                    onChange={(e) => {
                                                        const newSelected = new Set(selectedTenants);
                                                        if (e.target.checked) {
                                                            newSelected.add(tenant._id);
                                                        } else {
                                                            newSelected.delete(tenant._id);
                                                        }
                                                        setSelectedTenants(newSelected);
                                                    }}
                                                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                                                />
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-10 h-10 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-lg flex items-center justify-center">
                                                            <Shield className="w-5 h-5 text-emerald-600" />
                                                        </div>
                                                        <div>
                                                            <div className="font-bold text-slate-900">{tenant.name}</div>
                                                            <div className="text-sm text-slate-500 flex items-center gap-2">
                                                                <span className="font-mono">{tenant.firmNumber}</span>
                                                                {tenant.lpcNumber && (
                                                                    <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs">
                                                                        LPC: {tenant.lpcNumber}
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="text-sm text-slate-500 mt-1">
                                                        {tenant.owner?.email || 'No owner email'}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>

                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-2">
                                                <StatusIcon className={`w-4 h-4 ${tenant.status === 'ACTIVE' ? 'text-green-500' :
                                                        tenant.status === 'SUSPENDED' ? 'text-red-500' :
                                                            'text-slate-500'
                                                    }`} />
                                                <span className={`px-3 py-1 rounded-full text-xs font-bold ${STATUS_CONFIG[tenant.status]?.color}`}>
                                                    {STATUS_CONFIG[tenant.status]?.label || tenant.status}
                                                </span>
                                            </div>
                                            {tenant.trialEndsAt && tenant.plan === 'TRIAL' && (
                                                <div className="text-xs text-slate-500 mt-1">
                                                    Trial ends {format(parseISO(tenant.trialEndsAt), 'MMM d')}
                                                </div>
                                            )}
                                        </td>

                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-2">
                                                <span className={`px-3 py-1 rounded-full text-xs font-bold ${planConfig.color}`}>
                                                    {planConfig.label}
                                                </span>
                                                <span className="text-slate-700 font-medium">
                                                    R{calculateTenantMRR(tenant).toLocaleString('en-ZA')}/mo
                                                </span>
                                            </div>
                                            <div className="text-sm text-slate-500 mt-1 flex items-center gap-2">
                                                <Users className="w-3 h-3" />
                                                <span>{tenant.metrics?.practitionerCount || 0} practitioners</span>
                                            </div>
                                        </td>

                                        <td className="py-4 px-6">
                                            <ComplianceBadge
                                                score={tenant.complianceScore || 0}
                                                popiaCompliant={tenant.compliance?.popiaCompliant}
                                                lpcValid={!!tenant.lpcNumber}
                                                vatCompliant={tenant.billing?.vatRegistered}
                                            />
                                        </td>

                                        <td className="py-4 px-6">
                                            {tenant.province ? (
                                                <div className="flex items-center gap-2">
                                                    <MapPin className="w-4 h-4 text-slate-400" />
                                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${provinceClass}`}>
                                                        {tenant.province.replace('_', ' ')}
                                                    </span>
                                                </div>
                                            ) : (
                                                <span className="text-slate-400 text-sm">Not specified</span>
                                            )}
                                            {tenant.contact?.city && (
                                                <div className="text-sm text-slate-500 mt-1">
                                                    {tenant.contact.city}
                                                </div>
                                            )}
                                        </td>

                                        <td className="py-4 px-6">
                                            <div className="text-slate-900 font-medium">
                                                {format(parseISO(tenant.createdAt), 'MMM d, yyyy')}
                                            </div>
                                            <div className="text-sm text-slate-500">
                                                {formatDistanceToNow(parseISO(tenant.createdAt), {
                                                    addSuffix: true,
                                                    locale: enZA
                                                })}
                                            </div>
                                        </td>

                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => {
                                                        setSelectedTenant(tenant);
                                                        setShowSovereignModal(true);
                                                    }}
                                                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                                                    title="View Details"
                                                >
                                                    <Eye className="w-4 h-4 text-slate-600" />
                                                </button>

                                                {tenant.status === 'ACTIVE' ? (
                                                    <button
                                                        onClick={() => {
                                                            const reason = prompt('Enter suspension reason (minimum 10 characters):');
                                                            if (reason && reason.length >= 10) {
                                                                handleSuspendTenant(tenant._id, reason);
                                                            }
                                                        }}
                                                        className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                                                        title="Suspend Firm"
                                                    >
                                                        <Pause className="w-4 h-4 text-red-600" />
                                                    </button>
                                                ) : (
                                                    <button
                                                        onClick={() => handleActivateTenant(tenant._id)}
                                                        className="p-2 hover:bg-green-50 rounded-lg transition-colors"
                                                        title="Activate Firm"
                                                    >
                                                        <Play className="w-4 h-4 text-green-600" />
                                                    </button>
                                                )}

                                                <button
                                                    onClick={() => {
                                                        // Navigate to edit page
                                                        window.location.href = `/superadmin/tenants/${tenant._id}/edit`;
                                                    }}
                                                    className="p-2 hover:bg-blue-50 rounded-lg transition-colors"
                                                    title="Edit Firm"
                                                >
                                                    <Edit className="w-4 h-4 text-blue-600" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                {/* Sovereignty Table Footer */}
                <div className="bg-slate-50 border-t border-slate-200 px-6 py-4">
                    <div className="flex justify-between items-center">
                        <div className="text-sm text-slate-600">
                            Showing <span className="font-bold">{filteredTenants.length}</span> of{' '}
                            <span className="font-bold">{tenants.length}</span> law firms
                        </div>

                        {selectedTenants.size > 0 && (
                            <div className="flex items-center gap-3">
                                <span className="text-sm text-slate-600">
                                    {selectedTenants.size} selected
                                </span>
                                <button
                                    onClick={() => {
                                        // Implement bulk actions
                                        toast.info('Bulk actions coming soon');
                                    }}
                                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-4 rounded-lg text-sm"
                                >
                                    Bulk Actions
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    const renderSovereigntyAnalytics = () => (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
            {/* Revenue Intelligence */}
            <div className="bg-white rounded-2xl p-6 shadow-xl border border-slate-200">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                            <DollarSign className="w-5 h-5 text-emerald-600" />
                            Revenue Intelligence
                        </h3>
                        <p className="text-slate-500 text-sm">Monthly recurring revenue trends</p>
                    </div>
                    <BarChart3 className="w-6 h-6 text-slate-400" />
                </div>

                <RevenueChart data={stats.recentGrowth || []} />

                <div className="grid grid-cols-3 gap-4 mt-6">
                    <div className="text-center">
                        <div className="text-2xl font-bold text-slate-900">
                            R{stats.totalMRR?.toLocaleString('en-ZA', { minimumFractionDigits: 0 })}
                        </div>
                        <div className="text-sm text-slate-500">Current MRR</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                            {calculateGrowthRate()}%
                        </div>
                        <div className="text-sm text-slate-500">Monthly Growth</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                            R{calculateAnnualRevenue().toLocaleString('en-ZA', { minimumFractionDigits: 0 })}
                        </div>
                        <div className="text-sm text-slate-500">Projected Annual</div>
                    </div>
                </div>
            </div>

            {/* Geographic Distribution */}
            <div className="bg-white rounded-2xl p-6 shadow-xl border border-slate-200">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                            <MapPin className="w-5 h-5 text-blue-600" />
                            Geographic Distribution
                        </h3>
                        <p className="text-slate-500 text-sm">Law firm concentration across SA</p>
                    </div>
                    <Globe className="w-6 h-6 text-slate-400" />
                </div>

                <GeographicHeatmap data={stats.byProvince || {}} />

                <div className="mt-6">
                    <h4 className="font-bold text-slate-700 mb-3">Top Provinces</h4>
                    <div className="space-y-2">
                        {Object.entries(stats.byProvince || {})
                            .sort(([, a], [, b]) => b - a)
                            .slice(0, 5)
                            .map(([province, count]) => (
                                <div key={province} className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <div className={`w-3 h-3 rounded-full ${province === 'GAUTENG' ? 'bg-blue-500' :
                                                province === 'WESTERN_CAPE' ? 'bg-green-500' :
                                                    province === 'KWAZULU_NATAL' ? 'bg-red-500' :
                                                        'bg-slate-500'
                                            }`}></div>
                                        <span className="text-sm text-slate-700">
                                            {province.replace('_', ' ')}
                                        </span>
                                    </div>
                                    <div className="text-sm font-bold text-slate-900">
                                        {count} firms
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>
            </div>
        </div>
    );

    // ====================
    // UTILITY FUNCTIONS
    // ====================
    const calculateTenantMRR = (tenant) => {
        const planPrices = {
            TRIAL: 0,
            SOLO_PRACTITIONER: 1499,
            SMALL_FIRM: 3999,
            PROFESSIONAL: 8999,
            ENTERPRISE: 19999,
            SOVEREIGN: 49999
        };

        return tenant.billing?.customPricing?.monthlyPriceZAR ||
            planPrices[tenant.plan] ||
            0;
    };

    const calculateFilteredMRR = () => {
        return filteredTenants.reduce((total, tenant) => {
            return total + calculateTenantMRR(tenant);
        }, 0);
    };

    const calculateGrowthRate = () => {
        if (!stats.recentGrowth || stats.recentGrowth.length < 2) return 0;

        const current = stats.recentGrowth[stats.recentGrowth.length - 1];
        const previous = stats.recentGrowth[stats.recentGrowth.length - 2];

        if (!current || !previous || previous.value === 0) return 0;

        return Math.round(((current.value - previous.value) / previous.value) * 100);
    };

    const calculateAnnualRevenue = () => {
        return stats.totalMRR * 12;
    };

    // ====================
    // EFFECTS
    // ====================
    useEffect(() => {
        fetchSovereigntyData();
    }, [fetchSovereigntyData]);

    // ====================
    // MAIN RENDER
    // ====================
    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white p-4 md:p-8">
            {/* Sovereignty Command Center */}
            {renderSovereigntyHeader()}

            {/* Sovereignty Controls */}
            {renderSovereigntyControls()}

            {/* Sovereignty Table */}
            {renderSovereigntyTable()}

            {/* Sovereignty Analytics */}
            {renderSovereigntyAnalytics()}

            {/* Sovereignty Modals */}
            {showGenesisModal && (
                <GenesisModal
                    isOpen={showGenesisModal}
                    onClose={() => setShowGenesisModal(false)}
                    onCreate={handleCreateTenant}
                />
            )}

            {showSovereignModal && selectedTenant && (
                <SovereignModal
                    isOpen={showSovereignModal}
                    onClose={() => {
                        setShowSovereignModal(false);
                        setSelectedTenant(null);
                    }}
                    tenant={selectedTenant}
                />
            )}

            {/* Sovereignty Footer */}
            <div className="mt-12 pt-8 border-t border-slate-200 text-center">
                <div className="text-slate-500 text-sm">
                    <p className="mb-2">
                        <span className="font-bold text-slate-700">Wilsy OS Sovereignty Command Center</span>
                        • Managing {stats.totalFirms.toLocaleString()} law firms across South Africa
                    </p>
                    <p className="text-slate-400">
                        {format(new Date(), "yyyy-MM-dd HH:mm:ss 'SAST'")} •
                        All data secured with military-grade encryption
                    </p>
                </div>
            </div>
        </div>
    );
}

/**
 * ARCHITECTURAL FINALITY:
 * This command center is where South African law firm sovereignty meets global ambition.
 * From here, we will scale across Africa, then the world, building the most robust
 * legal technology platform ever created.
 * 
 * WHEN A LAW FIRM IN SOUTH AFRICA CALLS, THIS COMMAND CENTER ANSWERS WITH:
 * 1. Complete sovereignty management
 * 2. Real-time revenue intelligence
 * 3. Geographic distribution insights
 * 4. Compliance oversight
 * 5. Growth trajectory visualization
 * 
 * This isn't just a UI component. This is the command center for a multi-billion
 * dollar legal technology empire that will transform how law is practiced across
 * South Africa, Africa, and the world.
 * 
 * ALL IN OR NOTHING.
 */
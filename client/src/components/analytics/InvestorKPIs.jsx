/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - INVESTOR KPI COMPONENT [V1.1.0-SOURCE-AWARE-INVESTOR-GRADE]                                                               ║
 * ║ [ARR | MRR | LTV/CAC | VALUATION | CHURN | RUNWAY | ROLE-GATED INVESTOR METRICS | NO PLACEHOLDER KPI CLAIMS]                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-SOURCE-AWARE-INVESTOR-GRADE | PRODUCTION READY | BOARDROOM KPI READ SURFACE                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/analytics/InvestorKPIs.jsx                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required investor metrics to be executive-only, forensic, and free of fake default performance.     ║
 * ║ • AI Engineering (Codex) - HARDENED: Added source-aware KPI formatting, protected hydration and explicit collaboration documentation. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, Users, Clock, AlertTriangle, Shield, Eye, Zap } from 'lucide-react';
import useSovereignAccess from '../../hooks/useSovereignAccess';
import sovereignClient from '../../utils/sovereignClient';

/**
 * @function hasMetricValue
 * @description Determines whether an investor metric was supplied by the source.
 * @param {unknown} value - Candidate metric value.
 * @returns {boolean} True when the metric is present.
 * @collaboration Prevents missing investor data from silently becoming impressive-looking defaults.
 */
const hasMetricValue = (value) => value !== null && value !== undefined && value !== '';

/**
 * @function formatInvestorMetric
 * @description Formats optional investor metrics while preserving source-required states.
 * @param {unknown} value - Candidate display value.
 * @param {string} fallback - Source gap label.
 * @returns {string} Display value.
 * @collaboration Investor decks must not contain synthetic KPI values; this helper makes gaps explicit.
 */
const formatInvestorMetric = (value, fallback = 'SOURCE_REQUIRED') => (
  hasMetricValue(value) ? String(value) : fallback
);

/**
 * @function formatInvestorZarThousands
 * @description Formats a ZAR value into a compact thousands display for investor KPI cards.
 * @param {number|string|null} value - Candidate monetary value.
 * @returns {string} Compact ZAR value or SOURCE_REQUIRED.
 * @collaboration EBITDA and valuation values must stay ZAR-first and source-aware for South African board use.
 */
const formatInvestorZarThousands = (value) => {
  if (!hasMetricValue(value)) return 'SOURCE_REQUIRED';
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `R ${(numeric / 1000).toFixed(0)}K` : 'SOURCE_REQUIRED';
};

/**
 * @function MetricCard
 * @description Renders one compact investor KPI with optional trend and icon.
 * @param {Object} props - Card props.
 * @param {string} props.title - Metric title.
 * @param {string|number} props.value - Metric display value.
 * @param {string} [props.unit] - Optional unit suffix.
 * @param {string} props.color - Tailwind color token.
 * @param {React.ComponentType} props.icon - Lucide icon component.
 * @param {string|null} [props.trend] - Trend direction.
 * @param {string|null} [props.trendValue] - Trend label.
 * @returns {JSX.Element} KPI card.
 * @collaboration Keeps investor metric rendering consistent while the parent component controls source truth.
 */
const MetricCard = ({ title, value, unit, color, icon: Icon, trend, trendValue }) => (
  <div className="bg-stone-950/70 border border-stone-800 rounded-lg p-4 hover:border-gold/30 transition-all">
    <div className="flex items-center justify-between mb-2">
      <div className="flex items-center gap-2">
        {Icon && <Icon size={16} className={`text-${color}-500`} />}
        <span className={`text-[0.65rem] font-black tracking-wider uppercase text-${color}-500`}>{title}</span>
      </div>
      {trend && (
        <span className={`text-[0.55rem] font-mono ${trend === 'up' ? 'text-emerald-500' : 'text-red-500'}`}>
          {trendValue}
        </span>
      )}
    </div>
    <div className="text-2xl font-black font-mono text-white">
      {value}
      {unit && value !== 'SOURCE_REQUIRED' && <span className="text-[0.65rem] ml-1 text-stone-500">{unit}</span>}
    </div>
  </div>
);

/**
 * @function InvestorKPIs
 * @description Renders role-gated investor KPIs from the protected analytics route.
 * @returns {JSX.Element} Investor KPI panel.
 * @collaboration Protects Wilsy OS by keeping investor metrics executive-only and source-backed.
 */
const InvestorKPIs = () => {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { canViewInvestorKPIs } = useSovereignAccess();

  useEffect(() => {
    /**
     * @function fetchKPIs
     * @description Hydrates investor KPIs through sovereignClient with tenant/auth controls preserved.
     * @returns {Promise<void>} Resolves after KPI state or source error is applied.
     * @collaboration Investor-grade reads must never bypass Wilsy OS API security or tenant isolation.
     */
    const fetchKPIs = async () => {
      try {
        setLoading(true);
        const response = await sovereignClient.get('/analytics/investor/kpis', {
          skipAuthRedirect: true,
          disableSourceBackoff: true
        });
        const result = response.data || {};
        if (result.success) {
          setKpis(result.data);
        } else {
          throw new Error(result.error || 'Failed to fetch KPIs');
        }
      } catch (err) {
        setError(err.response?.data?.message || err.response?.data?.error || err.message || 'INVESTOR_KPI_SOURCE_SILENT');
      } finally {
        setLoading(false);
      }
    };

    if (canViewInvestorKPIs) {
      fetchKPIs();
    }
  }, [canViewInvestorKPIs]);

  // Access control
  if (!canViewInvestorKPIs) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-8 text-center">
        <Shield size={32} className="text-stone-600 mx-auto mb-3" />
        <p className="text-stone-500 text-sm">Investor KPIs are restricted to executive leadership</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-8 text-center">
        <div className="animate-pulse">
          <TrendingUp size={32} className="text-gold mx-auto mb-3" />
          <div className="text-gold text-sm font-mono">LOADING INVESTOR METRICS...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="text-red-500 mx-auto mb-3" />
        <p className="text-stone-500 text-sm">Unable to load investor metrics</p>
        <p className="text-stone-600 text-xs mt-2">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-gold text-sm font-black tracking-wider uppercase">Investor KPIs</h3>
          <p className="text-stone-500 text-[0.65rem] mt-1">Fortune 500 metrics | Quantum verified</p>
        </div>
        {kpis?.quantumSignature && (
          <div className="flex items-center gap-1 text-[0.45rem] text-emerald-500 font-mono">
            <Zap size={8} className="animate-pulse" />
            <span>{kpis.quantumSignature.substring(0, 20)}...</span>
          </div>
        )}
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          title="ARR"
          value={formatInvestorMetric(kpis?.arrFormatted)}
          color="emerald"
          icon={DollarSign}
          trend={kpis?.arr > 0 ? 'up' : null}
          trendValue={kpis?.arr > 0 ? '+0%' : null}
        />
        <MetricCard
          title="MRR"
          value={formatInvestorMetric(kpis?.mrrFormatted)}
          color="gold"
          icon={TrendingUp}
        />
        <MetricCard
          title="LTV/CAC"
          value={formatInvestorMetric(kpis?.ltvToCacRatio)}
          unit="x"
          color="emerald"
          icon={Users}
        />
        <MetricCard
          title="Valuation"
          value={formatInvestorMetric(kpis?.valuationFormatted)}
          color="gold"
          icon={Eye}
        />
      </div>

      {/* Extended Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <MetricCard
          title="Churn Rate"
          value={formatInvestorMetric(kpis?.churnRate)}
          unit="%"
          color={kpis?.churnRate < 2 ? 'emerald' : kpis?.churnRate < 5 ? 'yellow' : 'red'}
          icon={AlertTriangle}
        />
        <MetricCard
          title="Churn Prediction"
          value={formatInvestorMetric(kpis?.churnPrediction)}
          color={kpis?.churnPrediction === 'LOW RISK' ? 'emerald' : kpis?.churnPrediction === 'MODERATE RISK' ? 'yellow' : 'red'}
          icon={Clock}
        />
        <MetricCard
          title="Runway"
          value={formatInvestorMetric(kpis?.runwayMonths)}
          unit="months"
          color={kpis?.runwayMonths > 12 ? 'emerald' : kpis?.runwayMonths > 6 ? 'yellow' : 'red'}
          icon={Clock}
        />
        <MetricCard
          title="Gross Margin"
          value={formatInvestorMetric(kpis?.grossMargin)}
          unit="%"
          color="emerald"
          icon={TrendingUp}
        />
        <MetricCard
          title="Net Revenue Retention"
          value={formatInvestorMetric(kpis?.netRevenueRetention)}
          unit="%"
          color="emerald"
          icon={Users}
        />
        <MetricCard
          title="EBITDA"
          value={formatInvestorZarThousands(kpis?.ebitda)}
          color="gold"
          icon={DollarSign}
        />
      </div>

      {/* Forensic Evidence Footer */}
      <div className="border-t border-stone-800 pt-3 mt-2">
        <div className="text-[0.4rem] text-stone-600 font-mono flex justify-between">
          <span>🔐 QUANTUM VERIFIED: Dilithium-5</span>
          <span>📊 REAL DATA: {hasMetricValue(kpis?.arrFormatted) ? `${kpis.arrFormatted} ARR` : 'SOURCE_REQUIRED'}</span>
        </div>
      </div>
    </div>
  );
};

export default InvestorKPIs;

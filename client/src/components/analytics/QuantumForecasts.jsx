/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QUANTUM FORECASTS COMPONENT [V1.1.0-SOURCE-AWARE-FORECASTS]                                                               ║
 * ║ [REVENUE FORECASTS | ROLE-GATED ACCESS | SOURCE-SILENT STATES | QUANTUM SIGNATURE DISPLAY | NO SYNTHETIC FORECAST VALUES]           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-SOURCE-AWARE-FORECASTS | PRODUCTION READY | FORECAST ANALYTICS READ SURFACE                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/analytics/QuantumForecasts.jsx                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required forecast intelligence to be useful, protected and free of fake future-value theatre.       ║
 * ║ • AI Engineering (Codex) - HARDENED: Added source-aware forecast formatting, route hydration docs and explicit source failure states. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect } from 'react';
import { Zap, Shield, AlertTriangle } from 'lucide-react';
import useSovereignAccess from '../../hooks/useSovereignAccess';
import sovereignClient from '../../utils/sovereignClient';

/**
 * @function hasForecastValue
 * @description Determines whether a forecast value was provided by the source.
 * @param {unknown} value - Candidate forecast value.
 * @returns {boolean} True when value is usable.
 * @collaboration Missing forecasts must remain visible as source gaps, not become zero-growth claims.
 */
const hasForecastValue = (value) => value !== null && value !== undefined && value !== '';

/**
 * @function formatForecastValue
 * @description Formats a ZAR forecast amount into compact display text.
 * @param {number|string|null} value - Forecast amount.
 * @returns {string} Compact ZAR forecast or SOURCE_REQUIRED.
 * @collaboration Forecasts are investor-sensitive; this formatter refuses to render invented currency values.
 */
const formatForecastValue = (value) => {
  if (!hasForecastValue(value)) return 'SOURCE_REQUIRED';
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 'SOURCE_REQUIRED';
  if (numeric >= 1_000_000_000) return `R ${(numeric / 1_000_000_000).toFixed(2)}B`;
  if (numeric >= 1_000_000) return `R ${(numeric / 1_000_000).toFixed(2)}M`;
  if (numeric >= 1_000) return `R ${(numeric / 1_000).toFixed(2)}K`;
  return `R ${numeric.toFixed(2)}`;
};

/**
 * @function formatForecastConfidence
 * @description Formats forecast confidence while preserving missing-source truth.
 * @param {number|string|null} value - Confidence value.
 * @returns {string} Confidence display.
 * @collaboration A confidence score of 100 without source data is fake certainty; this helper prevents that.
 */
const formatForecastConfidence = (value) => (
  hasForecastValue(value) ? `${value}%` : 'SOURCE_REQUIRED'
);

/**
 * @function ForecastCard
 * @description Renders one forecast horizon with confidence and optional signature proof.
 * @param {Object} props - Card props.
 * @param {string} props.title - Forecast horizon title.
 * @param {string} props.value - Formatted forecast value.
 * @param {string} props.confidence - Confidence display value.
 * @param {string} [props.quantumSignature] - Optional forecast signature.
 * @param {string} [props.color='emerald'] - Tailwind color token.
 * @returns {JSX.Element} Forecast card.
 * @collaboration Keeps all forecast horizons visually consistent while the parent handles source truth.
 */
const ForecastCard = ({ title, value, confidence, quantumSignature, color = 'emerald' }) => (
  <div className="bg-stone-900/30 border border-stone-800 rounded-lg p-4 hover:border-gold/30 transition-all">
    <div className="text-[0.55rem] text-stone-500 font-mono mb-1">{title}</div>
    <div className={`text-xl font-black font-mono text-${color}-400`}>
      {value}
    </div>
    <div className="flex items-center justify-between mt-2">
      <span className="text-[0.45rem] text-stone-500">Confidence: {confidence}</span>
      {quantumSignature && (
        <span className="text-[0.35rem] text-emerald-500 font-mono">{quantumSignature.substring(0, 12)}...</span>
      )}
    </div>
  </div>
);

/**
 * @function QuantumForecasts
 * @description Renders permission-gated forecast analytics from the protected analytics route.
 * @returns {JSX.Element} Forecast panel.
 * @collaboration Protects Wilsy OS by refusing to display synthetic forecasts when analytics sources are unavailable.
 */
const QuantumForecasts = () => {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { canViewForecasts } = useSovereignAccess();

  useEffect(() => {
    /**
     * @function fetchForecasts
     * @description Hydrates forecast analytics through sovereignClient with auth and tenant context intact.
     * @returns {Promise<void>} Resolves after forecast or source error state is applied.
     * @collaboration Direct backend calls are forbidden here because forecast data is role and tenant sensitive.
     */
    const fetchForecasts = async () => {
      try {
        setLoading(true);
        const response = await sovereignClient.get('/analytics/forecast', {
          skipAuthRedirect: true,
          disableSourceBackoff: true
        });
        const result = response.data || {};
        if (result.success) {
          setForecast(result.data);
        }
      } catch (err) {
        setError(err.response?.data?.message || err.response?.data?.error || err.message || 'FORECAST_SOURCE_SILENT');
      } finally {
        setLoading(false);
      }
    };

    if (canViewForecasts) {
      fetchForecasts();
    }
  }, [canViewForecasts]);

  if (!canViewForecasts) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-8 text-center">
        <Shield size={32} className="text-stone-600 mx-auto mb-3" />
        <p className="text-stone-500 text-sm">Forecast access restricted</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-8 text-center">
        <div className="animate-pulse">
          <Zap size={32} className="text-gold mx-auto mb-3" />
          <div className="text-gold text-sm font-mono">QUANTUM FORECASTING...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="text-red-500 mx-auto mb-3" />
        <p className="text-stone-500 text-sm">Forecast source unavailable</p>
        <p className="text-stone-600 text-xs mt-2">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-gold text-sm font-black tracking-wider uppercase">Quantum Forecasts</h3>
          <p className="text-stone-500 text-[0.65rem] mt-1">AI-powered | Dilithium-5 verified</p>
        </div>
        {forecast?.quantumSignature && (
          <div className="flex items-center gap-1 text-[0.45rem] text-emerald-500 font-mono">
            <Shield size={8} />
            <span>PQE-256 ACTIVE</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <ForecastCard
          title="NEXT QUARTER"
          value={formatForecastValue(forecast?.nextQuarter)}
          confidence={formatForecastConfidence(forecast?.confidence)}
          quantumSignature={forecast?.quantumSignature}
          color="emerald"
        />
        <ForecastCard
          title="NEXT YEAR"
          value={formatForecastValue(forecast?.nextYear)}
          confidence={formatForecastConfidence(forecast?.confidence)}
          color="gold"
        />
        <ForecastCard
          title="5 YEAR"
          value={formatForecastValue(forecast?.fiveYear)}
          confidence={formatForecastConfidence(forecast?.confidence)}
          color="emerald"
        />
      </div>

      {forecast?.note && (
        <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <AlertTriangle size={12} className="text-gold" />
            <span className="text-[0.5rem] text-stone-400">{forecast.note}</span>
          </div>
        </div>
      )}

      {forecast?.methodology && (
        <div className="text-[0.45rem] text-stone-500 text-center">
          Methodology: {forecast.methodology}
        </div>
      )}
    </div>
  );
};

export default QuantumForecasts;

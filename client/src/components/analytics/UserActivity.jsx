/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - USER ACTIVITY ANALYTICS COMPONENT [V1.1.0-SOURCE-AWARE-ACTIVITY]                                                          ║
 * ║ [TENANT USER ACTIVITY | ROLE-GATED VISIBILITY | SOURCE-SILENT STATES | FORENSIC HASH DISPLAY | NO FAKE ENGAGEMENT DATA]             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-SOURCE-AWARE-ACTIVITY | PRODUCTION READY | EXECUTIVE USER ACTIVITY READ SURFACE                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/analytics/UserActivity.jsx                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required Wilsy OS activity intelligence to be permissioned, monitored and never placeholder-driven. ║
 * ║ • AI Engineering (Codex) - HARDENED: Documented source-aware activity hydration and protected the component from fake user metrics.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect } from 'react';
import { AlertTriangle, Users, Activity, Clock, Eye } from 'lucide-react';
import useSovereignAccess from '../../hooks/useSovereignAccess';
import sovereignClient from '../../utils/sovereignClient';

/**
 * @function extractUserActivityPayload
 * @description Extracts the source payload returned by the analytics user-activity endpoint.
 * @param {Object} response - Axios response from sovereignClient.
 * @returns {Object|null} User activity payload or null when the source did not provide data.
 * @collaboration Future engineers must see that this component displays backend evidence only, not local demo data.
 */
const extractUserActivityPayload = (response = {}) => {
  const result = response.data || {};
  return result.success ? (result.data || null) : null;
};

/**
 * @function formatActivityMetric
 * @description Formats a user activity metric while preserving source gaps.
 * @param {number|string|null} value - Candidate metric value.
 * @param {string} suffix - Optional display suffix.
 * @returns {string} Metric display value.
 * @collaboration Engagement numbers are board-sensitive; missing sources must not become fake zeroes.
 */
const formatActivityMetric = (value, suffix = '') => {
  if (value === null || value === undefined || value === '') return 'SOURCE_REQUIRED';
  return `${value}${suffix}`;
};

/**
 * @function UserActivity
 * @description Renders role-gated tenant user activity analytics from the protected analytics API.
 * @returns {JSX.Element} Source-aware user activity panel.
 * @collaboration Protects Wilsy OS by showing activity only to authorized operators and declaring source failures clearly.
 */
const UserActivity = () => {
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { canViewUserActivity } = useSovereignAccess();

  useEffect(() => {
    /**
     * @function fetchActivity
     * @description Hydrates user activity through sovereignClient so auth, tenant headers and source-state handling stay centralized.
     * @returns {Promise<void>} Resolves when activity, source error or loading state has been applied.
     * @collaboration Direct localhost fetches bypassed Wilsy OS security controls; this function keeps the route protected.
     */
    const fetchActivity = async () => {
      try {
        const response = await sovereignClient.get('/analytics/users', {
          skipAuthRedirect: true,
          disableSourceBackoff: true
        });
        const payload = extractUserActivityPayload(response);
        setActivity(payload);
        if (!payload) setError('USER_ACTIVITY_SOURCE_SILENT');
      } catch (err) {
        setError(err.response?.data?.message || err.response?.data?.error || err.message || 'USER_ACTIVITY_SOURCE_SILENT');
      } finally {
        setLoading(false);
      }
    };

    if (canViewUserActivity) {
      fetchActivity();
    } else {
      setLoading(false);
    }
  }, [canViewUserActivity]);

  if (!canViewUserActivity) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-6 text-center">
        <Eye size={24} className="text-stone-600 mx-auto mb-2" />
        <p className="text-stone-500 text-xs">User activity restricted</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-6 text-center">
        <div className="animate-pulse">
          <Users size={24} className="text-gold mx-auto mb-2" />
          <div className="text-gold text-xs font-mono">LOADING...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-stone-900/50 border border-stone-800 rounded-lg p-6 text-center">
        <AlertTriangle size={24} className="text-red-500 mx-auto mb-2" />
        <p className="text-stone-500 text-xs">User activity source unavailable</p>
        <p className="text-stone-600 text-[0.6rem] mt-2">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-gold text-[0.7rem] font-black tracking-wider uppercase">User Activity</h4>
        {activity?.forensicHash && (
          <span className="text-[0.35rem] text-emerald-500 font-mono">🔐 {activity.forensicHash.substring(0, 12)}...</span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="bg-stone-900/30 border border-stone-800 rounded-lg p-3 text-center">
          <Users size={14} className="text-emerald-500 mx-auto mb-1" />
          <div className="text-xl font-black text-white">{formatActivityMetric(activity?.totalUsers)}</div>
          <div className="text-[0.45rem] text-stone-500">Total Users</div>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-lg p-3 text-center">
          <Activity size={14} className="text-emerald-500 mx-auto mb-1" />
          <div className="text-xl font-black text-white">{formatActivityMetric(activity?.activeToday)}</div>
          <div className="text-[0.45rem] text-stone-500">Active Today</div>
        </div>
        <div className="bg-stone-900/30 border border-stone-800 rounded-lg p-3 text-center">
          <Clock size={14} className="text-gold mx-auto mb-1" />
          <div className="text-xl font-black text-white">{formatActivityMetric(activity?.activePercentage, '%')}</div>
          <div className="text-[0.45rem] text-stone-500">Engagement</div>
        </div>
      </div>

      {activity?.activeThisWeek !== null && activity?.activeThisWeek !== undefined && (
        <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-2">
          <div className="flex justify-between text-[0.45rem]">
            <span className="text-stone-500">Active This Week</span>
            <span className="text-white font-mono">{formatActivityMetric(activity.activeThisWeek)}</span>
          </div>
        </div>
      )}

      <div className="text-[0.35rem] text-stone-600 text-center">
        Last updated: {activity?.lastUpdated ? new Date(activity.lastUpdated).toLocaleString() : 'N/A'}
      </div>
    </div>
  );
};

export default UserActivity;

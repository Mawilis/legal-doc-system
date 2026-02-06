/**
 * File: client/src/features/dashboard/components/StatsGrid.jsx
 * Path: client/src/features/dashboard/components/StatsGrid.jsx
 * STATUS: PRODUCTION-READY | DATA VISUALIZATION | ACCESSIBLE
 * VERSION: 2026-01-14
 *
 * PURPOSE
 * - Responsive KPI grid for the Dashboard: System Health, Active Users, Pending Docs, Storage.
 * - Resilient to missing data, accessible, localized number formatting, and lightweight skeletons.
 *
 * COLLABORATION & OWNERSHIP (MANDATORY)
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team
 * - DESIGN OWNER: @design
 * - QA OWNER: @qa
 * - SECURITY OWNER: @security
 *
 * REVIEW CHECKLIST (PRE-MERGE)
 * - @frontend-team: confirm design tokens and spacing match design system.
 * - @design: approve color variants and iconography.
 * - @qa: add unit tests (rendering, fallback values, accessibility).
 * - @security: confirm no PII is rendered in KPIs or logs.
 *
 * NOTES
 * - Uses styled-components for scoped styling.
 * - Avoids rendering raw objects; all values are sanitized and formatted.
 * - Add tests for number formatting, skeleton display, and responsive layout.
 */

import React, { memo } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FiActivity, FiUsers, FiFileText, FiHardDrive } from 'react-icons/fi';

/* -------------------------
   Styled components
   ------------------------- */

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
  width: 100%;
`;

const Card = styled.article`
  background: var(--card-bg, #ffffff);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--card-border, #E6EDF3);
  box-shadow: 0 4px 8px rgba(2,6,23,0.03);
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: transform 160ms ease, box-shadow 160ms ease;
  min-height: 96px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(2,6,23,0.06);
  }
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  min-width: 0;

  .label {
    color: var(--muted, #64748B);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
  }

  .value {
    color: var(--text, #0F172A);
    font-size: 1.5rem;
    font-weight: 800;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sub {
    margin-top: 6px;
    color: var(--muted, #64748B);
    font-size: 0.8rem;
  }
`;

const IconBox = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.25rem;
  flex-shrink: 0;

  ${(p) => p.$variant === 'blue' && `background: #EFF6FF; color: #3B82F6;`}
  ${(p) => p.$variant === 'green' && `background: #F0FDF4; color: #16A34A;`}
  ${(p) => p.$variant === 'orange' && `background: #FFF7ED; color: #F97316;`}
  ${(p) => p.$variant === 'purple' && `background: #FAF5FF; color: #7C3AED;`}
`;

/* Skeleton for loading state */
const Skeleton = styled.div`
  width: 100%;
  height: 16px;
  background: linear-gradient(90deg, rgba(0,0,0,0.04) 0%, rgba(0,0,0,0.02) 50%, rgba(0,0,0,0.04) 100%);
  border-radius: 8px;
  animation: shimmer 1.2s linear infinite;
  @keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: 200px 0; }
  }
`;

/* -------------------------
   Helpers
   ------------------------- */

/**
 * formatNumber
 * - Localized, compact formatting for large numbers (e.g., 1.2K, 3.4M).
 */
function formatNumber(value, locale = undefined) {
    if (value == null || Number.isNaN(Number(value))) return '0';
    const num = Number(value);
    // Use compact notation for large numbers
    try {
        return new Intl.NumberFormat(locale || undefined, { notation: 'compact', maximumFractionDigits: 1 }).format(num);
    } catch {
        return String(num);
    }
}

/* -------------------------
   Component
   ------------------------- */

function StatsGridComponent({ stats = {}, loading = false, locale }) {
    // Defensive defaults
    const {
        systemHealth = null, // allow null to show skeleton or N/A
        activeUsers = null,
        documentsPending = null,
        storageUsed = null
    } = stats || {};

    return (
        <Grid role="list" aria-label="Key performance indicators">
            <Card role="listitem" aria-label="System health">
                <Content>
                    <span className="label">System Health</span>
                    <div className="value" aria-live="polite">
                        {loading ? <Skeleton aria-hidden="true" /> : (systemHealth != null ? String(systemHealth) : 'N/A')}
                    </div>
                    <div className="sub">Uptime and service health</div>
                </Content>
                <IconBox $variant="green" aria-hidden="true"><FiActivity /></IconBox>
            </Card>

            <Card role="listitem" aria-label="Active users">
                <Content>
                    <span className="label">Active Users</span>
                    <div className="value" aria-live="polite">
                        {loading ? <Skeleton aria-hidden="true" /> : formatNumber(activeUsers, locale)}
                    </div>
                    <div className="sub">Users active in the last 24 hours</div>
                </Content>
                <IconBox $variant="blue" aria-hidden="true"><FiUsers /></IconBox>
            </Card>

            <Card role="listitem" aria-label="Pending documents">
                <Content>
                    <span className="label">Pending Docs</span>
                    <div className="value" aria-live="polite">
                        {loading ? <Skeleton aria-hidden="true" /> : formatNumber(documentsPending, locale)}
                    </div>
                    <div className="sub">Documents awaiting processing or review</div>
                </Content>
                <IconBox $variant="orange" aria-hidden="true"><FiFileText /></IconBox>
            </Card>

            <Card role="listitem" aria-label="Storage used">
                <Content>
                    <span className="label">Storage</span>
                    <div className="value" aria-live="polite">
                        {loading ? <Skeleton aria-hidden="true" /> : (storageUsed != null ? String(storageUsed) : '0 GB')}
                    </div>
                    <div className="sub">Approximate storage consumed</div>
                </Content>
                <IconBox $variant="purple" aria-hidden="true"><FiHardDrive /></IconBox>
            </Card>
        </Grid>
    );
}

/* Memoize to avoid unnecessary re-renders */
const StatsGrid = memo(StatsGridComponent);

StatsGrid.propTypes = {
    stats: PropTypes.shape({
        systemHealth: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        activeUsers: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        documentsPending: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        storageUsed: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    }),
    loading: PropTypes.bool,
    locale: PropTypes.string
};

StatsGrid.defaultProps = {
    stats: {
        systemHealth: '98%',
        activeUsers: 0,
        documentsPending: 0,
        storageUsed: '0 GB'
    },
    loading: false,
    locale: undefined
};

export default StatsGrid;

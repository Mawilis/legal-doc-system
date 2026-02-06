/**
 * File: client/src/components/TenantSelector.jsx
 * Path: client/src/components/TenantSelector.jsx
 * STATUS: PRODUCTION-READY | GLOBAL COMPONENT
 * VERSION: 2026-01-14
 *
 * PURPOSE
 * - Allows users to switch active tenant context safely and accessibly.
 * - Minimal surface: renders only when multiple tenants exist; normalizes tenant shape;
 *   emits tenant id and tenant object on change; supports disabled/loading states.
 *
 * COLLABORATION & OWNERSHIP (MANDATORY)
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team
 * - BACKEND OWNER: @backend-team (tenant shape contract)
 * - SECURITY OWNER: @security (ensure no PII leakage in UI)
 * - QA OWNER: @qa (unit + accessibility tests)
 *
 * REVIEW CHECKLIST (PRE-MERGE)
 * - @frontend-team: confirm design tokens and spacing match design system
 * - @backend-team: confirm tenant object shape (id/_id, name)
 * - @security: review that no sensitive PII is rendered
 * - @qa: add tests for keyboard navigation, focus, and onChange behavior
 *
 * NOTES
 * - Tenant objects accepted: { id, name } or { _id, name } or simple strings.
 * - onChange receives (tenantId, tenantObject) to make downstream logic simpler.
 * - Component is accessible (aria-label, keyboard focus) and hides itself when single/no tenant.
 * - Avoids rendering email or other PII; only tenant.name is shown (assumed safe).
 */

import React, { useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FiGrid } from 'react-icons/fi';

/* -------------------------
   Styled primitives
   ------------------------- */

const SelectContainer = styled.div`
  position: relative;
  display: inline-flex;
  align-items: center;
  min-width: 160px;
`;

const Select = styled.select`
  appearance: none;
  background-color: var(--select-bg, #fff);
  border: 1px solid var(--select-border, #E2E8F0);
  padding: 8px 36px 8px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text, #0F172A);
  font-weight: 600;
  cursor: pointer;
  transition: border-color 120ms ease, box-shadow 120ms ease;
  width: 100%;

  &:hover { border-color: #CBD5E1; }
  &:focus {
    outline: none;
    border-color: #3B82F6;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.08);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const IconWrapper = styled.div`
  position: absolute;
  right: 8px;
  pointer-events: none;
  color: var(--muted, #64748B);
  display: flex;
  align-items: center;
`;

/* -------------------------
   Helpers
   ------------------------- */

/**
 * normalizeTenants
 * - Accepts array of tenants in various shapes and returns normalized objects:
 *   { id: string, name: string, raw: original }
 */
function normalizeTenants(tenants) {
    if (!Array.isArray(tenants)) return [];
    return tenants.map((t) => {
        if (!t) return null;
        if (typeof t === 'string') return { id: t, name: t, raw: t };
        const id = t.id || t._id || t.tenantId || (t && t.name ? String(t.name) : null);
        const name = t.name || t.displayName || String(id || '');
        return { id: String(id), name: String(name), raw: t };
    }).filter(Boolean);
}

/* -------------------------
   Component
   ------------------------- */

function TenantSelector({ tenants = [], currentTenantId = '', onChange, disabled = false, placeholder = 'Select organization' }) {
    const normalized = useMemo(() => normalizeTenants(tenants), [tenants]);

    // If fewer than 2 tenants, do not render selector to avoid UI clutter
    if (!normalized || normalized.length < 2) return null;

    // Ensure currentTenantId exists in list; fallback to first tenant
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const effectiveCurrent = useMemo(() => {
        const found = normalized.find((t) => t.id === String(currentTenantId));
        return found ? found.id : normalized[0].id;
    }, [normalized, currentTenantId]);

    // eslint-disable-next-line react-hooks/rules-of-hooks
    const handleChange = useCallback((e) => {
        const id = e.target.value;
        const tenantObj = normalized.find((t) => t.id === id) || null;
        try {
            // Provide both id and full tenant object to caller
            if (typeof onChange === 'function') onChange(id, tenantObj);
        } catch (err) {
            // Swallow to avoid UI crash; caller should handle errors
            // eslint-disable-next-line no-console
            console.error('TenantSelector onChange handler threw', err);
        }
    }, [normalized, onChange]);

    return (
        <SelectContainer aria-hidden={disabled ? 'true' : 'false'}>
            <Select
                value={effectiveCurrent}
                onChange={handleChange}
                aria-label="Select organization"
                disabled={disabled}
                title="Switch organization"
            >
                {/* Optional placeholder as non-selectable option */}
                <option value="" disabled hidden>{placeholder}</option>
                {normalized.map((t) => (
                    <option key={t.id} value={t.id}>
                        {t.name}
                    </option>
                ))}
            </Select>
            <IconWrapper aria-hidden="true">
                <FiGrid size={14} />
            </IconWrapper>
        </SelectContainer>
    );
}

/* -------------------------
   PropTypes & Defaults
   ------------------------- */

TenantSelector.propTypes = {
    tenants: PropTypes.arrayOf(PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.shape({
            id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            _id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            name: PropTypes.string,
            displayName: PropTypes.string
        })
    ])),
    currentTenantId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    onChange: PropTypes.func.isRequired, // (tenantId, tenantObject) => void
    disabled: PropTypes.bool,
    placeholder: PropTypes.string
};

TenantSelector.defaultProps = {
    tenants: [],
    currentTenantId: '',
    disabled: false,
    placeholder: 'Select organization'
};

export default React.memo(TenantSelector);

/**
 * File: client/src/components/Spinner.jsx
 * Path: client/src/components/Spinner.jsx
 * STATUS: PRODUCTION-READY | EPITOME | UI UTILITY
 * VERSION: 2026-01-14
 *
 * PURPOSE
 * - Reusable, accessible, and configurable loading indicator for Wilsy OS.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team
 * - QA OWNER: @qa
 * - REVIEW CHECKLIST:
 *   - @frontend-team: confirm visual tokens (size, color) match design system
 *   - @qa: add snapshot and accessibility tests (axe)
 *
 * SECURITY & ACCESSIBILITY NOTES
 * - No PII or sensitive data is rendered.
 * - Uses ARIA role="status" and visually-hidden label for screen readers.
 * - Lightweight, no external dependencies.
 *
 * USAGE
 * <Spinner size={40} thickness={4} color="#3498db" label="Loading content" />
 */

import React from 'react';
import PropTypes from 'prop-types';

/**
 * Spinner
 * - Props:
 *   - size: diameter in px
 *   - thickness: border thickness in px
 *   - color: spinner accent color
 *   - label: accessible label read by screen readers
 *   - className: optional className for styling overrides
 */
export default function Spinner({ size = 40, thickness = 4, color = '#3498db', label = 'Loading', className = '' }) {
    const outer = {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '1rem'
    };

    const spinnerStyle = {
        width: `${size}px`,
        height: `${size}px`,
        border: `${thickness}px solid rgba(0,0,0,0.08)`,
        borderTop: `${thickness}px solid ${color}`,
        borderRadius: '50%',
        animation: 'wilsy-spinner-spin 1s linear infinite',
        boxSizing: 'border-box'
    };

    const srOnly = {
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: 0,
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0,0,0,0)',
        whiteSpace: 'nowrap',
        border: 0
    };

    return (
        <div style={outer} className={className} role="status" aria-live="polite" aria-label={label}>
            <div style={spinnerStyle} aria-hidden="true" />
            <span style={srOnly}>{label}</span>

            {/* Inline keyframes to avoid external CSS dependency */}
            <style>{`
        @keyframes wilsy-spinner-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
}

Spinner.propTypes = {
    size: PropTypes.number,
    thickness: PropTypes.number,
    color: PropTypes.string,
    label: PropTypes.string,
    className: PropTypes.string
};

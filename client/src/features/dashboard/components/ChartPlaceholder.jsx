/**
 * File: client/src/features/dashboard/components/ChartPlaceholder.jsx
 * Path: client/src/features/dashboard/components/ChartPlaceholder.jsx
 * STATUS: PRODUCTION-READY | DASHBOARD UI | ACCESSIBLE
 * VERSION: 2026-01-14
 *
 * PURPOSE
 * - Lightweight, accessible placeholder for charts while data loads.
 * - Provides consistent sizing, skeleton state, and clear ARIA semantics.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team
 * - DESIGN OWNER: @design
 * - QA OWNER: @qa
 * - REVIEW CHECKLIST:
 *   - @frontend-team: confirm tokens and spacing match design system
 *   - @design: approve iconography and copy
 *   - @qa: add snapshot and accessibility tests (axe)
 *   - @security: ensure no PII is rendered
 *
 * NOTES
 * - Keep this component dependency-free beyond styled-components and react-icons.
 * - Use `loading` prop to show animated skeleton; `height` and `minHeight` are configurable.
 * - Does not attempt to render real chart content; callers should replace with actual chart component when data arrives.
 */

import React from 'react';
import PropTypes from 'prop-types';
import styled, { keyframes } from 'styled-components';
import { FiBarChart2 } from 'react-icons/fi';

/* -------------------------
   Animations & tokens
   ------------------------- */

const shimmer = keyframes`
  0% { background-position: -200px 0; }
  100% { background-position: 200px 0; }
`;

/* -------------------------
   Styled primitives
   ------------------------- */

const Container = styled.div`
  width: 100%;
  min-height: ${(p) => p.minHeight}px;
  height: ${(p) => p.height}px;
  background: var(--chart-placeholder-bg, #F8FAFC);
  border: 2px dashed var(--chart-placeholder-border, #E2E8F0);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--muted, #94A3B8);
  transition: background 0.18s ease;
  box-sizing: border-box;
  padding: 16px;
  position: relative;

  &:hover {
    background: var(--chart-placeholder-hover, #F1F5F9);
  }
`;

const Message = styled.p`
  margin-top: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--muted, #94A3B8);
`;

/* Skeleton bar used when loading */
const SkeletonBar = styled.div`
  width: 60%;
  height: 12px;
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(0,0,0,0.04) 0%, rgba(0,0,0,0.02) 50%, rgba(0,0,0,0.04) 100%);
  background-size: 400px 100%;
  animation: ${shimmer} 1.2s linear infinite;
`;

/* Small caption under skeleton */
const SkeletonCaption = styled.div`
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--muted, #94A3B8);
`;

/* -------------------------
   Component
   ------------------------- */

export default function ChartPlaceholder({
    title = 'Data Visualization',
    loading = true,
    height = 300,
    minHeight = 200,
    ariaLabel = 'Chart placeholder'
}) {
    return (
        <Container role="region" aria-label={ariaLabel} height={height} minHeight={minHeight}>
            <FiBarChart2 size={36} aria-hidden="true" />
            {loading ? (
                <>
                    <SkeletonBar aria-hidden="true" />
                    <SkeletonCaption aria-hidden="true">Loading {title}…</SkeletonCaption>
                    <span style={{
                        position: 'absolute',
                        left: '-9999px',
                        width: '1px',
                        height: '1px',
                        overflow: 'hidden'
                    }}>Loading chart content</span>
                </>
            ) : (
                <Message>{title} Loading...</Message>
            )}
        </Container>
    );
}

ChartPlaceholder.propTypes = {
    /** Title shown in the placeholder and used in accessible text */
    title: PropTypes.string,
    /** When true, show animated skeleton; when false, show static message */
    loading: PropTypes.bool,
    /** Height in px for the placeholder area */
    height: PropTypes.number,
    /** Minimum height in px */
    minHeight: PropTypes.number,
    /** ARIA label for the region */
    ariaLabel: PropTypes.string
};

ChartPlaceholder.defaultProps = {
    title: 'Data Visualization',
    loading: true,
    height: 300,
    minHeight: 200,
    ariaLabel: 'Chart placeholder'
};

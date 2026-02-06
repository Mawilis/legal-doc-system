/*
 * File: client/src/components/layout/AuthLayout.jsx
 * STATUS: PRODUCTION-READY | EPITOME | PUBLIC GATEWAY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * The Authoritative Authentication Shell for Wilsy OS.
 * - Investor-grade glassmorphism and authority gradients.
 * - Forensic-grade accessibility (ARIA regions, keyboard UX).
 * - High-fidelity brand storytelling for public-facing gateways.
 * -----------------------------------------------------------------------------
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - WORTH: Biblical | Worth Billions | No Child's Place.
 * - DESIGN: Implements radial depth and "Glass-Saturate" effects.
 * - COMPLIANCE: Includes explicit legal disclosure hooks and i18n mapping.
 * -----------------------------------------------------------------------------
 * REVIEWERS: @design, @security, @platform, @accessibility
 * TESTS: jest + @testing-library/react — ensures brand & form pane presence.
 * -----------------------------------------------------------------------------
 */

'use client';

import React, { Suspense, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import styled from 'styled-components';
import { ShieldCheck, Zap, Users } from 'lucide-react';

/**
 * BRANDING ASSETS
 * Ensure these paths are synchronized with your Vite/Webpack assets folder.
 */
import wilsyLogo from '../../assets/branding/wilsy_logo.png';

/* -------------------------
   SOVEREIGN THEME TOKENS
   - Radial and Linear gradients optimized for "Vault" aesthetic.
   ------------------------- */
const Shell = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(1200px 600px at 10% 10%, rgba(0,163,224,0.06), transparent 8%),
              linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 24px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #e6eef8;
`;

/* Container: Glassmorphism Architecture */
const Container = styled.section`
  width: 100%;
  max-width: 1100px;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
  backdrop-filter: blur(18px) saturate(120%);
  -webkit-backdrop-filter: blur(18px) saturate(120%);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 40px 120px -30px rgba(2,6,23,0.7);
  align-items: stretch;

  @media (max-width: 960px) {
    grid-template-columns: 1fr;
    max-width: 520px;
    border-radius: 20px;
  }
`;

/* Brand Pane: Left Column Storytelling */
const BrandPane = styled.aside`
  padding: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(225deg, rgba(37,99,235,0.08) 0%, rgba(0,163,224,0.02) 100%);
  color: #ffffff;

  .logo {
    height: 56px;
    width: auto;
    margin-bottom: 28px;
    display: block;
  }

  h1 {
    font-size: 2.25rem;
    font-weight: 900;
    margin: 0 0 12px 0;
    line-height: 1.02;
    letter-spacing: -0.6px;
    background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  p {
    font-size: 1.05rem;
    line-height: 1.6;
    color: rgba(226,232,240,0.9);
    margin: 0 0 28px 0;
    max-width: 36ch;
  }

  .features {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 8px;
  }

  @media (max-width: 960px) {
    display: none;
  }
`;

const FeatureItem = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 0.95rem;
  font-weight: 700;
  color: rgba(226,232,240,0.95);

  .icon-box {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(180deg, rgba(37,99,235,0.14), rgba(0,163,224,0.06));
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #60a5fa;
    flex-shrink: 0;
  }
`;

/* Form Pane: Right Column Interaction */
const FormPane = styled.main`
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.98));
  padding: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #0f172a;

  @media (max-width: 640px) {
    padding: 32px 20px;
  }
`;

const FormHeader = styled.header`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;

  .mini-logo {
    height: 36px;
    width: auto;
  }

  h2 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 800;
    color: #0b2546;
  }

  p {
    margin: 6px 0 0 0;
    color: #475569;
    font-size: 0.95rem;
  }
`;

const Legal = styled.div`
  margin-top: 20px;
  font-size: 0.85rem;
  color: #64748b;

  a {
    color: #0b3d91;
    text-decoration: underline;
    font-weight: 600;
  }
`;

const VisuallyHidden = styled.span`
  border: 0;
  clip: rect(0 0 0 0);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
`;

/* -------------------------
   I18N CONTENT STRINGS
   ------------------------- */
const strings = {
  title: 'Securing Justice, Digitally.',
  subtitle: 'The most sophisticated OS for modern legal practitioners. Forensic-grade document handling meets high-speed collaboration.',
  features: [
    { key: 'compliance', label: 'POPIA & GDPR Forensic Compliance' },
    { key: 'tracking', label: 'Real-time Sheriff & Service Tracking' },
    { key: 'multi', label: 'Multi-Tenant Firm Sovereignty' }
  ],
  disclosure: 'By continuing you agree to Wilsy OS Terms & Conditions.',
  termsUrl: process.env.REACT_APP_TERMS_URL || '#'
};

/* -------------------------
   AUTH LAYOUT COMPONENT
   ------------------------- */
export default function AuthLayout() {
  /**
   * FOCUS ORCHESTRATION
   * Ensures the viewport is ready for interaction immediately upon arrival.
   */
  useEffect(() => {
    const main = document.querySelector('[data-wilsy-auth-main]');
    if (main) main.focus();
  }, []);

  return (
    <Shell>
      <Container role="region" aria-label="Authentication gateway">

        {/* BRAND PANE: The Visionary Introduction */}
        <BrandPane role="complementary" aria-labelledby="wilsy-brand-heading">
          <img src={wilsyLogo} alt="Wilsy logo" className="logo" loading="eager" />
          <h1 id="wilsy-brand-heading">{strings.title}</h1>
          <p>{strings.subtitle}</p>

          <div className="features" aria-hidden="false">
            <FeatureItem>
              <div className="icon-box" aria-hidden="true"><ShieldCheck size={18} /></div>
              {strings.features[0].label}
            </FeatureItem>

            <FeatureItem>
              <div className="icon-box" aria-hidden="true"><Zap size={18} /></div>
              {strings.features[1].label}
            </FeatureItem>

            <FeatureItem>
              <div className="icon-box" aria-hidden="true"><Users size={18} /></div>
              {strings.features[2].label}
            </FeatureItem>
          </div>
        </BrandPane>

        {/* FORM PANE: The Transactional Gateway */}
        <FormPane role="main" aria-label="Authentication flow" data-wilsy-auth-main tabIndex={-1}>
          <FormHeader>
            <img src={wilsyLogo} alt="Wilsy mini logo" className="mini-logo" />
            <div>
              <h2>Welcome to Wilsy OS</h2>
              <p>Access your secure workspace</p>
            </div>
          </FormHeader>

          {/* DYNAMIC CONTENT OUTLET (Login / Register / Forgot) */}
          <Suspense fallback={<div aria-live="polite" className="text-slate-400">Loading authentication…</div>}>
            <Outlet />
          </Suspense>

          {/* LEGAL COMPLIANCE FOOTER */}
          <Legal aria-live="polite">
            {strings.disclosure}{' '}
            <a href={strings.termsUrl} target="_blank" rel="noopener noreferrer">Terms & Conditions</a>
          </Legal>

          <VisuallyHidden aria-hidden="true">Wilsy OS Authentication Shell Entry</VisuallyHidden>
        </FormPane>

      </Container>
    </Shell>
  );
}

/* -------------------------
   ARCHITECTURAL NOTES:
   - Asset Management: Ensure wilsyLogo is accessible via the relative path provided.
   - Component Tree: The Outlet renders LoginForm, which should be self-contained.
   - Compliance: TermsUrl should be mapped to the legal firm's governance page.
   ------------------------- */
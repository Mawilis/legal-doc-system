/* eslint-disable */
/**
 * 🏛️ WILSY OS - SOVEREIGN CRISIS COMMAND TEST SUITE
 * @version 1.0.3
 * @epitome BIBLICAL WORTH BILLIONS | 101/10 TEST COVERAGE
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { expect, test, describe, beforeEach } from 'vitest';
import Sovereign_Crisis_Command from '../../src/components/sovereign/Sovereign_Crisis_Command';

describe('🏛️ Sovereign Crisis Command - Institutional Test Suite', () => {
  describe('[LAYER_1] Base Render & Structural Integrity', () => {
    beforeEach(() => {
      render(<Sovereign_Crisis_Command />);
    });

    test('[1.1] Renders the main header with crisis command title', () => {
      const header = screen.getByTestId('crisis-header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveTextContent('SOVEREIGN CRISIS COMMAND');
    });

    test('[1.2] Displays all four status dashboard metrics', () => {
      expect(screen.getByTestId('metric-incidents')).toBeInTheDocument();
      expect(screen.getByTestId('metric-response')).toBeInTheDocument();
      expect(screen.getByTestId('metric-status')).toBeInTheDocument();
      expect(screen.getByTestId('metric-recovery')).toBeInTheDocument();
    });

    test('[1.3] Shows correct initial metric values', () => {
      expect(screen.getByTestId('incidents-count')).toHaveTextContent('4');
      expect(screen.getByTestId('response-time')).toHaveTextContent('2.4s');
      expect(screen.getByTestId('system-status')).toHaveTextContent('DEGRADED');
      expect(screen.getByTestId('recovery-eta')).toHaveTextContent('00:47:32');
    });
  });

  describe('[LAYER_2] Incident Severity & Classification', () => {
    beforeEach(() => {
      render(<Sovereign_Crisis_Command />);
    });

    test('[2.1] All severity levels display correctly', () => {
      // FIX: Use getAllByText for elements that appear multiple times
      const criticalElements = screen.getAllByText('CRITICAL');
      expect(criticalElements.length).toBe(2);

      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    });

    test('[2.2] Critical count shows correctly in metrics', () => {
      expect(screen.getByTestId('critical-count')).toHaveTextContent('2 CRITICAL');
    });
  });

  describe('[LAYER_3] Incident Data & Details', () => {
    beforeEach(() => {
      render(<Sovereign_Crisis_Command />);
    });

    test('[3.1] Displays all incident titles', () => {
      expect(screen.getByText('UNAUTHORIZED ACCESS ATTEMPT')).toBeInTheDocument();
      expect(screen.getByText('COMPLIANCE THRESHOLD ALERT')).toBeInTheDocument();
      expect(screen.getByText('ANOMALOUS TRAFFIC PATTERN')).toBeInTheDocument();
      expect(screen.getByText('CERTIFICATE EXPIRING')).toBeInTheDocument();
    });

    test('[3.2] Timestamps display correctly', () => {
      // FIX: Use test IDs instead of text matching
      expect(screen.getByTestId('incident-1-time')).toHaveTextContent('Time: 10:47:23');
      expect(screen.getByTestId('incident-2-time')).toHaveTextContent('Time: 10:32:15');
      expect(screen.getByTestId('incident-3-time')).toHaveTextContent('Time: 09:58:44');
      expect(screen.getByTestId('incident-4-time')).toHaveTextContent('Time: 08:12:30');
    });
  });

  describe('[LAYER_4] Emergency Protocols', () => {
    beforeEach(() => {
      render(<Sovereign_Crisis_Command />);
    });

    test('[4.1] Emergency Protocols section renders', () => {
      expect(screen.getByTestId('protocols-section')).toBeInTheDocument();
    });

    test('[4.2] All three protocols display', () => {
      expect(screen.getByText('SOVEREIGN LOCKDOWN')).toBeInTheDocument();
      expect(screen.getByText('EMERGENCY RECOVERY')).toBeInTheDocument();
      expect(screen.getByText('FORENSIC CAPTURE')).toBeInTheDocument();
    });

    test('[4.3] Protocol cards have unique test IDs', () => {
      const protocolCards = screen.getAllByTestId(/^protocol-.+-card$/);
      expect(protocolCards.length).toBe(3);
    });
  });
});

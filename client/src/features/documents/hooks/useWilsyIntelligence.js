/**
 * Copyright (c) 2025 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * All Rights Reserved.
 */
import { useState, useEffect } from 'react';

export const useWilsyIntelligence = (documentData) => {
  const [intelligence, setIntelligence] = useState({
    billing: null,
    risk: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    if (!documentData) return;

    const fetchIntelligence = async () => {
      try {
        // 1. Fetch Real-time Billing from Port 3001 (Gateway)
        const billRes = await fetch('http://localhost:3001/api/billing/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: documentData.serviceType || 'service_summons',
            distanceKm: documentData.distanceKm || 0,
            isUrgent: documentData.urgency === 'urgent'
          })
        });
        const billingData = await billRes.json();

        // 2. Fetch AI Risk Score from Port 3001 (Gateway)
        const riskRes = await fetch('http://localhost:3001/api/ai/risk-score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            area: documentData.serviceAddress,
            defendantHistory: documentData.defendantStatus || 'unknown'
          })
        });
        const riskData = await riskRes.json();

        setIntelligence({
          billing: billingData,
          risk: riskData,
          loading: false,
          error: null
        });
      } catch (err) {
        setIntelligence(prev => ({ ...prev, loading: false, error: err.message }));
      }
    };

    fetchIntelligence();
  }, [documentData]);

  return intelligence;
};

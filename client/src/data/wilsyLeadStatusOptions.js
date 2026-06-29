/* eslint-disable */

export const WILSY_LEAD_STATUS_OPTIONS = Object.freeze([
  { value: "NEW", label: "New", posture: "INTAKE" },
  { value: "PROSPECTING", label: "Prospecting", posture: "ACTIVE_PIPELINE" },
  { value: "CONTACTED", label: "Contacted", posture: "ACTIVE_PIPELINE" },
  { value: "ENGAGED", label: "Engaged", posture: "ACTIVE_PIPELINE" },
  { value: "QUALIFIED", label: "Qualified", posture: "QUALIFIED_PIPELINE" },
  { value: "NEEDS_REVIEW", label: "Needs Review", posture: "GOVERNANCE_REVIEW" },
  { value: "PROPOSAL", label: "Proposal", posture: "REVENUE_STAGE" },
  { value: "NEGOTIATION", label: "Negotiation", posture: "REVENUE_STAGE" },
  { value: "CONVERTED", label: "Converted", posture: "WON" },
  { value: "NURTURE", label: "Nurture", posture: "LONG_CYCLE" },
  { value: "ON_HOLD", label: "On Hold", posture: "PAUSED" },
  { value: "LOST", label: "Lost", posture: "CLOSED" },
  { value: "DISQUALIFIED", label: "Disqualified", posture: "CLOSED" }
]);

/**
 * @function normalizeWilsyLeadStatusValue
 * @description Normalizes a CRM Lead status value into the governed Wilsy status code.
 * @collaboration Used by the Lead edit surface before sending a backend-governed status update.
 */
export function normalizeWilsyLeadStatusValue(value = "") {
  const normalizedValue = String(value || "")
    .trim()
    .replace(/[\s-]+/g, "_")
    .toUpperCase();

  const exactMatch = WILSY_LEAD_STATUS_OPTIONS.find((option) => option.value === normalizedValue);

  if (exactMatch) {
    return exactMatch.value;
  }

  const labelMatch = WILSY_LEAD_STATUS_OPTIONS.find(
    (option) => option.label.toUpperCase() === String(value || "").trim().toUpperCase()
  );

  return labelMatch?.value || "PROSPECTING";
}

/**
 * @function formatWilsyLeadStatusLabel
 * @description Converts a governed CRM Lead status code into a readable operator label.
 * @collaboration Keeps the edit cockpit readable while preserving backend status discipline.
 */
export function formatWilsyLeadStatusLabel(value = "") {
  const normalizedValue = normalizeWilsyLeadStatusValue(value);
  const status = WILSY_LEAD_STATUS_OPTIONS.find((option) => option.value === normalizedValue);

  return status?.label || "Prospecting";
}

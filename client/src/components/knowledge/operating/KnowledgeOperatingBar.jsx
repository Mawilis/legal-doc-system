/* eslint-disable */
/**
 * WILSY OS - KNOWLEDGE OPERATING BAR [FG108O4B-PRODUCTION]
 * VERSION: 1.0.0-KNOWLEDGE-OPERATING-ROOM
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/knowledge/operating/KnowledgeOperatingBar.jsx
 * PURPOSE: Own the consolidated Knowledge Base operating bar so title authority, search, stats,
 * live suggestions, workspace return, trust posture, and search status render as one auditable
 * command surface instead of fragmented top-page regions.
 * COLLABORATION: Wilson Khanyezi mandated JSX ownership consolidation for the Knowledge Operating
 * Room. Codex implemented the single-bar component while preserving WilsyKnowledgeBaseVault state,
 * backend evidence language, dynamic suggestions, and route-return authority.
 */

import React, { useMemo, useState } from 'react';
import {
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  Info,
  RefreshCw,
  Search,
  ShieldCheck,
  X,
} from 'lucide-react';
import styles from './KnowledgeOperatingBar.module.css';

/**
 * @function KnowledgeOperatingBar
 * @description Renders the consolidated Knowledge Base operating bar from parent-owned Vault state, search handlers, dynamic suggestions, authority labels, and live status copy.
 * @param {object} props Search state, authority labels, return command, suggestion rows, status labels, and selected artifact posture.
 * @returns {JSX.Element} Consolidated Knowledge Operating Bar.
 * @collaboration WilsyKnowledgeBaseVault calls this component; knowledgeBaseVaultRoutes supply the Vault payload; preserve dynamic suggestions, parent-owned search state, and customer-safe evidence language.
 */
export default function KnowledgeOperatingBar({
  query = '',
  onQueryChange = () => undefined,
  onSubmitSearch = () => undefined,
  onClearSearch = () => undefined,
  onRefresh = () => undefined,
  loading = false,
  matchesCount = 0,
  libraryLabel = 'Knowledge Base Manifest',
  authoritySourceLabel = 'Verified library',
  authorityAccessLabel = 'Permissioned access',
  originLabel = 'Return to CRM',
  originRoute = '/crm',
  onReturn = () => undefined,
  suggestions = [],
  selectedTitle = 'Awaiting artifact',
  selectedOwner = 'Verified owner required',
  trustPosture = 'Permissioned',
  submittedQuery = '',
  activeCategoryLabel = 'All categories',
}) {
  const [activeBadgeId, setActiveBadgeId] = useState('');
  const hasLiveSuggestions = String(query || '').trim().length > 0 && suggestions.length > 0;
  const artifactLabel = `${matchesCount} artifact${matchesCount === 1 ? '' : 's'} ready`;
  const statusLabel = loading
    ? 'Searching the sovereign library'
    : matchesCount === 0
      ? 'No verified knowledge match'
      : matchesCount === 1
        ? '1 verified artifact ready'
        : `${matchesCount} verified artifacts ready`;
  const searchSignal = String(query || submittedQuery || '').trim();
  const badgeRows = useMemo(() => ([
    {
      id: 'matches',
      label: 'Matches',
      value: String(matchesCount),
      detail: statusLabel,
    },
    {
      id: 'library',
      label: 'Library',
      value: libraryLabel,
      detail: 'Saved Knowledge Base manifest and proof-backed artifact index.',
    },
    {
      id: 'verification',
      label: 'Verification',
      value: 'Verified',
      detail: 'Source evidence is checked before the artifact appears in this workspace.',
    },
    {
      id: 'access',
      label: 'Access',
      value: authorityAccessLabel,
      detail: `${authoritySourceLabel}. ${activeCategoryLabel}.`,
    },
    {
      id: 'selected',
      label: 'Selected',
      value: selectedTitle,
      detail: `${selectedOwner}. ${trustPosture}.`,
    },
  ]), [
    activeCategoryLabel,
    authorityAccessLabel,
    authoritySourceLabel,
    libraryLabel,
    matchesCount,
    selectedOwner,
    selectedTitle,
    statusLabel,
    trustPosture,
  ]);
  const activeBadge = badgeRows.find((badge) => badge.id === activeBadgeId) || null;
  const primarySignals = useMemo(() => ([
    { label: 'Matches', value: String(matchesCount) },
    { label: 'Verify', value: trustPosture },
  ]), [matchesCount, trustPosture]);

  /**
   * @function toggleBadgePanel
   * @description Toggles on-demand Knowledge Base authority badge details without expanding the default workspace chrome.
   * @param {string} badgeId Badge identifier.
   * @returns {void}
   * @collaboration KnowledgeOperatingBar badges, WilsyKnowledgeBaseVault compact workspace, and on-request metadata disclosure.
   */
  function toggleBadgePanel(badgeId = '') {
    setActiveBadgeId((currentBadgeId) => (currentBadgeId === badgeId ? '' : badgeId));
  }

  return (
    <section
      className={styles.knowledgeOperatingBar}
      aria-label="Wilsy Knowledge Base operating bar"
      data-wilsy-knowledge-operating-bar="FG108O4B_JSX_CONSOLIDATED"
    >
      <div className={styles.topAppBar}>
        <button type="button" className={styles.originReturnCommand} onClick={onReturn}>
          <ArrowLeft size={16} aria-hidden="true" />
          <span>{originLabel}</span>
        </button>

        <div className={styles.titleCell}>
          <span>Wilsy OS Knowledge Base</span>
          <strong>{selectedTitle !== 'Awaiting artifact' ? selectedTitle : 'Knowledge workspace'}</strong>
        </div>

        <label className={styles.searchBox}>
          <Search size={16} aria-hidden="true" />
          <input
            type="search"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault();
                onSubmitSearch();
              }
            }}
            placeholder="Ask or search verified operating knowledge, releases, owners, proof, fingerprints, or training guidance"
            aria-label="Search Wilsy Knowledge Base documents"
          />
          {searchSignal ? (
            <button
              type="button"
              className={styles.clearSearchButton}
              onClick={onClearSearch}
              aria-label="Clear Knowledge Base search"
            >
              <X size={15} aria-hidden="true" />
            </button>
          ) : null}
        </label>

        <button type="button" className={styles.searchButton} onClick={onSubmitSearch}>
          <Search size={16} aria-hidden="true" />
          Search
        </button>

        <button type="button" className={styles.refreshButton} onClick={onRefresh}>
          <RefreshCw size={16} aria-hidden="true" />
          Refresh
        </button>

        <div className={styles.signalCluster} aria-label="Knowledge Base compact status">
          {primarySignals.map((signal) => (
            <span key={signal.label} className={styles.signalPill}>
              <small>{signal.label}</small>
              <strong>{signal.value}</strong>
            </span>
          ))}
          <button
            type="button"
            className={styles.detailToggleButton}
            onClick={() => toggleBadgePanel(activeBadgeId ? '' : 'library')}
            aria-expanded={Boolean(activeBadge)}
            aria-controls="wilsy-knowledge-operating-details"
          >
            <Info size={13} aria-hidden="true" />
            <span>Details</span>
            {activeBadge ? <ChevronUp size={13} aria-hidden="true" /> : <ChevronDown size={13} aria-hidden="true" />}
          </button>
        </div>
      </div>

      {activeBadge ? (
        <div className={styles.badgeDetailPanel} aria-live="polite" id="wilsy-knowledge-operating-details">
          <div className={styles.badgeDetailSummary}>
            <ShieldCheck size={15} aria-hidden="true" />
            <strong>{activeBadge.label}: {activeBadge.value}</strong>
            <span>{activeBadge.detail}</span>
            <small>{originRoute}</small>
            <button
              type="button"
              className={styles.closeDetailButton}
              onClick={() => toggleBadgePanel('')}
              aria-label="Hide Knowledge Base operating details"
            >
              <X size={14} aria-hidden="true" />
            </button>
          </div>
          <div className={styles.badgeDetailPicker} aria-label="Knowledge Base detail topics">
            {badgeRows.map((badge) => (
              <button
                type="button"
                key={badge.id}
                className={activeBadgeId === badge.id ? styles.badgeButtonActive : styles.badgeButton}
                onClick={() => toggleBadgePanel(badge.id)}
                aria-expanded={activeBadgeId === badge.id}
              >
                <span>{badge.label}</span>
                <strong>{badge.value}</strong>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {hasLiveSuggestions ? (
        <div className={styles.suggestionRow} aria-label="Live Knowledge Base suggestions">
          <span>Live matches</span>
          <div role="listbox" aria-label="Instant Knowledge Base matches">
            {suggestions.map((entry) => (
              <button
                type="button"
                key={entry.key}
                className={styles.liveKnowledgeSuggestion}
                role="option"
                aria-selected={entry.selected}
                onClick={entry.onSelect}
              >
                <strong>{entry.title}</strong>
                <small>{entry.detail}</small>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <div className={styles.statusRow} aria-live="polite" aria-label="Vault backend search status">
        <strong>{loading ? 'Verifying' : artifactLabel}</strong>
        <span>
          {searchSignal ? `Live signal: ${searchSignal}` : 'All saved knowledge'} | {activeCategoryLabel}
        </span>
      </div>
    </section>
  );
}

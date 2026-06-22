/* eslint-disable */
/**
 * WILSY OS - GLOBAL COMMAND SEARCH BRIDGE [V1.0.0-SOVEREIGN-SEARCH]
 * Absolute Path: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/WilsyGlobalCommandSearch.jsx
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowRight,
  Building2,
  Crown,
  CreditCard,
  FileText,
  FolderOpen,
  LayoutDashboard,
  Search,
  ShieldCheck,
  Terminal,
  Users,
  X
} from 'lucide-react';

const WILSY_SEARCH_REGISTRY = Object.freeze([
  { id: 'founder', label: 'Founder Dashboard', type: 'Dashboard', dashboardKey: 'FOUNDER_DASHBOARD', route: '/founder', keywords: 'founder root omega sovereign admin command center', icon: Crown },
  { id: 'executive', label: 'Executive Dashboard', type: 'Dashboard', dashboardKey: 'EXECUTIVE_DASHBOARD', route: '/executive', keywords: 'ceo executive boardroom arr kpi decision command', icon: LayoutDashboard },
  { id: 'hr', label: 'People and HR', type: 'Vertical System', dashboardKey: 'HR_DASHBOARD', route: '/hr', keywords: 'employees people payroll benefits performance time off recruitment', icon: Users },
  { id: 'crm', label: 'CRM and Customers', type: 'Vertical System', dashboardKey: 'CRM_DASHBOARD', route: '/crm', keywords: 'clients customers leads accounts deals contacts pipeline', icon: Building2 },
  { id: 'finance', label: 'Finance Dashboard', type: 'Vertical System', dashboardKey: 'FINANCE_DASHBOARD', route: '/finance', keywords: 'finance cfo kpi revenue currency fx', icon: CreditCard },
  { id: 'billing', label: 'Billing and Invoicing', type: 'Business System', route: '/billing', keywords: 'billing invoice payment receipt credit note vat subscription', icon: CreditCard },
  { id: 'revenue-ledger', label: 'Revenue Ledger', type: 'Forensic Ledger', route: '/revenue-ledger', keywords: 'ledger revenue proof invoice evidence fiscal trail', icon: FileText },
  { id: 'documents', label: 'Document Vault', type: 'Document System', route: '/documents', keywords: 'documents vault versions audit verify share watermark lock', icon: FolderOpen },
  { id: 'artifacts', label: 'Artifact Studio', type: 'Artifact System', route: '/artifacts', keywords: 'artifact board pack nda agreement evidence pack invoice pdf docx json', icon: FileText },
  { id: 'legal', label: 'Legal and Compliance', type: 'Legal System', route: '/legal', keywords: 'legal compliance popia forensic evidence risk contracts', icon: ShieldCheck },
  { id: 'client-portal', label: 'Client Portal', type: 'Client System', route: '/client-portal', keywords: 'client portal messages matters invoices documents activity', icon: Building2 },
  { id: 'settings', label: 'Account Settings', type: 'Command', command: 'OPEN_ACCOUNT_SETTINGS', route: '/account', keywords: 'settings account theme security compliance profile mfa sessions', icon: Terminal },
  { id: 'theme', label: 'Change Operating Skin', type: 'Command', command: 'OPEN_THEME_SETTINGS', route: '/account/theme', keywords: 'theme skin day night auto aurora forensic cobalt pearl gold quantum', icon: Terminal },
  { id: 'export', label: 'Export Current View', type: 'Command', command: 'EXPORT_CURRENT_VIEW', keywords: 'export pdf csv json view artifact', icon: Terminal },
  { id: 'resync', label: 'Resync Sources', type: 'Command', command: 'RESYNC_SOURCES', keywords: 'resync refresh sources telemetry finance fx crm hr', icon: Terminal }
]);

/**
 * @function normalizeSearchText
 * @description Normalizes search text for local matching.
 * @param {unknown} value - Candidate search text.
 * @returns {string} Normalized text.
 * @collaboration Keeps global command search deterministic and local-first.
 */
const normalizeSearchText = (value = '') => (
  String(value || '').toLowerCase().replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim()
);

/**
 * @function rankWilsySearchRows
 * @description Ranks Wilsy OS search rows against the user query.
 * @param {Array<Object>} rows - Search candidate rows.
 * @param {string} query - Search query.
 * @returns {Array<Object>} Ranked search rows.
 * @collaboration Turns dashboard, vertical, artifact and command entries into one local command surface.
 */
const rankWilsySearchRows = (rows = [], query = '') => {
  const needle = normalizeSearchText(query);
  if (!needle) return rows.slice(0, 12).map(row => ({ ...row, score: 1 }));

  return rows
    .map(row => {
      const label = normalizeSearchText(row.label);
      const type = normalizeSearchText(row.type);
      const keywords = normalizeSearchText(row.keywords);
      const route = normalizeSearchText(row.route);
      let score = 0;

      if (label === needle) score += 100;
      if (label.startsWith(needle)) score += 60;
      if (label.includes(needle)) score += 40;
      if (keywords.includes(needle)) score += 28;
      if (type.includes(needle)) score += 16;
      if (route.includes(needle)) score += 10;

      return { ...row, score };
    })
    .filter(row => row.score > 0)
    .sort((a, b) => b.score - a.score || a.label.localeCompare(b.label))
    .slice(0, 18);
};

/**
 * @function buildTenantContextRows
 * @description Builds tenant-aware command search rows.
 * @param {Object} params - Tenant and user context.
 * @returns {Array<Object>} Tenant-aware rows.
 * @collaboration Makes global search feel attached to the current operator and tenant rather than generic SaaS chrome.
 */
const buildTenantContextRows = ({ user = {}, activeTenant = {} } = {}) => {
  const tenantName = activeTenant?.name || activeTenant?.companyName || activeTenant?.tenantName || 'Current Tenant';
  const userEmail = user?.email || user?.username || '';

  return [
    {
      id: 'tenant-profile',
      label: `${tenantName} Profile`,
      type: 'Tenant Context',
      route: '/account/tenant',
      keywords: `tenant profile branding identity ${tenantName} ${userEmail}`,
      icon: Building2
    },
    {
      id: 'operator-profile',
      label: 'My Operator Profile',
      type: 'Operator Context',
      route: '/account/profile',
      keywords: `my account profile user operator ${userEmail}`,
      icon: Users
    }
  ];
};

/**
 * @function WilsyGlobalCommandSearch
 * @description Global Wilsy OS command and local search overlay.
 * @param {Object} props - Component props.
 * @param {boolean} props.isOpen - Whether the overlay is visible.
 * @param {Function} props.onClose - Close handler.
 * @param {Function} props.onNavigate - Result activation handler.
 * @param {Object} props.user - Current user.
 * @param {Object} props.activeTenant - Current tenant.
 * @param {string} props.currentDashboardKey - Mounted dashboard key.
 * @returns {React.ReactElement|null} Global command search overlay.
 * @collaboration Gives Wilsy OS a real Command K experience instead of isolated placeholder search fields.
 */
const WilsyGlobalCommandSearch = ({
  isOpen = false,
  onClose = () => {},
  onNavigate = () => {},
  user = {},
  activeTenant = {},
  currentDashboardKey = ''
}) => {
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef(null);

  const rows = useMemo(() => (
    [
      ...buildTenantContextRows({ user, activeTenant }),
      ...WILSY_SEARCH_REGISTRY
    ]
  ), [activeTenant, user]);

  const rankedRows = useMemo(() => (
    rankWilsySearchRows(rows, query)
  ), [query, rows]);

  useEffect(() => {
    if (!isOpen) return;
    setActiveIndex(0);
    requestAnimationFrame(() => inputRef.current?.focus());
  }, [isOpen]);

  /**
   * @function handleResultActivation
   * @description Activates a selected command search result.
   * @param {Object} row - Selected search row.
   * @returns {void}
   * @collaboration Routes dashboards, commands and vertical systems from one sovereign command interface.
   */
  const handleResultActivation = (row = {}) => {
    if (!row.id) return;

    onNavigate({
      ...row,
      query,
      currentDashboardKey,
      activatedAt: new Date().toISOString()
    });

    setQuery('');
    onClose();
  };

  /**
   * @function handleInputKeyDown
   * @description Handles keyboard navigation inside the global search overlay.
   * @param {KeyboardEvent} event - Keyboard event.
   * @returns {void}
   * @collaboration Makes Command K usable without forcing mouse navigation.
   */
  const handleInputKeyDown = (event) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveIndex(index => Math.min(index + 1, Math.max(rankedRows.length - 1, 0)));
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex(index => Math.max(index - 1, 0));
      return;
    }

    if (event.key === 'Enter') {
      event.preventDefault();
      handleResultActivation(rankedRows[activeIndex] || rankedRows[0]);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Wilsy OS Global Search"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9600,
        display: 'grid',
        placeItems: 'start center',
        padding: '8vh 18px 18px',
        background: 'rgba(0,0,0,0.68)',
        backdropFilter: 'blur(14px)'
      }}
      onMouseDown={event => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        style={{
          width: 'min(920px, 100%)',
          overflow: 'hidden',
          color: 'var(--wilsy-text, #fffaf0)',
          background: 'linear-gradient(180deg, color-mix(in srgb, var(--wilsy-panel, #07101d) 94%, transparent), color-mix(in srgb, var(--wilsy-bg, #020306) 98%, transparent))',
          border: '1px solid var(--wilsy-border, rgba(212,175,55,0.28))',
          borderRadius: 28,
          boxShadow: '0 34px 120px rgba(0,0,0,0.58), inset 0 1px 0 rgba(255,255,255,0.08)'
        }}
      >
        <header
          style={{
            display: 'grid',
            gridTemplateColumns: '22px minmax(0, 1fr) max-content',
            alignItems: 'center',
            gap: 14,
            padding: '18px 20px',
            borderBottom: '1px solid var(--wilsy-border, rgba(212,175,55,0.18))'
          }}
        >
          <Search size={19} color="var(--wilsy-accent, #d4af37)" />
          <input
            ref={inputRef}
            value={query}
            onChange={event => setQuery(event.target.value)}
            onKeyDown={handleInputKeyDown}
            placeholder="Search Wilsy OS, commands, people, clients, invoices, documents..."
            style={{
              width: '100%',
              border: 0,
              outline: 0,
              color: 'var(--wilsy-text, #fffaf0)',
              background: 'transparent',
              fontFamily: 'JetBrains Mono, IBM Plex Mono, ui-monospace, monospace',
              fontSize: 16,
              fontWeight: 800,
              letterSpacing: '0.02em'
            }}
          />
          <button
            type="button"
            onClick={onClose}
            aria-label="Close global search"
            style={{
              width: 38,
              height: 38,
              display: 'grid',
              placeItems: 'center',
              borderRadius: 14,
              border: '1px solid var(--wilsy-border, rgba(212,175,55,0.2))',
              color: 'var(--wilsy-text, #fffaf0)',
              background: 'rgba(255,255,255,0.04)',
              cursor: 'pointer'
            }}
          >
            <X size={18} />
          </button>
        </header>

        <div
          style={{
            display: 'grid',
            gap: 8,
            maxHeight: '58vh',
            overflow: 'auto',
            padding: 14
          }}
        >
          {rankedRows.length ? rankedRows.map((row, index) => {
            const RowIcon = row.icon || Terminal;
            const isActive = index === activeIndex;

            return (
              <button
                key={row.id}
                type="button"
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => handleResultActivation(row)}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '40px minmax(0, 1fr) max-content',
                  alignItems: 'center',
                  gap: 13,
                  minHeight: 68,
                  padding: '10px 12px',
                  borderRadius: 18,
                  border: isActive
                    ? '1px solid var(--wilsy-accent, #d4af37)'
                    : '1px solid var(--wilsy-border, rgba(212,175,55,0.14))',
                  background: isActive
                    ? 'color-mix(in srgb, var(--wilsy-accent, #d4af37) 12%, transparent)'
                    : 'rgba(255,255,255,0.035)',
                  color: 'var(--wilsy-text, #fffaf0)',
                  textAlign: 'left',
                  fontFamily: 'JetBrains Mono, IBM Plex Mono, ui-monospace, monospace',
                  cursor: 'pointer'
                }}
              >
                <span
                  style={{
                    width: 40,
                    height: 40,
                    display: 'grid',
                    placeItems: 'center',
                    borderRadius: 14,
                    color: 'var(--wilsy-accent, #d4af37)',
                    background: 'rgba(0,0,0,0.22)'
                  }}
                >
                  <RowIcon size={18} />
                </span>
                <span style={{ minWidth: 0 }}>
                  <strong
                    style={{
                      display: 'block',
                      color: 'var(--wilsy-text, #fffaf0)',
                      fontSize: 13,
                      lineHeight: 1.25
                    }}
                  >
                    {row.label}
                  </strong>
                  <small
                    style={{
                      display: 'block',
                      marginTop: 5,
                      color: 'var(--wilsy-muted, #aeb6c8)',
                      fontSize: 11,
                      lineHeight: 1.35
                    }}
                  >
                    {row.type} {row.route ? `// ${row.route}` : ''}
                  </small>
                </span>
                <ArrowRight size={16} color="var(--wilsy-authority, #d4af37)" />
              </button>
            );
          }) : (
            <article
              style={{
                padding: 22,
                color: 'var(--wilsy-muted, #aeb6c8)',
                border: '1px solid var(--wilsy-border, rgba(212,175,55,0.14))',
                borderRadius: 18,
                background: 'rgba(255,255,255,0.035)',
                fontFamily: 'JetBrains Mono, IBM Plex Mono, ui-monospace, monospace'
              }}
            >
              No Wilsy OS result found. Try HR, client, invoice, document, artifact, billing, compliance or settings.
            </article>
          )}
        </div>

        <footer
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            gap: 12,
            padding: '12px 20px 16px',
            color: 'var(--wilsy-muted, #aeb6c8)',
            borderTop: '1px solid var(--wilsy-border, rgba(212,175,55,0.12))',
            fontFamily: 'JetBrains Mono, IBM Plex Mono, ui-monospace, monospace',
            fontSize: 11
          }}
        >
          <span>Press Enter to open</span>
          <span>Esc to close // ↑ ↓ to navigate</span>
        </footer>
      </section>
    </div>
  );
};

export default WilsyGlobalCommandSearch;

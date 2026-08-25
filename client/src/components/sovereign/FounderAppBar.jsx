/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS - Founder Command App Bar
 * =============================================================================
 * File:           client/src/components/sovereign/FounderAppBar.jsx
 * Version:        v1.1.0-VISIBLE-MENUS
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Top navigation with ALWAYS-VISIBLE category triggers and
 *                 React-state dropdowns that are not clipped by parent overflow.
 *                 Single kennel chip. No duplicate identity controls.
 * Classification: Production Artifact
 *
 * Change Log:
 *   2026-08-01 v1.1.0-VISIBLE-MENUS - overflow:visible; fixed-position menus;
 *     removed competing identity UI; higher-contrast triggers.
 *   2026-08-01 v1.0.0-INSTITUTIONAL - Initial extract from FounderDashboard.
 *
 * Certification Seal: PRODUCTION_READY_v1.1.0-VISIBLE-MENUS
 * =============================================================================
 */

import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { createPortal } from 'react-dom';

const CLOSE_DELAY_MS = 180;

/**
 * Portal dropdown so parent overflow:hidden cannot clip the menu.
 */
function MenuPortal({ anchorEl, open, onClose, children, label }) {
  const [pos, setPos] = useState({ top: 0, left: 0, minWidth: 240 });

  useLayoutEffect(() => {
    if (!open || !anchorEl) return undefined;
    const update = () => {
      const r = anchorEl.getBoundingClientRect();
      setPos({
        top: r.bottom + 4,
        left: Math.min(r.left, window.innerWidth - 260),
        minWidth: Math.max(240, r.width)
      });
    };
    update();
    window.addEventListener('resize', update);
    window.addEventListener('scroll', update, true);
    return () => {
      window.removeEventListener('resize', update);
      window.removeEventListener('scroll', update, true);
    };
  }, [open, anchorEl]);

  if (!open || typeof document === 'undefined') return null;

  return createPortal(
    <div
      role="menu"
      aria-label={label}
      data-wilsy-founder-menu={label}
      style={{
        position: 'fixed',
        top: pos.top,
        left: pos.left,
        minWidth: pos.minWidth,
        maxHeight: 'min(70vh, 440px)',
        overflowY: 'auto',
        background: '#0B1024',
        border: '1px solid rgba(212,175,55,0.4)',
        borderRadius: 8,
        boxShadow: '0 20px 50px rgba(0,0,0,0.85)',
        zIndex: 99999,
        display: 'flex',
        flexDirection: 'column',
        padding: '6px 0'
      }}
      onMouseDown={(e) => e.stopPropagation()}
    >
      {children}
    </div>,
    document.body
  );
}

/**
 * @param {object} props
 * @param {{ label: string, items: Array<{key:string,label:string,icon?:any,active?:boolean}> }[]} props.menuGroups
 * @param {(key: string) => void} props.onActivateModule
 * @param {boolean} [props.kennelConnected]
 * @param {number} [props.kennelLatencyMs]
 * @param {string} [props.kennelVersion]
 * @param {React.ReactNode} [props.rightSlot] - metrics/clock ONLY (no second user chip)
 */
const FounderAppBar = ({
  menuGroups = [],
  onActivateModule,
  kennelConnected = false,
  kennelLatencyMs = 0,
  kennelVersion = '1.1.1',
  rightSlot = null,
  brandLabel = 'WILSY OS'
}) => {
  const [openLabel, setOpenLabel] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const closeTimerRef = useRef(null);
  const buttonRefs = useRef({});

  const clearCloseTimer = useCallback(() => {
    if (closeTimerRef.current) {
      clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }
  }, []);

  const scheduleClose = useCallback(() => {
    clearCloseTimer();
    closeTimerRef.current = setTimeout(() => {
      setOpenLabel(null);
      setAnchorEl(null);
    }, CLOSE_DELAY_MS);
  }, [clearCloseTimer]);

  const openGroup = useCallback((label, el) => {
    clearCloseTimer();
    setOpenLabel(label);
    setAnchorEl(el);
  }, [clearCloseTimer]);

  const toggleGroup = useCallback((label, el) => {
    clearCloseTimer();
    setOpenLabel((prev) => {
      if (prev === label) {
        setAnchorEl(null);
        return null;
      }
      setAnchorEl(el);
      return label;
    });
  }, [clearCloseTimer]);

  useEffect(() => {
    const onPointer = (event) => {
      const t = event.target;
      if (t?.closest?.('[data-wilsy-founder-menu]')) return;
      if (t?.closest?.('[data-wilsy-founder-trigger]')) return;
      setOpenLabel(null);
      setAnchorEl(null);
    };
    const onKey = (event) => {
      if (event.key === 'Escape') {
        setOpenLabel(null);
        setAnchorEl(null);
      }
    };
    document.addEventListener('mousedown', onPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onPointer);
      document.removeEventListener('keydown', onKey);
      clearCloseTimer();
    };
  }, [clearCloseTimer]);

  const handleSelect = useCallback((key) => {
    setOpenLabel(null);
    setAnchorEl(null);
    try {
      onActivateModule?.(key);
    } catch (err) {
      if (import.meta.env.DEV) console.warn('[FounderAppBar] activate failed', err);
    }
  }, [onActivateModule]);

  const openItems = menuGroups.find((g) => g.label === openLabel)?.items || [];

  return (
    <header
      role="banner"
      aria-label="Founder command navigation"
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        flexShrink: 0,
        background: '#070B18',
        borderBottom: '1px solid rgba(212,175,55,0.2)',
        position: 'relative',
        zIndex: 500,
        overflow: 'visible'
      }}
    >
      {/* Row 1: brand + kennel + right metrics */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 12,
          minHeight: 44,
          padding: '6px 16px 0 16px',
          overflow: 'visible'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
          <span
            style={{
              fontWeight: 900,
              letterSpacing: '0.14em',
              fontSize: '0.82rem',
              color: '#D4AF37',
              fontFamily: 'ui-monospace, JetBrains Mono, monospace',
              whiteSpace: 'nowrap'
            }}
          >
            {brandLabel}
          </span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 10px',
              borderRadius: 999,
              border: `1px solid ${kennelConnected ? 'rgba(16,185,129,0.45)' : 'rgba(239,68,68,0.45)'}`,
              background: kennelConnected ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
              color: kennelConnected ? '#6EE7B7' : '#FCA5A5',
              fontSize: '0.62rem',
              fontWeight: 800,
              letterSpacing: '0.06em',
              fontFamily: 'ui-monospace, monospace',
              whiteSpace: 'nowrap'
            }}
            title={`Kennel ${kennelConnected ? 'CONNECTED' : 'FRACTURE'} v${kennelVersion}`}
          >
            <span
              style={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                background: kennelConnected ? '#10b981' : '#ef4444'
              }}
            />
            KENNEL · {kennelConnected ? 'CONNECTED' : 'FRACTURE'}
            {kennelVersion ? ` · v${kennelVersion}` : ''}
            {kennelLatencyMs > 0 ? ` · ${kennelLatencyMs}ms` : ''}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
          {rightSlot}
        </div>
      </div>

      {/* Row 2: ALWAYS-VISIBLE category triggers */}
      <nav
        aria-label="Module categories"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '8px 16px 10px 16px',
          overflowX: 'auto',
          overflowY: 'visible',
          WebkitOverflowScrolling: 'touch',
          scrollbarWidth: 'thin'
        }}
      >
        {menuGroups.map((group) => {
          const isOpen = openLabel === group.label;
          const hasActive = (group.items || []).some((it) => it.active);
          return (
            <button
              key={group.label}
              type="button"
              data-wilsy-founder-trigger={group.label}
              ref={(el) => {
                buttonRefs.current[group.label] = el;
              }}
              aria-haspopup="menu"
              aria-expanded={isOpen}
              onClick={(e) => toggleGroup(group.label, e.currentTarget)}
              onMouseEnter={(e) => openGroup(group.label, e.currentTarget)}
              onMouseLeave={scheduleClose}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 12px',
                minHeight: 36,
                borderRadius: 6,
                border: isOpen || hasActive
                  ? '1px solid rgba(212,175,55,0.55)'
                  : '1px solid rgba(255,255,255,0.12)',
                background: isOpen || hasActive
                  ? 'rgba(212,175,55,0.16)'
                  : 'rgba(255,255,255,0.04)',
                color: isOpen || hasActive ? '#F5E6A8' : '#E5E5E5',
                fontWeight: 700,
                fontSize: '0.7rem',
                letterSpacing: '0.03em',
                fontFamily: 'ui-monospace, JetBrains Mono, monospace',
                whiteSpace: 'nowrap',
                cursor: 'pointer',
                flexShrink: 0,
                lineHeight: 1.2
              }}
            >
              <span>{group.label}</span>
              <ChevronDown
                size={13}
                style={{
                  transform: isOpen ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.15s ease',
                  opacity: 0.85
                }}
              />
            </button>
          );
        })}
      </nav>

      <MenuPortal
        anchorEl={anchorEl}
        open={Boolean(openLabel)}
        label={openLabel || ''}
        onClose={() => {
          setOpenLabel(null);
          setAnchorEl(null);
        }}
      >
        <div
          onMouseEnter={clearCloseTimer}
          onMouseLeave={scheduleClose}
        >
          {openItems.length === 0 && (
            <div style={{ padding: '12px 16px', color: '#888', fontSize: '0.72rem' }}>
              No modules in this group
            </div>
          )}
          {openItems.map((item) => (
            <button
              key={item.key}
              type="button"
              role="menuitem"
              onClick={() => handleSelect(item.key)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                width: '100%',
                padding: '10px 16px',
                border: 'none',
                background: item.active ? 'rgba(212,175,55,0.16)' : 'transparent',
                color: item.active ? '#D4AF37' : '#E8E8E8',
                fontWeight: item.active ? 800 : 500,
                fontSize: '0.75rem',
                textAlign: 'left',
                cursor: 'pointer',
                fontFamily: 'ui-monospace, monospace'
              }}
            >
              {item.icon ? <span style={{ display: 'inline-flex' }}>{item.icon}</span> : null}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </MenuPortal>
    </header>
  );
};

export default FounderAppBar;

/* eslint-disable */
import React from 'react';
import {
  ArrowLeft,
  Building2,
  ChevronDown,
  Crown,
  Gauge,
  Search,
  ShieldCheck,
  Sparkles
} from 'lucide-react';

const WILSY_CHROME_VERSION = 'R10-CHROME-PRIMITIVES-ONE-FILE';
const WILSY_CHROME_DATA_SEAL = 'WILSY_OS_REUSABLE_DASHBOARD_CHROME';

const chromeTokens = {
  bg: '#050A14',
  panel: 'rgba(8, 13, 26, 0.86)',
  panelStrong: 'rgba(9, 16, 32, 0.96)',
  line: 'rgba(154, 179, 216, 0.22)',
  lineStrong: 'rgba(154, 179, 216, 0.38)',
  text: '#F8FBFF',
  muted: '#AAB6C9',
  faint: '#6F7D95',
  cyan: '#19D6FF',
  green: '#32F59E',
  gold: '#E7C85C',
  danger: '#FF5C7A',
  shadow: '0 28px 90px rgba(0, 0, 0, 0.36)',
  radius: 28
};

/**
 * @function mergeSx
 * @description Merges component-owned sovereign chrome styles with caller-provided style overrides.
 * @collaboration Keeps Wilsy OS chrome primitives reusable across CRM, Executive, Founder, and vertical dashboards without duplicating style logic.
 */
function mergeSx(base, override) {
  return {
    ...base,
    ...(override || {})
  };
}

/**
 * @function WilsyWorkspaceShell
 * @description Provides the reusable outer sovereign workspace shell for Wilsy OS dashboards.
 * @collaboration Allows every dashboard to share the same operating surface while still passing custom rail, content, and action areas.
 */
export function WilsyWorkspaceShell({
  children,
  rail,
  footer,
  tone = 'night',
  'data-testid': dataTestId = 'wilsy-workspace-shell',
  style
}) {
  const isDay = tone === 'day';

  return (
    <section
      data-testid={dataTestId}
      data-wilsy-chrome-version={WILSY_CHROME_VERSION}
      data-wilsy-chrome-seal={WILSY_CHROME_DATA_SEAL}
      style={mergeSx({
        minHeight: '100vh',
        width: '100%',
        boxSizing: 'border-box',
        padding: 'clamp(18px, 2.2vw, 34px)',
        color: isDay ? '#07111F' : chromeTokens.text,
        background: isDay
          ? 'linear-gradient(135deg, #F7FBFF 0%, #E9F4FF 44%, #FFFFFF 100%)'
          : 'radial-gradient(circle at 12% 10%, rgba(0, 114, 255, 0.20), transparent 32%), radial-gradient(circle at 86% 8%, rgba(50, 245, 158, 0.13), transparent 28%), linear-gradient(135deg, #050A14 0%, #07101F 52%, #030610 100%)',
        overflow: 'hidden'
      }, style)}
    >
      {rail}
      <main
        data-wilsy-workspace-main="true"
        style={{
          display: 'grid',
          gap: 'clamp(18px, 2vw, 30px)',
          width: '100%',
          maxWidth: 1680,
          margin: '0 auto'
        }}
      >
        {children}
      </main>
      {footer}
    </section>
  );
}

/**
 * @function WilsyCommandTopRail
 * @description Renders a reusable command authority top rail with command label, title, search, sync posture, and primary action.
 * @collaboration Gives all Wilsy OS dashboards one consistent command surface instead of rebuilding rail logic per vertical.
 */
export function WilsyCommandTopRail({
  commandLabel = 'Founder Command',
  title = 'Command authority and operating posture.',
  subtitle = 'Root authority across identity, tenant posture, route visibility and operating preferences.',
  story = 'Known for • Forensic command intelligence',
  searchPlaceholder = 'Search Wilsy OS command layer',
  syncLabel = 'Live sync',
  primaryAction,
  onPrimaryAction,
  rightSlot,
  style
}) {
  return (
    <header
      data-wilsy-command-top-rail="true"
      style={mergeSx({
        display: 'grid',
        gridTemplateColumns: 'minmax(160px, 0.20fr) minmax(360px, 1fr) minmax(220px, 0.34fr)',
        alignItems: 'center',
        gap: 18,
        width: '100%',
        maxWidth: 1680,
        margin: '0 auto clamp(18px, 2vw, 28px)',
        padding: '18px clamp(18px, 2vw, 26px)',
        border: `1px solid ${chromeTokens.line}`,
        borderRadius: chromeTokens.radius,
        background: 'linear-gradient(135deg, rgba(8, 13, 26, 0.94), rgba(5, 10, 20, 0.82))',
        boxShadow: chromeTokens.shadow,
        boxSizing: 'border-box'
      }, style)}
    >
      <div style={{ display: 'grid', gap: 12 }}>
        <span style={{
          color: chromeTokens.text,
          fontSize: 12,
          lineHeight: 1.2,
          fontWeight: 900,
          letterSpacing: '0.24em',
          textTransform: 'uppercase'
        }}>
          {commandLabel}
        </span>
        <span style={{
          color: chromeTokens.muted,
          fontSize: 11,
          lineHeight: 1.2,
          fontWeight: 850,
          letterSpacing: '0.28em',
          textTransform: 'uppercase'
        }}>
          {story}
        </span>
      </div>

      <div style={{ display: 'grid', gap: 4 }}>
        <h1 style={{
          margin: 0,
          color: chromeTokens.text,
          fontSize: 'clamp(26px, 2.4vw, 44px)',
          lineHeight: 0.98,
          fontWeight: 950,
          letterSpacing: '-0.05em'
        }}>
          {title}
        </h1>
        <p style={{
          margin: 0,
          color: chromeTokens.muted,
          fontSize: 'clamp(14px, 1.05vw, 17px)',
          lineHeight: 1.35,
          maxWidth: 980
        }}>
          {subtitle}
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: primaryAction ? '1fr auto' : '1fr',
        gap: 10,
        alignItems: 'center'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          minHeight: 46,
          padding: '0 14px',
          border: `1px solid ${chromeTokens.line}`,
          borderRadius: 16,
          color: chromeTokens.muted,
          background: 'rgba(255, 255, 255, 0.035)'
        }}>
          <Search size={16} />
          <span style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontSize: 13,
            fontWeight: 750
          }}>
            {searchPlaceholder}
          </span>
        </div>

        {primaryAction ? (
          <button
            type="button"
            onClick={onPrimaryAction}
            data-wilsy-primary-action="true"
            style={{
              minHeight: 46,
              padding: '0 16px',
              border: `1px solid rgba(50, 245, 158, 0.42)`,
              borderRadius: 16,
              color: '#03130D',
              background: `linear-gradient(135deg, ${chromeTokens.green}, ${chromeTokens.cyan})`,
              fontSize: 12,
              fontWeight: 950,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              cursor: 'pointer'
            }}
          >
            {primaryAction}
          </button>
        ) : null}

        <div style={{
          gridColumn: '1 / -1',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 12,
          color: chromeTokens.faint,
          fontSize: 11,
          fontWeight: 850,
          letterSpacing: '0.18em',
          textTransform: 'uppercase'
        }}>
          <span>{syncLabel}</span>
          {rightSlot}
        </div>
      </div>
    </header>
  );
}

/**
 * @function WilsyIdentityPlate
 * @description Renders the reusable identity, command verification, compliance, authority, CID, and tenant scope card.
 * @collaboration Replaces per-dashboard identity-card duplication with one sovereign identity component across Wilsy OS.
 */
export function WilsyIdentityPlate({
  initials = 'WK',
  name = 'Wilson Khanyezi',
  accountLabel = '',
  commandLabel = 'Command Identity',
  statusLabel = 'Tenant Verified',
  complianceLabel = 'POPIA S19',
  authorityLabel = 'Tenant Authority',
  correlationId = 'CID-28FC37',
  tenantName = 'Wilsy OS Root',
  tenantId,
  tenantOptions = [],
  density = 'standard',
  onTenantClick,
  onTenantChange,
  style,
  ...domProps
}) {
  const isAccountDensity = density === 'account';
  const isCompact = density === 'compact' || isAccountDensity;
  const safeCid = String(correlationId || 'CID-WILSYROOT').replace(/^REF\s+/i, 'CID-').toUpperCase();

  const plateSettings = isAccountDensity
    ? {
        columns: '86px minmax(0, 1fr)',
        avatarSize: 74,
        avatarFont: 29,
        gap: 18,
        padding: '16px 18px',
        radius: 26,
        maxWidth: 540,
        minHeight: 210,
        nameFont: 'clamp(25px, 1.65vw, 32px)',
        labelFont: 10,
        evidenceFont: 9
      }
    : {
        columns: isCompact ? '92px minmax(0, 1fr)' : '128px minmax(0, 1fr)',
        avatarSize: isCompact ? 86 : 104,
        avatarFont: isCompact ? 32 : 40,
        gap: isCompact ? 18 : 26,
        padding: isCompact ? '18px 20px' : 'clamp(20px, 2vw, 30px)',
        radius: isCompact ? 28 : 34,
        maxWidth: isCompact ? 540 : 620,
        minHeight: 'auto',
        nameFont: isCompact ? 'clamp(24px, 1.55vw, 30px)' : 'clamp(26px, 1.9vw, 34px)',
        labelFont: isCompact ? 10 : 12,
        evidenceFont: isCompact ? 9 : 11
      };

  return (
    <aside
      data-wilsy-identity-plate="true"
      data-wilsy-identity-plate-density={density}
      {...domProps}
      style={mergeSx({
        position: 'relative',
        display: 'grid',
        gridTemplateColumns: plateSettings.columns,
        gap: plateSettings.gap,
        alignItems: 'center',
        minWidth: 0,
        width: '100%',
        maxWidth: plateSettings.maxWidth,
        minHeight: plateSettings.minHeight,
        padding: plateSettings.padding,
        border: `1px solid ${chromeTokens.lineStrong}`,
        borderRadius: plateSettings.radius,
        background: [
          'radial-gradient(circle at 18% 24%, rgba(25, 214, 255, 0.13), transparent 32%)',
          'radial-gradient(circle at 74% 12%, rgba(231, 200, 92, 0.11), transparent 34%)',
          'linear-gradient(135deg, rgba(7, 18, 33, 0.98), rgba(4, 8, 17, 0.94))'
        ].join(', '),
        boxShadow: '0 30px 90px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.035)',
        boxSizing: 'border-box',
        overflow: 'hidden'
      }, style)}
    >
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: '0 8% auto 30%',
          height: 1,
          background: 'linear-gradient(90deg, transparent, rgba(25,214,255,0.22), rgba(231,200,92,0.20), transparent)'
        }}
      />

      <div style={{
        display: 'grid',
        placeItems: 'center',
        width: plateSettings.avatarSize,
        height: plateSettings.avatarSize,
        alignSelf: 'center',
        justifySelf: 'center',
        border: `1px solid rgba(25, 214, 255, 0.34)`,
        borderRadius: isAccountDensity ? 20 : 24,
        background: 'linear-gradient(145deg, rgba(25, 214, 255, 0.18), rgba(255, 255, 255, 0.025))',
        color: chromeTokens.text,
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.07), 0 18px 54px rgba(0,0,0,0.22)',
        fontSize: plateSettings.avatarFont,
        fontWeight: 950,
        lineHeight: 1,
        letterSpacing: '-0.08em'
      }}>
        {initials}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateRows: 'auto auto auto auto',
        gap: isAccountDensity ? 9 : 13,
        minWidth: 0,
        overflow: 'visible',
        alignContent: 'center'
      }}>
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: isAccountDensity ? '7px 14px' : '8px 18px',
          minWidth: 0,
          overflow: 'visible'
        }}>
          <span style={{
            color: chromeTokens.muted,
            fontSize: plateSettings.labelFont,
            lineHeight: 1,
            fontWeight: 950,
            letterSpacing: isAccountDensity ? '0.14em' : '0.20em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap'
          }}>
            {commandLabel}
          </span>
          <span style={{
            color: chromeTokens.green,
            fontSize: plateSettings.labelFont,
            lineHeight: 1,
            fontWeight: 950,
            letterSpacing: isAccountDensity ? '0.12em' : '0.16em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap'
          }}>
            ● {statusLabel}
          </span>
        </div>

        <div style={{ display: 'grid', gap: accountLabel ? 4 : 0, minWidth: 0 }}>
          <strong style={{
            color: chromeTokens.text,
            fontSize: plateSettings.nameFont,
            lineHeight: 1,
            fontWeight: 950,
            letterSpacing: '-0.06em',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}>
            {name}
          </strong>

          {accountLabel ? (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              width: 'max-content',
              maxWidth: '100%',
              color: chromeTokens.faint,
              fontSize: 10,
              lineHeight: 1,
              fontWeight: 900,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              whiteSpace: 'nowrap'
            }}>
              {accountLabel}
            </span>
          ) : null}
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: isAccountDensity ? '7px 10px' : '8px 14px',
          alignItems: 'center',
          color: chromeTokens.green,
          fontSize: plateSettings.evidenceFont,
          fontWeight: 950,
          letterSpacing: isAccountDensity ? '0.08em' : '0.12em',
          lineHeight: 1.15,
          textTransform: 'uppercase',
          whiteSpace: 'normal',
          overflow: 'visible'
        }}>
          <span>{complianceLabel}</span>
          <span>•</span>
          <span>{authorityLabel}</span>
          <span style={{ color: chromeTokens.gold }}>{safeCid}</span>
        </div>

        <WilsyTenantScopeControl
          tenantName={tenantName}
          tenantId={tenantId}
          tenantOptions={tenantOptions}
          onClick={onTenantClick}
          onTenantChange={onTenantChange}
          compact={isCompact}
          density={density}
        />
      </div>
    </aside>
  );
}

/**
 * @function WilsyTenantScopeControl
 * @description Renders a reusable tenant scope selector shell for dashboard identity and command surfaces.
 * @collaboration Standardizes tenant posture controls across all Wilsy OS dashboards while preserving real tenant switching semantics.
 */
export function WilsyTenantScopeControl({
  tenantName = 'Wilsy OS Root',
  tenantId,
  tenantOptions = [],
  label = 'Tenant Scope',
  compact = false,
  density = 'standard',
  onClick,
  onTenantChange,
  style
}) {
  const hasTenantOptions = Array.isArray(tenantOptions) && tenantOptions.length > 0;
  const isAccountDensity = density === 'account';

  if (isAccountDensity) {
    return (
      <div
        data-wilsy-tenant-scope-control="true"
        data-wilsy-tenant-scope-select="R10-CHROME-PRIMITIVE-TENANT-SCOPE"
        style={mergeSx({
          position: 'relative',
          display: 'grid',
          gridTemplateColumns: '22px minmax(0, 1fr) 16px',
          alignItems: 'center',
          gap: 10,
          width: '100%',
          minHeight: 42,
          maxHeight: 42,
          padding: '7px 10px',
          border: `1px solid ${chromeTokens.lineStrong}`,
          borderRadius: 15,
          color: chromeTokens.text,
          background: 'rgba(3, 7, 15, 0.74)',
          boxSizing: 'border-box',
          overflow: 'hidden'
        }, style)}
      >
        <Building2 size={15} color={chromeTokens.green} />

        <span style={{
          display: 'grid',
          gap: 2,
          minWidth: 0,
          pointerEvents: 'none'
        }}>
          <span style={{
            color: chromeTokens.muted,
            fontSize: 8,
            lineHeight: 1,
            fontWeight: 950,
            letterSpacing: '0.20em',
            textTransform: 'uppercase',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {label}
          </span>
          <strong style={{
            color: chromeTokens.text,
            fontSize: 13,
            lineHeight: 1,
            fontWeight: 900,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {tenantName}
          </strong>
        </span>

        <ChevronDown size={14} color={chromeTokens.muted} />

        {hasTenantOptions ? (
          <select
            aria-label={label}
            data-wilsy-tenant-select-control="R10-CHROME-PRIMITIVE-SELECT"
            value={tenantId}
            onChange={onTenantChange}
            style={{
              position: 'absolute',
              inset: 0,
              width: '100%',
              height: '100%',
              opacity: 0,
              border: 0,
              cursor: 'pointer'
            }}
          >
            {tenantOptions.map(option => (
              <option key={option.tenantId || option.value || option.id} value={option.tenantId || option.value || option.id}>
                {option.label || option.name || option.displayName || option.tenantId || option.value || option.id}
              </option>
            ))}
          </select>
        ) : null}
      </div>
    );
  }

  return (
    <div
      data-wilsy-tenant-scope-control="true"
      data-wilsy-tenant-scope-select="R10-CHROME-PRIMITIVE-TENANT-SCOPE"
      role={hasTenantOptions ? undefined : 'button'}
      tabIndex={hasTenantOptions ? undefined : 0}
      onClick={hasTenantOptions ? undefined : onClick}
      style={mergeSx({
        display: 'grid',
        gridTemplateColumns: '36px minmax(0, 1fr) 20px',
        alignItems: 'center',
        gap: 14,
        width: '100%',
        minHeight: compact ? 48 : 74,
        padding: compact ? '9px 12px' : '14px 18px',
        border: `1px solid ${chromeTokens.lineStrong}`,
        borderRadius: compact ? 18 : 22,
        color: chromeTokens.text,
        background: 'rgba(3, 7, 15, 0.78)',
        cursor: hasTenantOptions ? 'default' : 'pointer',
        boxSizing: 'border-box',
        textAlign: 'left'
      }, style)}
    >
      <Building2 size={22} color={chromeTokens.green} />
      <span style={{ display: 'grid', gap: 5, minWidth: 0 }}>
        <span style={{
          color: chromeTokens.muted,
          fontSize: 11,
          lineHeight: 1,
          fontWeight: 950,
          letterSpacing: '0.22em',
          textTransform: 'uppercase'
        }}>
          {label}
        </span>

        {hasTenantOptions ? (
          <select
            data-wilsy-tenant-select-control="R10-CHROME-PRIMITIVE-SELECT"
            value={tenantId}
            onChange={onTenantChange}
            style={{
              appearance: 'none',
              WebkitAppearance: 'none',
              width: '100%',
              minWidth: 0,
              border: 0,
              outline: 0,
              padding: 0,
              margin: 0,
              color: chromeTokens.text,
              background: 'transparent',
              fontSize: compact ? 14 : 16,
              lineHeight: 1.1,
              fontWeight: 900,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              cursor: 'pointer'
            }}
          >
            {tenantOptions.map(option => (
              <option key={option.tenantId || option.value || option.id} value={option.tenantId || option.value || option.id}>
                {option.label || option.name || option.displayName || option.tenantId || option.value || option.id}
              </option>
            ))}
          </select>
        ) : (
          <strong style={{
            color: chromeTokens.text,
            fontSize: compact ? 14 : 16,
            lineHeight: 1.1,
            fontWeight: 900,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {tenantName}
          </strong>
        )}
      </span>
      <ChevronDown size={18} color={chromeTokens.muted} />
    </div>
  );
}

/**
 * @function WilsyMetricTile
 * @description Renders a reusable dashboard metric tile with status rail, icon, label, value, and evidence text.
 * @collaboration Replaces repeated KPI cards across vertical dashboards with one shared Wilsy OS primitive.
 */
export function WilsyMetricTile({
  label = 'Sovereign Command',
  value = 'Verified',
  evidence = 'Tenant-bound command layer',
  icon,
  tone = 'cyan',
  status = 'ACTIVE',
  style
}) {
  const accent = tone === 'green'
    ? chromeTokens.green
    : tone === 'gold'
      ? chromeTokens.gold
      : tone === 'danger'
        ? chromeTokens.danger
        : chromeTokens.cyan;

  return (
    <article
      data-wilsy-metric-tile="true"
      style={mergeSx({
        position: 'relative',
        display: 'grid',
        gridTemplateColumns: '48px minmax(0, 1fr)',
        gap: 16,
        alignItems: 'center',
        minHeight: 132,
        padding: 18,
        border: `1px solid ${chromeTokens.line}`,
        borderRadius: 24,
        background: 'linear-gradient(135deg, rgba(8, 13, 26, 0.92), rgba(5, 10, 20, 0.82))',
        boxShadow: '0 18px 54px rgba(0,0,0,0.26)',
        overflow: 'hidden',
        boxSizing: 'border-box'
      }, style)}
    >
      <span style={{
        position: 'absolute',
        inset: '0 auto 0 0',
        width: 4,
        background: `linear-gradient(180deg, ${accent}, transparent)`
      }} />

      <span style={{
        display: 'grid',
        placeItems: 'center',
        width: 46,
        height: 46,
        border: `1px solid ${chromeTokens.line}`,
        borderRadius: 14,
        color: accent,
        background: 'rgba(255,255,255,0.035)'
      }}>
        {icon || <Gauge size={20} />}
      </span>

      <span style={{ display: 'grid', gap: 8, minWidth: 0 }}>
        <span style={{
          color: chromeTokens.muted,
          fontSize: 10,
          fontWeight: 950,
          letterSpacing: '0.26em',
          textTransform: 'uppercase'
        }}>
          {status}
        </span>
        <strong style={{
          color: chromeTokens.text,
          fontSize: 'clamp(18px, 1.35vw, 24px)',
          lineHeight: 1.05,
          fontWeight: 950,
          letterSpacing: '-0.04em'
        }}>
          {value}
        </strong>
        <span style={{
          color: chromeTokens.muted,
          fontSize: 13,
          lineHeight: 1.3,
          fontWeight: 700
        }}>
          {label} · {evidence}
        </span>
      </span>
    </article>
  );
}

/**
 * @function WilsyFounderReturnControl
 * @description Renders the reusable floating Founder return control.
 * @collaboration Prevents duplicate founder-return controls by providing one standard dashboard primitive.
 */
export function WilsyFounderReturnControl({
  label = 'Founder',
  onClick,
  style
}) {
  return (
    <button
      type="button"
      data-wilsy-founder-return-control="true"
      onClick={onClick}
      aria-label="Return to Founder Command"
      style={mergeSx({
        position: 'fixed',
        left: 24,
        bottom: 24,
        zIndex: 80,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 10,
        minHeight: 50,
        padding: '0 16px',
        border: `1px solid rgba(231, 200, 92, 0.36)`,
        borderRadius: 999,
        color: chromeTokens.gold,
        background: 'linear-gradient(135deg, rgba(7, 18, 33, 0.96), rgba(4, 8, 17, 0.92))',
        boxShadow: '0 16px 44px rgba(0,0,0,0.32)',
        cursor: 'pointer',
        fontSize: 12,
        fontWeight: 950,
        letterSpacing: '0.14em',
        textTransform: 'uppercase'
      }, style)}
    >
      <Crown size={18} />
      {label}
      <ArrowLeft size={16} />
    </button>
  );
}

export const WilsyChromeIcons = {
  Crown,
  ShieldCheck,
  Sparkles,
  Gauge
};


const WILSY_R11_COMMAND_IDENTITY_COCKPIT_PRIMITIVE = 'WILSY_R11_COMMAND_IDENTITY_COCKPIT_PRIMITIVE_ACTIVE';

const WILSY_DEFAULT_COCKPIT_ROUTES = [
  { id: 'crm', label: 'CRM', description: 'Pipeline, receipts and source posture', status: 'ready' },
  { id: 'finance', label: 'Finance', description: 'Revenue ledger and audit-backed flows', status: 'ready' },
  { id: 'hr', label: 'HR', description: 'People command and workforce compliance', status: 'ready' },
  { id: 'security', label: 'Security', description: 'Sessions, MFA, posture and access signals', status: 'ready' }
];

const WILSY_DEFAULT_COCKPIT_TELEMETRY = [
  { id: 'contracts', label: 'Contracts verified', value: '7' },
  { id: 'sessions', label: 'Active sessions', value: '15' },
  { id: 'receipts', label: 'Receipts logged', value: '42' }
];

const WILSY_DEFAULT_COMPLIANCE_ANCHORS = [
  { id: 'popia-s19', label: 'POPIA S19', description: 'Security safeguards and lawful processing evidence' },
  { id: 'tenant-authority', label: 'Tenant Authority', description: 'Root tenant posture, jurisdiction and operating seal' },
  { id: 'audit-seal', label: 'Audit Seal', description: 'Cryptographic command receipt trail' }
];

/**
 * @function WilsyCommandIdentityCockpit
 * @description Renders a reusable cockpit-grade command identity surface with route launch, telemetry, compliance anchors, authentication hooks, and audit receipt hooks.
 * @collaboration Turns the Wilsy identity card into a live sovereign cockpit primitive that can be reused across CRM, Executive, Founder, HR, Finance, Security, and future vertical dashboards.
 */
export function WilsyCommandIdentityCockpit({
  identity = {},
  routes = WILSY_DEFAULT_COCKPIT_ROUTES,
  telemetry = WILSY_DEFAULT_COCKPIT_TELEMETRY,
  complianceAnchors = WILSY_DEFAULT_COMPLIANCE_ANCHORS,
  activeRouteId,
  authenticationLabel = 'Authenticate session',
  onAuthenticate,
  onRouteLaunch,
  onComplianceOpen,
  onReceiptLog,
  style
}) {
  const identitySeal = identity.correlationId || identity.cid || 'CID-WILSYROOT';

  /**
   * @function emitReceipt
   * @description Emits a cockpit audit receipt payload with the active identity seal, tenant scope, and timestamp.
   * @collaboration Allows route launch, compliance drill-down, and authentication events to share one auditable receipt bridge.
   */
  const emitReceipt = (payload) => {
    onReceiptLog?.({
      seal: identitySeal,
      tenantId: identity.tenantId,
      timestamp: new Date().toISOString(),
      ...payload
    });
  };

  return (
    <section
      data-wilsy-command-identity-cockpit="true"
      data-wilsy-command-identity-cockpit-version={WILSY_R11_COMMAND_IDENTITY_COCKPIT_PRIMITIVE}
      style={mergeSx({
        display: 'grid',
        gridTemplateColumns: 'minmax(460px, 0.42fr) minmax(620px, 1fr)',
        gap: 22,
        alignItems: 'stretch',
        width: '100%',
        boxSizing: 'border-box',
        padding: 'clamp(8px, 0.8vw, 14px)',
        border: `1px solid ${chromeTokens.line}`,
        borderRadius: 32,
        background: [
          'radial-gradient(circle at 8% 12%, rgba(25,214,255,0.14), transparent 30%)',
          'radial-gradient(circle at 88% 0%, rgba(50,245,158,0.10), transparent 28%)',
          'linear-gradient(135deg, rgba(5,10,20,0.70), rgba(3,7,15,0.52))'
        ].join(', '),
        boxShadow: '0 34px 110px rgba(0,0,0,0.38)'
      }, style)}
    >
      <WilsyIdentityPlate
        initials={identity.initials || 'WK'}
        name={identity.name || identity.displayName || 'Wilson Khanyezi'}
        accountLabel={identity.accountLabel || ''}
        commandLabel={identity.commandLabel || 'Command Identity'}
        statusLabel={identity.statusLabel || 'Tenant Verified'}
        complianceLabel={identity.complianceLabel || 'POPIA S19'}
        authorityLabel={identity.authorityLabel || 'Tenant Authority'}
        correlationId={identitySeal}
        tenantName={identity.tenantName || 'Wilsy OS Root'}
        tenantId={identity.tenantId}
        tenantOptions={identity.tenantOptions || []}
        density={identity.density || 'account'}
        onTenantChange={identity.onTenantChange}
        data-wilsy-command-cockpit-identity-plate="true"
        style={{
          maxWidth: '100%',
          height: '100%'
        }}
      />

      <div
        data-wilsy-command-cockpit-stack="true"
        style={{
          display: 'grid',
          gridTemplateRows: 'auto auto auto',
          gap: 14,
          minWidth: 0
        }}
      >
        <div
          data-wilsy-command-cockpit-route-grid="true"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
            gap: 12
          }}
        >
          {routes.map(route => {
            const active = activeRouteId === route.id;

            return (
              <button
                key={route.id}
                type="button"
                data-wilsy-command-cockpit-route={route.id}
                data-wilsy-command-cockpit-route-active={active ? 'true' : 'false'}
                onClick={() => {
                  onRouteLaunch?.(route);
                  emitReceipt({ type: 'route_launch', routeId: route.id });
                }}
                style={{
                  display: 'grid',
                  gap: 8,
                  minHeight: 128,
                  padding: 16,
                  border: `1px solid ${active ? 'rgba(50, 245, 158, 0.72)' : chromeTokens.line}`,
                  borderRadius: 20,
                  color: chromeTokens.text,
                  background: active
                    ? 'linear-gradient(135deg, rgba(50,245,158,0.18), rgba(25,214,255,0.08))'
                    : 'linear-gradient(135deg, rgba(8,13,26,0.90), rgba(4,8,17,0.76))',
                  boxShadow: active ? '0 0 38px rgba(50,245,158,0.22)' : '0 14px 40px rgba(0,0,0,0.22)',
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
              >
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  color: active ? chromeTokens.green : chromeTokens.cyan,
                  fontSize: 10,
                  fontWeight: 950,
                  letterSpacing: '0.18em',
                  textTransform: 'uppercase'
                }}>
                  <ShieldCheck size={14} />
                  {route.status || 'ready'}
                </span>
                <strong style={{
                  color: chromeTokens.text,
                  fontSize: 18,
                  lineHeight: 1.02,
                  fontWeight: 950,
                  letterSpacing: '-0.04em'
                }}>
                  {route.label}
                </strong>
                <small style={{
                  color: chromeTokens.muted,
                  fontSize: 12,
                  lineHeight: 1.25,
                  fontWeight: 700
                }}>
                  {route.description}
                </small>
              </button>
            );
          })}
        </div>

        <div
          data-wilsy-command-cockpit-telemetry="true"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
            gap: 10
          }}
        >
          {telemetry.map(item => (
            <div
              key={item.id}
              data-wilsy-command-cockpit-telemetry-item={item.id}
              style={{
                display: 'grid',
                gap: 6,
                padding: '12px 14px',
                border: `1px solid ${chromeTokens.line}`,
                borderRadius: 18,
                background: 'rgba(255,255,255,0.035)'
              }}
            >
              <span style={{
                color: chromeTokens.muted,
                fontSize: 10,
                lineHeight: 1,
                fontWeight: 950,
                letterSpacing: '0.16em',
                textTransform: 'uppercase'
              }}>
                {item.label}
              </span>
              <strong style={{
                color: chromeTokens.green,
                fontSize: 24,
                lineHeight: 1,
                fontWeight: 950
              }}>
                {item.value}
              </strong>
            </div>
          ))}
        </div>

        <div
          data-wilsy-command-cockpit-compliance="true"
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr auto',
            gap: 12,
            alignItems: 'stretch'
          }}
        >
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
            gap: 10
          }}>
            {complianceAnchors.map(anchor => (
              <button
                key={anchor.id}
                type="button"
                data-wilsy-command-cockpit-compliance-anchor={anchor.id}
                onClick={() => {
                  onComplianceOpen?.(anchor);
                  emitReceipt({ type: 'compliance_anchor_open', anchorId: anchor.id });
                }}
                style={{
                  display: 'grid',
                  gap: 6,
                  minHeight: 76,
                  padding: '12px 14px',
                  border: `1px solid ${chromeTokens.line}`,
                  borderRadius: 18,
                  color: chromeTokens.text,
                  background: 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
              >
                <span style={{
                  color: chromeTokens.gold,
                  fontSize: 10,
                  fontWeight: 950,
                  letterSpacing: '0.16em',
                  textTransform: 'uppercase'
                }}>
                  {anchor.label}
                </span>
                <small style={{
                  color: chromeTokens.muted,
                  fontSize: 11,
                  lineHeight: 1.25,
                  fontWeight: 700
                }}>
                  {anchor.description}
                </small>
              </button>
            ))}
          </div>

          <button
            type="button"
            data-wilsy-command-cockpit-authenticate="true"
            onClick={() => {
              onAuthenticate?.({ seal: identitySeal, tenantId: identity.tenantId });
              emitReceipt({ type: 'authentication_requested' });
            }}
            style={{
              minWidth: 190,
              border: `1px solid rgba(50, 245, 158, 0.46)`,
              borderRadius: 18,
              color: '#03130D',
              background: `linear-gradient(135deg, ${chromeTokens.green}, ${chromeTokens.cyan})`,
              cursor: 'pointer',
              fontSize: 11,
              fontWeight: 950,
              letterSpacing: '0.14em',
              textTransform: 'uppercase'
            }}
          >
            {authenticationLabel}
          </button>
        </div>
      </div>
    </section>
  );
}

export const WILSY_COMMAND_IDENTITY_COCKPIT_DEFAULTS = {
  routes: WILSY_DEFAULT_COCKPIT_ROUTES,
  telemetry: WILSY_DEFAULT_COCKPIT_TELEMETRY,
  complianceAnchors: WILSY_DEFAULT_COMPLIANCE_ANCHORS
};


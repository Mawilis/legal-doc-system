/**
 * TITLE: WILSY OS Headquarters authenticated executive workspace
 * VERSION: v2.4.1-EXACT-SESSION-KPI-PRESENTATION
 * AUTHORITY: WILSY EOS client projection; Python EOS remains the business authority
 * EPITOME: Presents the authenticated company operating plane and a source-backed
 *          My Work snapshot without inventing enterprise metrics or commands.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/WilsyHeadquartersWorkspace.jsx
 * COLLABORATION / OWNERSHIP: WILSY EOS frontend projection consuming /api/my-work
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v2.4.1-EXACT-SESSION-KPI-PRESENTATION applies the same
 *            exact-session guard to the executive KPI strip and provides
 *            the authenticated current tenant to Daily Brief; no stale
 *            prior-capacity counts may appear during scope transitions.
 *            v2.4.0-CURRENT-SOURCE-HEADQUARTERS-KPI partitions the
 *            Headquarters My Work summary by authenticated EOS identity and
 *            source coverage. It deduplicates overview/brief reads and listens
 *            for confirmed source-command invalidation; stale tenant results
 *            are never presented as live company operating metrics.
 *            v2.3.0-SOURCE-OWNED-OPERATIONS-DEEP-LINK routes an authenticated
 *            operations-source work handoff to the existing EOS-backed create
 *            and manage workspace instead of a dead-end overview. Only the
 *            owning module's permission and entitlement checks admit commands.
 *            v2.2.0-MY-WORK-ITEM-HANDOFF carries a selected daily source key into
 *            canonical My Work, where a fresh authorized read validates it.
 *            v2.1.0-URL-ROUTED-WORKFORCE-DUTIES supports the validated HR entry URL from
 *            global daily attention without inferring any new permissions.
 *            v2.0.0-HEADQUARTERS-ACTIONABLE-DAILY-BRIEF adds authorised interactive daily work
 *            without removing source-backed KPI, HR requisitions, workforce,
 *            operations, authenticated tenant identity or runtime monitoring.
 *            v1.9.0 projects the server-certified active tenant label into
 *            Headquarters chrome with an explicit neutral fallback when the
 *            authenticated tenant projection is unavailable.
 *            v1.8.0 adds an authenticated handoff into the canonical HR
 *            operating suite so hiring and workforce commands remain owned by
 *            the existing HR surface and its EOS authorization boundaries.
 *            v1.7.0 adds explicit refresh controls for the My Work and HR
 *            requisition projections so daily users can request a fresh
 *            server read without inventing local state or commands.
 *            v1.6.0 projects the authenticated server-validated operator name
 *            and business role into the Headquarters chrome without treating
 *            browser presentation as authorization.
 * COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2
 * SECURITY / PRIVACY POSTURE: Uses the authenticated API client and renders only
 *                             the caller's independently authorized work summary.
 * TENANT BOUNDARY: Inherited from the authenticated workspace and /api/my-work.
 * AUTHORITY BOUNDARY: Read-only projection; source services own all commands.
 * FINANCIAL AUTHORITY BOUNDARY: No financial, settlement, or release authority.
 */
import React, { lazy, Suspense, useContext, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import AuthContext from '../../contexts/authContext.jsx';
import api from '../../services/api.js';
import {
  currentUnifiedMyWorkScope,
  readUnifiedMyWork,
  subscribeUnifiedMyWork,
} from '../../services/unifiedMyWorkSync.js';
import { useKennelHealth } from '../../hooks/useKennelHealth.js';
import {
  ArrowUpRight, BriefcaseBusiness, Building2, CheckCircle2, ChevronRight,
  CircleAlert, Code2, FileText, Globe2, Headphones, LockKeyhole, RefreshCw,
  Users, Wallet,
} from 'lucide-react';
import MyWorkWorkspace from './MyWorkWorkspace.jsx';
import WilsyHeadquartersDailyBrief from './WilsyHeadquartersDailyBrief.jsx';
import TenantModuleWorkspace from '../os/TenantModuleWorkspace.jsx';

const HRDashboard = lazy(() => import('../hr/HrDashboard.jsx'));

const departments = [
  { id: 'engineering', label: 'Engineering', icon: Code2, description: 'Product delivery, repository activity, releases and CI evidence.' },
  { id: 'finance', label: 'Finance', icon: Wallet, description: 'Authorised finance operations, reconciliations and approvals.' },
  { id: 'sales', label: 'Sales', icon: BriefcaseBusiness, description: 'Pipeline, partnerships, proposals and commercial follow-through.' },
  { id: 'customer-success', label: 'Customer Success', icon: Headphones, description: 'Customer onboarding, adoption, support and renewal work.' },
  { id: 'operations', label: 'Operations', icon: RefreshCw, description: 'Service delivery, operational queues and execution controls.' },
  { id: 'security', label: 'Security', icon: LockKeyhole, description: 'Identity, security posture, risk and compliance work.' },
];

const businessModels = [
  'Law firms', 'Importers & exporters', 'Private doctors & dentists',
  'Clinics', 'Spare-parts businesses', 'Mechanics & workshops',
  'Vehicle dealerships', 'Agriculture', 'General trading',
];

function SourceBoundary({ title, description }) {
  return (
    <section className="rounded-2xl border border-amber-300/20 bg-[#101a2a] p-6" data-source-state="NOT_CONNECTED">
      <div className="flex items-start gap-3">
        <CircleAlert className="mt-0.5 shrink-0 text-amber-300" size={20} />
        <div>
          <h3 className="font-semibold text-white">{title}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
          <p className="mt-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-amber-200">Source integration not yet certified</p>
        </div>
      </div>
    </section>
  );
}

/**
 * @description Renders the authenticated headquarters operating workspace.
 * @collaboration Composes the daily brief, canonical My Work projection, HR reads, and tenant modules.
 * @institutional Keeps selected work navigation in presentation state while EOS revalidates access.
 * @param {{tenantId?: string|null}} props Authenticated tenant identifier supplied by the parent.
 * @returns {JSX.Element}
 */
export default function WilsyHeadquartersWorkspace({ tenantId = null }) {
  const location = useLocation();
  const auth = useContext(AuthContext) || {};
  const authUser = auth.user || {};
  const workTenantId = tenantId || authUser.tenantId;
  const workScope = currentUnifiedMyWorkScope(auth, workTenantId);
  // A deep-link selects a pre-existing workspace view, not IAM or module
  // admission authority. The Operations form and API enforce their own grants.
  const sectionFromUrl = new URLSearchParams(location.search).get('section');
  const [section, setSection] = useState(() =>
    ['hr-workspace', 'operations'].includes(sectionFromUrl) ? sectionFromUrl : 'overview');
  const [showMyWork, setShowMyWork] = useState(false);
  const [myWorkFocusItem, setMyWorkFocusItem] = useState(null);
  useEffect(() => {
    const requested = new URLSearchParams(location.search).get('section');
    if (requested === 'hr-workspace' || requested === 'operations') {
      setSection(requested);
      setShowMyWork(false);
    } else if (!requested) {
      setSection((current) =>
        current === 'hr-workspace' || current === 'operations' ? 'overview' : current);
    }
  }, [location.search]);
  const [workforce, setWorkforce] = useState(null);
  const [workforceLoading, setWorkforceLoading] = useState(false);
  const [workforceError, setWorkforceError] = useState('');
  const [workforceSearch, setWorkforceSearch] = useState('');
  const [workforceOffset, setWorkforceOffset] = useState(0);
  const [workforceRefresh, setWorkforceRefresh] = useState(0);
  const [requisitions, setRequisitions] = useState(null);
  const [requisitionsLoading, setRequisitionsLoading] = useState(false);
  const [requisitionsError, setRequisitionsError] = useState('');
  const [requisitionsRefresh, setRequisitionsRefresh] = useState(0);
  const kennelHealth = useKennelHealth({ pollInterval: 60000 });
  const [myWorkSnapshot, setMyWorkSnapshot] = useState(null);
  const [myWorkSnapshotScope, setMyWorkSnapshotScope] = useState(null);
  const [myWorkLoading, setMyWorkLoading] = useState(false);
  const [myWorkError, setMyWorkError] = useState('');
  const [myWorkRefresh, setMyWorkRefresh] = useState(0);
  useEffect(() => {
    if (section !== 'overview' || showMyWork) return undefined;
    if (!workScope) {
      setMyWorkSnapshot(null);
      setMyWorkSnapshotScope(null);
      setMyWorkError('MY_WORK_AUTHENTICATED_SCOPE_REQUIRED');
      setMyWorkLoading(false);
      return undefined;
    }
    let current = true;
    const controller = new AbortController();
    setMyWorkLoading(true);
    setMyWorkError('');
    readUnifiedMyWork(
      workScope,
      { tenantId: workTenantId, principalId: authUser.id },
      { signal: controller.signal, force: true },
    )
      .then((verified) => {
        if (current) {
          setMyWorkSnapshot(verified);
          setMyWorkSnapshotScope(workScope);
        }
      })
      .catch((error) => {
        if (current && error?.name !== 'AbortError') {
          setMyWorkSnapshot(null);
          setMyWorkSnapshotScope(null);
          setMyWorkError(error?.response?.data?.detail || error?.message || 'MY_WORK_UNAVAILABLE');
        }
      })
      .finally(() => {
        if (current) setMyWorkLoading(false);
      });
    return () => {
      current = false;
      controller.abort();
    };
  }, [section, showMyWork, myWorkRefresh, workScope, workTenantId]);

  useEffect(() => {
    if (!workScope || section !== 'overview' || showMyWork) return undefined;
    return subscribeUnifiedMyWork(workScope, () => {
      setMyWorkRefresh((value) => value + 1);
    });
  }, [workScope, section, showMyWork]);
  useEffect(() => {
    if (section !== 'people' && section !== 'overview') return undefined;
    let current = true;
    setWorkforceLoading(true);
    setWorkforceError('');
    const query = workforceSearch.trim();
    api.get('/hr/workforce', {
      params: {
        limit: section === 'overview' ? 1 : 50,
        offset: section === 'overview' ? 0 : workforceOffset,
        ...(section === 'people' && query.length >= 2 ? { q: query } : {}),
      },
      forceNetworkRetry: true,
    })
      .then((response) => {
        if (current) setWorkforce(response.data);
      })
      .catch((error) => {
        if (current) {
          setWorkforce(null);
          setWorkforceError(error?.response?.data?.detail || 'WORKFORCE_DIRECTORY_UNAVAILABLE');
        }
      })
      .finally(() => {
        if (current) setWorkforceLoading(false);
      });
    return () => { current = false; };
  }, [section, workforceSearch, workforceOffset, workforceRefresh]);
  useEffect(() => {
    if (section !== 'hiring') return undefined;
    let current = true;
    setRequisitionsLoading(true);
    setRequisitionsError('');
    api.get('/hr/headcount-requisitions', { forceNetworkRetry: true })
      .then((response) => {
        const payload = response?.data;
        if (!payload || !Array.isArray(payload.items) || !payload.generated_at) {
          throw new Error('HEADCOUNT_REQUISITIONS_INVALID');
        }
        if (current) setRequisitions(payload);
      })
      .catch((error) => {
        if (current) {
          setRequisitions(null);
          setRequisitionsError(error?.response?.data?.detail || error?.message || 'HEADCOUNT_REQUISITIONS_UNAVAILABLE');
        }
      })
      .finally(() => {
        if (current) setRequisitionsLoading(false);
      });
    return () => { current = false; };
  }, [section, requisitionsRefresh]);
  const selectedDepartment = departments.find((item) => item.id === section);
  const openMyWork = (item = null) => {
    const sourceKey = typeof item?.source_key === 'string' && item.source_key.trim()
      ? item.source_key
      : null;
    setMyWorkFocusItem(sourceKey);
    setShowMyWork(true);
  };

  return (
    <main className="min-h-screen bg-[#080f1d] text-slate-100">
      <div className="mx-auto grid max-w-[1600px] lg:grid-cols-[250px_minmax(0,1fr)]">
        <aside className="border-b border-white/10 p-4 lg:min-h-[calc(100vh-73px)] lg:border-b-0 lg:border-r">
          <p className="px-3 pb-3 pt-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Company operating plane</p>
          <nav className="space-y-1" aria-label="Headquarters navigation">
            <button onClick={() => { setSection('overview'); setShowMyWork(false); }} className={navClass(section === 'overview' && !showMyWork)}><Building2 size={17}/> Headquarters</button>
            <button onClick={() => openMyWork()} className={navClass(showMyWork)}><CheckCircle2 size={17}/> My Work</button>
            <button onClick={() => { setSection('people'); setShowMyWork(false); }} className={navClass(section === 'people')}><Users size={17}/> Organisation & People</button>
            {departments.map(({id,label,icon:Icon}) => <button key={id} onClick={() => { setSection(id); setShowMyWork(false); }} className={navClass(section === id)}><Icon size={17}/>{label}</button>)}
            <div className="my-4 border-t border-white/10"/>
            <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Product & customer plane</p>
            <button onClick={() => { setSection('products'); setShowMyWork(false); }} className={navClass(section === 'products')}><Globe2 size={17}/> Products & Business Portfolio</button>
            <button onClick={() => { setSection('knowledge'); setShowMyWork(false); }} className={navClass(section === 'knowledge')}><FileText size={17}/> Knowledge & Documents</button>
          </nav>
          <div className="mt-8 rounded-xl border border-white/10 bg-white/[0.03] p-3 text-xs leading-5 text-slate-400">
            <div className="mb-1 flex items-center gap-2 text-slate-200"><LockKeyhole size={14}/> Authority boundary</div>
            WILSY company records and each customer business remain separately authorised and tenant-isolated.
          </div>
          <RuntimeHealthFooter health={kennelHealth}/>
        </aside>

        <div className="min-w-0 p-4 sm:p-6 lg:p-9">
          {showMyWork ? (
            <MyWorkWorkspace focusWorkItem={myWorkFocusItem} />
          ) : section === 'overview' ? (
            <>
              <section className="relative overflow-hidden rounded-3xl border border-amber-300/20 bg-gradient-to-br from-[#132b50] via-[#10213b] to-[#091426] p-7 sm:p-10">
                <div className="absolute -right-12 -top-20 h-72 w-72 rounded-full border border-amber-300/10"/>
                <div className="relative max-w-3xl">
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300">One company. One operating environment.</p>
                  <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-5xl">WILSY Headquarters</h1>
                  <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">The place where Wilsy (Pty) Ltd coordinates its people, products, customers and daily execution.</p>
                  <div className="mt-7 flex flex-wrap gap-3">
                    <button onClick={() => openMyWork()} className="inline-flex items-center gap-2 rounded-xl bg-amber-300 px-5 py-3 text-sm font-semibold text-[#091426]">Open My Work <ArrowUpRight size={16}/></button>
                    <button onClick={() => setSection('people')} className="rounded-xl border border-white/20 px-5 py-3 text-sm font-medium text-white">Organisation & workforce</button>
                  </div>
                </div>
              </section>

              <ExecutiveKpiStrip myWorkSnapshot={myWorkSnapshotScope === workScope ? myWorkSnapshot : null} workforce={section === 'overview' ? workforce : null}/>

              <WilsyHeadquartersDailyBrief tenantId={workTenantId} onOpenWork={(item) => openMyWork(item)} />

              <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ActionCard title="Daily execution" detail="Authorised tasks and source-owned completion" onClick={() => openMyWork()} icon={CheckCircle2}/>
                <ActionCard title="People & workforce" detail="Employee records, hiring and onboarding" onClick={() => setSection('people')} icon={Users}/>
                <ActionCard title="Product delivery" detail="Repositories, releases and CI evidence" onClick={() => setSection('engineering')} icon={Code2}/>
                <ActionCard title="Business portfolio" detail="Separate customer businesses and workspaces" onClick={() => setSection('products')} icon={Globe2}/>
              </div>

              <MyWorkSnapshot loading={myWorkLoading} error={myWorkError} snapshot={myWorkSnapshotScope === workScope ? myWorkSnapshot : null} onOpen={() => openMyWork()} onRefresh={() => setMyWorkRefresh((value) => value + 1)}/>

              <div className="mt-8 grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
                <section className="rounded-2xl border border-white/10 bg-[#101a2a] p-5">
                  <div className="flex items-center justify-between gap-3"><h2 className="text-lg font-semibold">Department workspaces</h2><span className="text-[10px] uppercase tracking-widest text-slate-500">Source-backed views</span></div>
                  <div className="mt-4 grid gap-2 sm:grid-cols-2">
                    {departments.map(({id,label,icon:Icon,description}) => <button key={id} onClick={() => setSection(id)} className="rounded-xl border border-white/10 bg-white/[0.025] p-4 text-left hover:border-amber-300/40"><Icon className="text-amber-300" size={19}/><div className="mt-3 font-medium">{label}</div><p className="mt-1 text-xs leading-5 text-slate-400">{description}</p><div className="mt-3 flex items-center gap-1 text-xs text-amber-200">Open workspace <ChevronRight size={13}/></div></button>)}
                  </div>
                </section>
                <section className="rounded-2xl border border-white/10 bg-[#101a2a] p-5">
                  <h2 className="text-lg font-semibold">Operational truth</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-400">This landing page does not invent headcount, revenue, customer totals, uptime or project progress. Each measure will appear only when its owning service is connected and authorised.</p>
                  <div className="mt-5 space-y-3 text-sm">
                    <StatusLine label="My Work" state="Certified foundation" good/>
                    <StatusLine label="Workforce directory" state="Awaiting HR source certification"/>
                    <StatusLine label="Hiring & identity admission" state="Governed workflow required"/>
                    <StatusLine label="Repository & CI evidence" state="Integration gate pending"/>
                  </div>
                </section>
              </div>
            </>
          ) : section === 'people' ? (
            <>
              <PageHeading eyebrow="People & organisation" title="Organisation and workforce" subtitle="Employee records must come from the authorised HR source. Employment does not itself create a login, tenant membership or IAM permission."/>
              {workforceLoading ? (
                <section role="status" className="rounded-2xl border border-white/10 bg-[#101a2a] p-6 text-sm text-amber-200">Loading authorised workforce records…</section>
              ) : workforceError ? (
                <section role="alert" className="rounded-2xl border border-red-400/20 bg-[#101a2a] p-6">
                  <h2 className="font-semibold text-red-200">Workforce directory unavailable</h2>
                  <p className="mt-2 text-sm text-slate-300">The HR source could not verify or return the directory. No empty-state or cached employee list is substituted.</p>
                  <p className="mt-3 font-mono text-xs text-slate-500">{workforceError}</p>
                  <button onClick={() => setSection('overview')} className="mt-4 rounded-lg border border-white/15 px-3 py-2 text-xs">Return to Headquarters</button>
                </section>
              ) : (
                <section className="rounded-2xl border border-white/10 bg-[#101a2a] p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div><h2 className="text-lg font-semibold">Authorised workforce directory</h2><p className="mt-1 text-xs text-slate-400">Limited directory fields from the tenant-authorised HR employee registry.</p></div>
                    <span className="text-xs text-slate-400">{workforce?.total ?? 0} matching records</span>
                  </div>
                  <div className="mt-4 grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto]">
                    <label className="grid gap-1 text-xs text-slate-400">
                      Search workforce
                      <input
                        aria-label="Search workforce directory"
                        value={workforceSearch}
                        onChange={(event) => { setWorkforceSearch(event.target.value); setWorkforceOffset(0); }}
                        placeholder="Name, employee ID, role or department"
                        className="rounded-lg border border-white/15 bg-[#080f1d] px-3 py-2 text-sm text-white outline-none focus:border-amber-300/50"
                      />
                    </label>
                    <button onClick={() => setWorkforceRefresh((value) => value + 1)} className="self-end rounded-lg border border-white/15 px-4 py-2 text-xs text-slate-200">Refresh</button>
                  </div>
                  {workforceSearch.trim().length === 1 && <p className="mt-2 text-xs text-amber-200">Enter at least two characters to filter the directory.</p>}
                  {(workforce?.items || []).length === 0 ? (
                    <p className="mt-5 rounded-xl border border-white/10 p-5 text-sm text-slate-300">No active workforce records were returned by the authorised HR source.</p>
                  ) : (
                    <div className="mt-4 divide-y divide-white/10">
                      {workforce.items.map((person) => (
                        <article key={person.employeeId} className="flex flex-wrap items-center justify-between gap-3 py-4">
                          <div><h3 className="font-medium text-white">{person.displayName || person.preferredName || person.employeeId}</h3><p className="mt-1 text-sm text-slate-400">{person.jobTitle || 'Role not recorded'} · {person.department || 'Department not recorded'}</p><p className="mt-1 text-xs text-slate-500">{person.workEmail || 'Work email not recorded'} · {person.workLocation || 'Location not recorded'}</p></div>
                          <span className="rounded-full border border-emerald-300/20 px-3 py-1 text-xs text-emerald-200">{person.employmentStatus || 'Status not recorded'}</span>
                        </article>
                      ))}
                    </div>
                  )}
                  {(workforce?.items || []).length > 0 && (
                    <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-4">
                      <button
                        disabled={workforceOffset === 0}
                        onClick={() => setWorkforceOffset((value) => Math.max(0, value - 50))}
                        className="rounded-lg border border-white/15 px-3 py-2 text-xs disabled:opacity-40"
                      >Previous</button>
                      <span className="text-xs text-slate-500">Showing {workforceOffset + 1}–{workforceOffset + (workforce.items?.length || 0)} of {workforce.total}</span>
                      <button
                        disabled={!workforce.hasMore}
                        onClick={() => setWorkforceOffset((value) => value + 50)}
                        className="rounded-lg border border-white/15 px-3 py-2 text-xs disabled:opacity-40"
                      >Next</button>
                    </div>
                  )}
                </section>
              )}
              <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3"><ActionCard title="Hiring" detail="Approved headcount and requisitions" onClick={() => setSection('hiring')} icon={BriefcaseBusiness}/><ActionCard title="Employee onboarding" detail="Employment record, then separately governed identity and access admission" onClick={() => setSection('onboarding')} icon={Users}/><ActionCard title="Open HR workspace" detail="Use the canonical governed workforce and hiring workflows" onClick={() => setSection('hr-workspace')} icon={ArrowUpRight}/></div>
            </>
          ) : section === 'hr-workspace' ? (
            <Suspense fallback={<section role="status" className="rounded-2xl border border-white/10 bg-[#101a2a] p-6 text-sm text-amber-200">Loading the canonical HR workspace…</section>}>
              <HRDashboard user={authUser}/>
            </Suspense>
          ) : section === 'hiring' ? (
            <HeadcountRequisitionWorkspace loading={requisitionsLoading} error={requisitionsError} payload={requisitions} onRefresh={() => setRequisitionsRefresh((value) => value + 1)}/>
          ) : section === 'onboarding' ? (
            <>
              <PageHeading eyebrow="People lifecycle" title="Employee onboarding" subtitle="Employment record, then separately governed identity and access admission."/>
              <SourceBoundary title="Employee onboarding workflow not yet connected" description="No candidate, employee, payroll, account or access record is fabricated here. The workflow will be connected only after the HR command authority, approval chain, identity provisioning boundary and atomic audit evidence are certified."/>
            </>
          ) : section === 'operations' ? (
            <TenantModuleWorkspace moduleId="OPERATIONS" />
          ) : selectedDepartment ? (
            <>
              <PageHeading eyebrow="Department workspace" title={selectedDepartment.label} subtitle={selectedDepartment.description}/>
              <SourceBoundary title={selectedDepartment.label + ' source is not yet connected'} description="This department view is an authenticated shell only. Live queues, records and commands will be mounted from their owning authorised service; no placeholder data or browser-only actions are presented."/>
            </>
          ) : section === 'products' ? (
            <>
              <PageHeading eyebrow="WILSY OS product platform" title="Products & business portfolio" subtitle="WILSY builds a reusable platform for different businesses. Each customer operates in its own tenant and authorised workspace; customer data is never part of WILSY's internal workforce records."/>
              <section className="mt-5 rounded-2xl border border-white/10 bg-[#101a2a] p-5"><h2 className="font-semibold">Business models the platform is designed to support</h2><div className="mt-4 flex flex-wrap gap-2">{businessModels.map((name) => <span key={name} className="rounded-full border border-amber-300/20 bg-amber-300/5 px-3 py-2 text-xs text-amber-100">{name}</span>)}</div></section>
              <div className="mt-5"><SourceBoundary title="Customer portfolio integration pending" description="Customer organisations, tenant lifecycle, subscriptions, onboarding and adoption must be read from their authoritative commercial and tenant services. This page does not imply that a listed business is already a customer or that customer data is accessible to WILSY staff." /></div>
            </>
          ) : (
            <>
              <PageHeading eyebrow="Company knowledge" title="Knowledge & documents" subtitle="Controlled company knowledge, policies and records."/>
              <SourceBoundary title="Document source not yet connected" description="Documents will be displayed only through the authorised document and records services, with their existing access controls and audit trail."/>
            </>
          )}
        </div>
      </div>
    </main>
  );
}

function navClass(active) {
  return 'flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm transition ' + (active ? 'bg-amber-300/10 text-amber-200 ring-1 ring-amber-300/20' : 'text-slate-300 hover:bg-white/5');
}
function PageHeading({eyebrow,title,subtitle}) {
  return <header className="mb-6"><p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-300">{eyebrow}</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">{title}</h1><p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{subtitle}</p></header>;
}
function ActionCard({title,detail,onClick,icon:Icon}) {
  return <button onClick={onClick} className="rounded-2xl border border-white/10 bg-[#101a2a] p-4 text-left transition hover:border-amber-300/40"><Icon className="text-amber-300" size={20}/><h3 className="mt-3 font-semibold">{title}</h3><p className="mt-1 text-xs leading-5 text-slate-400">{detail}</p><span className="mt-3 inline-flex items-center gap-1 text-xs text-amber-200">Open <ChevronRight size={13}/></span></button>;
}
function StatusLine({label,state,good=false}) {
  return <div className="flex items-start justify-between gap-3 border-b border-white/5 pb-3"><span className="text-slate-300">{label}</span><span className={'text-right text-xs ' + (good ? 'text-emerald-300' : 'text-amber-200')}>{state}</span></div>;
}

/**
 * @description Renders the authenticated My Work read projection on Headquarters.
 * @collaboration Consumes the existing /api/my-work response; source services own
 *                assignment, completion, approval and confidential-record access.
 * @institutional Prevents executive UI from presenting fabricated work or zeroes
 *                when the authorized source is empty, stale, or unavailable.
 * @param {{loading: boolean, error: string, snapshot: object|null, onOpen: Function, onRefresh: Function}} props
 * @returns {JSX.Element}
 */
function MyWorkSnapshot({ loading, error, snapshot, onOpen, onRefresh }) {
  const summary = snapshot?.summary;
  const sourceCounts = summary?.source_counts || {};
  const sourceCount = Object.keys(sourceCounts).length;
  const freshness = snapshot?.as_of ? new Date(snapshot.as_of).toLocaleString() : null;
  return (
    <section className="mt-8 rounded-2xl border border-white/10 bg-[#101a2a] p-5" aria-labelledby="my-work-snapshot-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-amber-300">Authenticated read projection</p>
          <h2 id="my-work-snapshot-heading" className="mt-1 text-lg font-semibold">My Work — attention snapshot</h2>
          <p className="mt-1 text-sm text-slate-400">Only independently authorized source records are included. Commands remain with their owning services.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={onRefresh} className="inline-flex items-center gap-1 rounded-lg border border-white/15 px-3 py-2 text-xs text-slate-200">Refresh snapshot <RefreshCw size={13}/></button>
          <button onClick={onOpen} className="inline-flex items-center gap-1 rounded-lg border border-white/15 px-3 py-2 text-xs text-amber-200">Open My Work <ArrowUpRight size={14}/></button>
        </div>
      </div>
      {loading ? (
        <p role="status" className="mt-5 rounded-xl border border-white/10 p-4 text-sm text-amber-200">Loading the authorized My Work projection…</p>
      ) : error ? (
        <div role="alert" className="mt-5 rounded-xl border border-red-400/20 bg-red-400/5 p-4">
          <p className="font-medium text-red-200">My Work snapshot unavailable</p>
          <p className="mt-1 text-sm text-slate-300">The source did not provide a valid projection. No zero-valued summary is substituted.</p>
          <p className="mt-2 font-mono text-xs text-slate-500">{error}</p>
        </div>
      ) : snapshot ? (
        <>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <MetricCard label="Active work" value={summary.active_count} detail="Authorized, non-terminal items" />
            <MetricCard label="Overdue" value={summary.overdue_count} detail="Based on source due dates" />
            <MetricCard label="Sources included" value={sourceCount} detail="Omitted sources are not treated as empty" />
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
            {Object.entries(sourceCounts).map(([source, count]) => <span key={source}>{source}: {count}</span>)}
            <span className="ml-auto">As of {freshness}</span>
          </div>
          {summary.active_count === 0 && <p className="mt-4 rounded-xl border border-white/10 p-4 text-sm text-slate-300">No active work was returned by the authorized sources at the recorded time.</p>}
        </>
      ) : (
        <p className="mt-5 rounded-xl border border-amber-300/20 p-4 text-sm text-amber-100">The My Work source has not returned a certified snapshot.</p>
      )}
    </section>
  );
}

function MetricCard({ label, value, detail }) {
  return <div className="rounded-xl border border-white/10 bg-white/[0.025] p-4"><p className="text-xs text-slate-400">{label}</p><p className="mt-2 text-2xl font-semibold text-white">{value}</p><p className="mt-1 text-xs text-slate-500">{detail}</p></div>;
}

function ExecutiveKpiStrip({ myWorkSnapshot, workforce }) {
  const myWorkSummary = myWorkSnapshot?.summary;
  return (
    <section className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Executive KPI summary">
      <MetricCard
        label="My Work"
        value={Number.isInteger(myWorkSummary?.active_count) ? myWorkSummary.active_count : 'Unavailable'}
        detail={Number.isInteger(myWorkSummary?.overdue_count) ? `${myWorkSummary.overdue_count} overdue · source-backed` : 'Authorized source pending'}
      />
      <MetricCard label="Projects" value="Unavailable" detail="Project source not yet certified" />
      <MetricCard label="Approvals" value="Unavailable" detail="Approval source not yet certified" />
      <MetricCard
        label="Team"
        value={Number.isInteger(workforce?.total) ? workforce.total : 'Unavailable'}
        detail={Number.isInteger(workforce?.total) ? 'Authorized HR directory total' : 'Authorized HR source pending'}
      />
    </section>
  );
}

/**
 * @description Presents tenant-scoped HR headcount requisitions from Python EOS.
 * @collaboration Consumes GET /api/hr/headcount-requisitions; submit and decision
 *                commands remain owned by the HR router and its IAM bindings.
 * @institutional Makes the existing hiring planning authority useful from
 *                Headquarters without implying employment, identity, or payroll truth.
 * @param {{loading: boolean, error: string, payload: object|null, onRefresh: Function}} props
 * @returns {JSX.Element}
 */
function HeadcountRequisitionWorkspace({ loading, error, payload, onRefresh }) {
  return (
    <>
      <PageHeading eyebrow="People lifecycle" title="Hiring & requisitions" subtitle="Tenant-scoped headcount planning from the authorized HR registry. A requisition is not an employee, login, membership, capacity, payroll or IAM grant."/>
      {loading ? (
        <section role="status" className="rounded-2xl border border-white/10 bg-[#101a2a] p-6 text-sm text-amber-200">Loading authorized headcount requisitions…</section>
      ) : error ? (
        <section role="alert" className="rounded-2xl border border-red-400/20 bg-[#101a2a] p-6">
          <h2 className="font-semibold text-red-200">Hiring source unavailable</h2>
          <p className="mt-2 text-sm text-slate-300">The HR requisition registry did not return a valid projection. No empty list is substituted.</p>
          <p className="mt-3 font-mono text-xs text-slate-500">{error}</p>
        </section>
      ) : (
        <section className="rounded-2xl border border-white/10 bg-[#101a2a] p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div><h2 className="text-lg font-semibold">Authorized headcount requisitions</h2><p className="mt-1 text-xs text-slate-400">Read-only projection; lifecycle commands remain with the HR service.</p></div>
            <div className="flex items-center gap-3"><button onClick={onRefresh} className="inline-flex items-center gap-1 rounded-lg border border-white/15 px-3 py-2 text-xs text-slate-200">Refresh <RefreshCw size={13}/></button><span className="text-xs text-slate-400">{payload?.items?.length ?? 0} records</span></div>
          </div>
          {(payload?.items || []).length === 0 ? (
            <p className="mt-5 rounded-xl border border-white/10 p-5 text-sm text-slate-300">No headcount requisitions were returned for the authorized tenant.</p>
          ) : (
            <div className="mt-4 divide-y divide-white/10">
              {payload.items.map((item) => (
                <article key={item.requisition_id} className="flex flex-wrap items-start justify-between gap-4 py-4">
                  <div><h3 className="font-medium text-white">{item.position_title}</h3><p className="mt-1 text-sm text-slate-400">{item.department_id} · {item.employment_type} · {item.work_location}</p><p className="mt-1 text-xs text-slate-500">Requested headcount: {item.headcount} · Revision {item.revision}</p></div>
                  <span className="rounded-full border border-amber-300/20 px-3 py-1 text-xs text-amber-200">{item.status}</span>
                </article>
              ))}
            </div>
          )}
          {payload?.generated_at && <p className="mt-4 border-t border-white/10 pt-3 text-xs text-slate-500">Source generated at {new Date(payload.generated_at).toLocaleString()}</p>}
        </section>
      )}
    </>
  );
}


function RuntimeHealthFooter({ health }) {
  const status = String(health?.status || 'UNKNOWN').toUpperCase();
  const version = health?.version || 'Version unavailable';
  const checked = health?.lastChecked ? new Date(health.lastChecked).toLocaleString() : 'Not checked yet';
  return <div className="mt-4 border-t border-white/10 pt-4 text-xs text-slate-500"><div className="flex items-center justify-between gap-3"><span>WILSY OS runtime</span><span className={status === 'ONLINE' ? 'text-emerald-300' : 'text-amber-200'}>{status.toLowerCase()}</span></div><p className="mt-1">{version} · checked {checked}</p></div>;
}

/*
 * ARTIFACT: WILSY OS Headquarters authenticated executive workspace
 * VERSION: v2.4.1-EXACT-SESSION-KPI-PRESENTATION
 * AUTHORITY BOUNDARY: Read-only client projection; Python EOS owns business truth.
 * TENANT POSTURE: Authenticated tenant and principal scope are preserved.
 * FAIL-CLOSED POSTURE: Invalid or unavailable source data is disclosed, never zeroed.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial command is exposed.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */

/**
 * TITLE: WILSY OS Headquarters Authenticated Operating Workspace
 * VERSION: v1.2.0-DAILY-SOURCE-VERIFIED-HQ
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Authenticated tenant headquarters with live daily execution,
 *          source-owned work actions and separately bounded company services.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/WilsyHeadquartersWorkspace.jsx
 * COLLABORATION / OWNERSHIP: Python EOS owns My Work and HR truth;
 *                            global App chrome owns the sole app navigation bar.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.2.0-DAILY-SOURCE-VERIFIED-HQ replaces duplicate inner header
 *            with shared global chrome and mounts the real authorised daily
 *            execution brief above department discovery and quick actions.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No invented KPI, workforce, financial or role data.
 * TENANT BOUNDARY: Exact authenticated scope passed by the protected router.
 * AUTHORITY BOUNDARY: Presentation/read only; commands delegated to sources.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 */

import React, { useEffect, useState } from 'react';
import api from '../../services/api.js';
import {
  ArrowUpRight, BriefcaseBusiness, Building2, CheckCircle2, ChevronRight,
  CircleAlert, Code2, FileText, Globe2, Headphones, LockKeyhole, RefreshCw,
  Users, Wallet,
} from 'lucide-react';
import MyWorkWorkspace from './MyWorkWorkspace.jsx';
import WilsyHeadquartersDailyBrief from './WilsyHeadquartersDailyBrief.jsx';

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

export default function WilsyHeadquartersWorkspace({ tenantId = null }) {
  const [section, setSection] = useState('overview');
  const [showMyWork, setShowMyWork] = useState(false);
  const [workforce, setWorkforce] = useState(null);
  const [workforceLoading, setWorkforceLoading] = useState(false);
  const [workforceError, setWorkforceError] = useState('');
  const [workforceSearch, setWorkforceSearch] = useState('');
  const [workforceOffset, setWorkforceOffset] = useState(0);
  const [workforceRefresh, setWorkforceRefresh] = useState(0);
  useEffect(() => {
    if (section !== 'people') return undefined;
    let current = true;
    setWorkforceLoading(true);
    setWorkforceError('');
    const query = workforceSearch.trim();
    api.get('/hr/workforce', {
      params: {
        limit: 50,
        offset: workforceOffset,
        ...(query.length >= 2 ? { q: query } : {}),
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
  const selectedDepartment = departments.find((item) => item.id === section);

  return (
    <main className="min-h-screen bg-[#080f1d] text-slate-100">
      <div className="mx-auto grid max-w-[1600px] lg:grid-cols-[250px_minmax(0,1fr)]">
        <aside className="border-b border-white/10 p-4 lg:min-h-[calc(100vh-73px)] lg:border-b-0 lg:border-r">
          <p className="px-3 pb-3 pt-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Company operating plane</p>
          <nav className="space-y-1" aria-label="Headquarters navigation">
            <button onClick={() => { setSection('overview'); setShowMyWork(false); }} className={navClass(section === 'overview' && !showMyWork)}><Building2 size={17}/> Headquarters</button>
            <button onClick={() => { setShowMyWork(true); }} className={navClass(showMyWork)}><CheckCircle2 size={17}/> My Work</button>
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
        </aside>

        <div className="min-w-0 p-4 sm:p-6 lg:p-9">
          {showMyWork ? (
            <MyWorkWorkspace />
          ) : section === 'overview' ? (
            <>
              <section className="relative overflow-hidden rounded-3xl border border-amber-300/20 bg-gradient-to-br from-[#132b50] via-[#10213b] to-[#091426] p-7 sm:p-10">
                <div className="absolute -right-12 -top-20 h-72 w-72 rounded-full border border-amber-300/10"/>
                <div className="relative max-w-3xl">
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300">One company. One operating environment.</p>
                  <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-5xl">WILSY Headquarters</h1>
                  <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">The place where Wilsy (Pty) Ltd coordinates its people, products, customers and daily execution.</p>
                  <div className="mt-7 flex flex-wrap gap-3">
                    <button onClick={() => setShowMyWork(true)} className="inline-flex items-center gap-2 rounded-xl bg-amber-300 px-5 py-3 text-sm font-semibold text-[#091426]">Open My Work <ArrowUpRight size={16}/></button>
                    <button onClick={() => setSection('people')} className="rounded-xl border border-white/20 px-5 py-3 text-sm font-medium text-white">Organisation & workforce</button>
                  </div>
                </div>
              </section>

              <WilsyHeadquartersDailyBrief
                tenantId={tenantId}
                onOpenWork={() => setShowMyWork(true)}
              />

              <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <ActionCard title="Daily execution" detail="Authorised tasks and source-owned completion" onClick={() => setShowMyWork(true)} icon={CheckCircle2}/>
                <ActionCard title="People & workforce" detail="Employee records, hiring and onboarding" onClick={() => setSection('people')} icon={Users}/>
                <ActionCard title="Product delivery" detail="Repositories, releases and CI evidence" onClick={() => setSection('engineering')} icon={Code2}/>
                <ActionCard title="Business portfolio" detail="Separate customer businesses and workspaces" onClick={() => setSection('products')} icon={Globe2}/>
              </div>

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
              <div className="mt-5 grid gap-3 sm:grid-cols-2"><ActionCard title="Hiring" detail="Approved headcount and requisitions" onClick={() => setSection('hiring')} icon={BriefcaseBusiness}/><ActionCard title="Employee onboarding" detail="Employment record, then separately governed identity and access admission" onClick={() => setSection('onboarding')} icon={Users}/></div>
            </>
          ) : section === 'hiring' || section === 'onboarding' ? (
            <>
              <PageHeading eyebrow="People lifecycle" title={section === 'hiring' ? 'Hiring & requisitions' : 'Employee onboarding'} subtitle="Hiring approval, employment records and identity admission are separate governed stages."/>
              <SourceBoundary title={section === 'hiring' ? 'Hiring workflow not yet connected' : 'Employee onboarding workflow not yet connected'} description="No candidate, employee, payroll, account or access record is fabricated here. The workflow will be connected only after the HR command authority, approval chain, identity provisioning boundary and atomic audit evidence are certified."/>
            </>
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

/*
 * ARTIFACT: WilsyHeadquartersWorkspace.jsx
 * VERSION: v1.2.0-DAILY-SOURCE-VERIFIED-HQ
 * AUTHORITY BOUNDARY: Authenticated workspace composition only.
 * TENANT POSTURE: EOS tenant-scoped projections; no browser-derived rights.
 * FAIL-CLOSED POSTURE: Unavailable sources do not become invented metrics.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS only.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */

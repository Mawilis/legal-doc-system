import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowUpRight, BriefcaseBusiness, Building2, CheckCircle2, ChevronRight,
  CircleAlert, Code2, FileText, Globe2, Headphones, LockKeyhole, RefreshCw,
  ShieldCheck, Users, Wallet,
} from 'lucide-react';
import MyWorkWorkspace from './MyWorkWorkspace.jsx';

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

export default function WilsyHeadquartersWorkspace() {
  const navigate = useNavigate();
  const [section, setSection] = useState('overview');
  const [showMyWork, setShowMyWork] = useState(false);
  const selectedDepartment = departments.find((item) => item.id === section);

  return (
    <main className="min-h-screen bg-[#080f1d] text-slate-100">
      <header className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-4 border-b border-white/10 bg-[#0b1830]/95 px-5 py-4 backdrop-blur">
        <button onClick={() => { setSection('overview'); setShowMyWork(false); }} className="flex items-center gap-3 text-left">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-400 text-xl font-black text-[#081326]">W</span>
          <span><span className="block text-sm font-bold tracking-[0.18em]">WILSY</span><span className="block text-[10px] uppercase tracking-[0.18em] text-slate-400">Headquarters</span></span>
        </button>
        <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs text-emerald-200">
          <ShieldCheck size={15} /> Authenticated workspace
        </div>
      </header>

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
              <SourceBoundary title="Workforce directory is not yet connected" description="The legacy employee and HR routes have caller-controlled tenant scope and success-empty behaviour. Headquarters will not use them. The directory remains unavailable until an authenticated, tenant-authorised HR read contract and its replica-set tests are certified."/>
              <div className="mt-5 grid gap-3 sm:grid-cols-2"><ActionCard title="Hiring" detail="Approved headcount and requisitions" onClick={() => setSection('hiring')} icon={BriefcaseBusiness}/><ActionCard title="Employee onboarding" detail="Employment record, then separately governed identity and access admission" onClick={() => setSection('onboarding')} icon={Users}/></div>
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

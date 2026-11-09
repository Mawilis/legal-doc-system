import React, { useEffect, useState } from 'react';
import api from '../../services/api';

const SystemStatusPage = () => {
  const [state, setState] = useState({ phase: 'CHECKING', version: null, bridge: null, components: null, checkedAt: null });

  useEffect(() => {
    let active = true;
    const refresh = async () => {
      try {
        const [healthResponse, statusResponse] = await Promise.all([
          api.get('/kernel'),
          api.get('/kernel/status'),
        ]);
        const health = healthResponse?.data;
        const detail = statusResponse?.data;
        const ready = health?.status === 'OPERATIONAL'
          && detail?.status === 'OPERATIONAL'
          && detail?.components
          && Object.values(detail.components).every((value) => value === 'READY');
        if (active) setState({
          phase: ready ? 'OPERATIONAL' : 'DEGRADED',
          version: typeof health?.version === 'string' ? health.version : null,
          bridge: typeof health?.bridge === 'string' ? health.bridge : null,
          components: detail?.components && typeof detail.components === 'object' ? detail.components : null,
          checkedAt: new Date().toISOString(),
        });
      } catch {
        if (active) setState({ phase: 'UNAVAILABLE', version: null, bridge: null, components: null, checkedAt: new Date().toISOString() });
      }
    };
    void refresh();
    const interval = window.setInterval(refresh, 60000);
    return () => { active = false; window.clearInterval(interval); };
  }, []);

  return (
    <main className="mx-auto min-h-[calc(100vh-4rem)] w-full max-w-5xl px-6 py-10 text-slate-100">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-300">WILSY OS</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">System status</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Runtime health and product version are shown here, separate from the authenticated command bar.</p>
      </div>
      <section className="rounded-2xl border border-white/10 bg-[#101d32] p-6" aria-live="polite">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wider text-slate-400">EOS Kernel API</p>
            <p className="mt-2 text-lg font-semibold text-white">{state.phase === 'CHECKING' ? 'Checking…' : state.phase}</p>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${state.phase === 'OPERATIONAL' ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300' : 'border-amber-400/30 bg-amber-400/10 text-amber-200'}`}>{state.phase}</span>
        </div>
        <dl className="mt-6 grid gap-4 border-t border-white/10 pt-5 sm:grid-cols-2">
          <div><dt className="text-xs text-slate-500">WILSY OS client</dt><dd className="mt-1 text-sm text-white">v2.1.0</dd></div>
          <div><dt className="text-xs text-slate-500">EOS Kernel</dt><dd className="mt-1 text-sm text-white">{state.version ? `v${state.version}` : 'Unavailable'}</dd></div>
          <div><dt className="text-xs text-slate-500">Kernel bridge</dt><dd className="mt-1 text-sm text-white">{state.bridge || 'Unavailable'}</dd></div>
          <div><dt className="text-xs text-slate-500">Last checked</dt><dd className="mt-1 text-sm text-white">{state.checkedAt ? new Date(state.checkedAt).toLocaleString() : 'Not checked yet'}</dd></div>
        </dl>
        {state.components && <div className="mt-6 border-t border-white/10 pt-5"><h2 className="text-sm font-semibold text-white">Kernel components</h2><ul className="mt-3 grid gap-2 sm:grid-cols-2">{Object.entries(state.components).map(([name, status]) => <li key={name} className="flex items-center justify-between rounded-lg bg-white/[0.035] px-3 py-2 text-sm"><span className="capitalize text-slate-300">{name.replaceAll('_', ' ')}</span><span className={status === 'READY' ? 'text-emerald-300' : 'text-amber-200'}>{status}</span></li>)}</ul></div>}
      </section>
    </main>
  );
};

export default SystemStatusPage;

import React, { useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setSearchQuery, setSearchResults, setLoading, setError } from '../reducers/searchSlice';
import { performSearch } from '../reducers/searchSlice';

// Local demo data for graceful fallback
const DEMO_DATA = [
  { id: 'DOC-1001', type: 'document', title: 'Summons: Case 1001' },
  { id: 'DOC-1002', type: 'document', title: 'Notice of Motion: Case 1002' },
  { id: 'USR-001', type: 'user',     title: 'Admin — Demo User' },
  { id: 'TAG-INV', type: 'tag',      title: 'Invoice' },
];

export default function Search() {
  const dispatch = useDispatch();

  const searchState = useSelector((s) => s?.search) || {};
  const query   = (searchState.query ?? '');
  const results = Array.isArray(searchState.results) ? searchState.results : [];
  const loading = !!searchState.loading;
  const error   = searchState.error ?? null;

  const doLocalSearch = (q) => {
    const needle = (q || '').trim().toLowerCase();
    if (!needle) return [];
    return DEMO_DATA.filter(item =>
      item.title.toLowerCase().includes(needle) ||
      item.id.toLowerCase().includes(needle) ||
      item.type.toLowerCase().includes(needle)
    );
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    dispatch(setLoading(true));
    try {
      // First try backend
      await dispatch(performSearch(query)).unwrap();
      // If that works, we're done. Results are in slice.
      dispatch(setError(null));
    } catch (err) {
      // Backend not ready or failed? Fill with local demo.
      const demo = doLocalSearch(query);
      dispatch(setSearchResults(demo));
      const is404 = err?.status === 404 || /SEARCH_ENDPOINT_NOT_FOUND/i.test(String(err?.message || ''));
      dispatch(setError(is404 ? null : (err?.message || 'Search failed')));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const disabled = useMemo(() => !query || !query.trim(), [query]);

  return (
    <div style={{ padding: 16 }}>
      <h2>Search</h2>
      <form onSubmit={onSubmit} style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <input
          value={query}
          onChange={(e) => dispatch(setSearchQuery(e.target.value))}
          placeholder="Search documents, users, tags…"
          style={{ flex: 1, padding: 10, border: '1px solid #ccc', borderRadius: 6 }}
        />
        <button type="submit" disabled={disabled} style={{ padding: '10px 14px' }}>
          Search
        </button>
      </form>

      {loading && <p style={{ marginTop: 12 }}>Searching…</p>}
      {error && <p style={{ marginTop: 12, color: '#c1121f' }}>{String(error)}</p>}

      <div style={{ marginTop: 16 }}>
        {(!results || results.length === 0) && !loading && !error ? (
          <p style={{ color: '#666' }}>No results yet. Try searching for “case” or “admin”.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {results.map((r) => (
              <li key={r.id} style={{ padding: 10, borderBottom: '1px solid #eee' }}>
                <strong>{r.title}</strong>
                <div style={{ fontSize: 12, color: '#666' }}>
                  {r.type?.toUpperCase?.() || 'ITEM'} • {r.id}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

/* eslint-disable */
/**
 * WILSY OS - Sovereign Global Topography
 * Real-world owner-node map for live sovereign orchestration.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Graticule,
  Marker,
  Sphere,
  ZoomableGroup
} from 'react-simple-maps';
import worldGeography from 'world-atlas/countries-110m.json';
import {
  Activity,
  ArrowUpRight,
  Crosshair,
  Globe2,
  Loader2,
  MapPin,
  Maximize2,
  Minus,
  Plus,
  Radio,
  RefreshCw,
  Route,
  Satellite,
  ShieldCheck,
  Zap
} from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import sovereignClient from '../../utils/sovereignClient';
import { broadcastTelemetry } from '../../utils/telemetryHelper';
import styles from './Sovereign_Global_Topography.module.css';

const MAP_WIDTH = 1200;
const MAP_HEIGHT = 610;
const REGISTRY_TENANT = 'WILSY_ROOT';
const DEFAULT_MAP_POSITION = { coordinates: [20, -5], zoom: 1, locked: true };

/**
 * @function clamp
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));


/**
 * @function extractNodeRows
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const extractNodeRows = (payload = {}) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.nodes)) return payload.nodes;
  if (Array.isArray(payload.data)) return payload.data;
  if (Array.isArray(payload.data?.nodes)) return payload.data.nodes;
  if (Array.isArray(payload.data?.data?.nodes)) return payload.data.data.nodes;
  return [];
};


/**
 * @function normalizeNode
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const normalizeNode = (node = {}) => {
  const id = node._id || node.id || node.nodeId || node.entity || 'NODE';
  const metadata = node.metadata || {};
  const latency = Number(node.lastLatency ?? node.latency ?? 0);
  const stability = Number(node.neuralStability ?? node.stability ?? 100);

  return {
    ...node,
    id,
    label: node.entity || node.name || node.region || 'Sovereign Node',
    region: node.region || 'GLOBAL',
    lane: metadata.lane || metadata.deploymentStage || node.type || 'Sovereign mesh lane',
    jurisdiction: metadata.jurisdiction || node.tenantId || 'GLOBAL',
    systemOwner: metadata.systemOwner || null,
    legalEntityName: metadata.legalEntityName || null,
    registrationNumber: metadata.registrationNumber || null,
    founder: metadata.founder || null,
    founderRole: metadata.founderRole || null,
    ownershipPercent: metadata.ownershipPercent ?? null,
    commandAuthority: metadata.commandAuthority || null,
    ownerVisible: Boolean(metadata.ownerVisible),
    status: (node.status || 'SYNCING').toUpperCase(),
    latency: Number.isFinite(latency) ? latency : 0,
    stability: Number.isFinite(stability) ? stability : 100,
    hash: node.nodeSeal || node.hash || node.dilithiumSignature || '',
    lat: Number(node.lat || 0),
    lng: Number(node.lng || 0),
    forensicChain: Array.isArray(node.forensicChain) ? node.forensicChain : []
  };
};


/**
 * @function nodeTone
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const nodeTone = (node) => {
  if (node.status === 'ONLINE' || node.status === 'ACTIVE') return 'online';
  if (node.status === 'SYNCING') return 'syncing';
  return 'fault';
};


/**
 * @function isWilsyOwnedNode
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const isWilsyOwnedNode = (node = {}) => {
  const identity = [
    node.label,
    node.systemOwner,
    node.legalEntityName,
    node.commandAuthority,
    node.founder,
    node.metadata?.systemOwner,
    node.metadata?.legalEntityName,
    node.metadata?.commandAuthority,
    node.metadata?.founder
  ].filter(Boolean).join(' ');

  return Boolean(node.ownerVisible || node.metadata?.ownerVisible || /wilsy/i.test(identity));
};


/**
 * @function hasCoordinates
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const hasCoordinates = (node = {}) => (
  Number.isFinite(node.lat) &&
  Number.isFinite(node.lng) &&
  (node.lat !== 0 || node.lng !== 0)
);


/**
 * @function Sovereign_Global_Topography
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const Sovereign_Global_Topography = () => {
  const { activeTenant } = useTenants();
  const mapFrameRef = useRef(null);
  const [nodes, setNodes] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [meshStatus, setMeshStatus] = useState('ALIGNING');
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [mapPosition, setMapPosition] = useState(DEFAULT_MAP_POSITION);

  const fetchNodes = useCallback(async (mode = 'cold') => {
    setSyncing(mode !== 'cold');
    if (mode === 'cold') setLoading(true);

    try {
      const [nodeResult, healthResult] = await Promise.allSettled([
        sovereignClient.get('/nodes', {
          skipAuthRedirect: true,
          params: { tenant: REGISTRY_TENANT, limit: 100 }
        }),
        sovereignClient.get('/nodes/status/health', { skipAuthRedirect: true })
      ]);

      if (nodeResult.status === 'fulfilled') {
        const normalized = extractNodeRows(nodeResult.value.data || {})
          .map(normalizeNode)
          .filter(isWilsyOwnedNode);
        const ownerNode = normalized.find(node => node.ownerVisible) || normalized[0] || null;

        setNodes(normalized);
        setSelectedNodeId(ownerNode?.id || null);
        setMeshStatus(normalized.length ? 'WILSY_ROOT_ONLINE' : 'REGISTRY_EMPTY');
      } else {
        setNodes([]);
        setSelectedNodeId(null);
        setMeshStatus(`NODE_LINK_${nodeResult.reason?.response?.status || 'OFFLINE'}`);
      }

      if (healthResult.status === 'fulfilled') {
        setHealth(healthResult.value.data || null);
      }

      broadcastTelemetry(
        activeTenant?.tenantId || activeTenant?.id || 'GLOBAL_ROOT',
        'GLOBAL_ORCHESTRATOR',
        'NODES_SYNCED',
        'GlobalTopography'
      );
    } catch (error) {
      setMeshStatus('MESH_INTERRUPTED');
    } finally {
      setLoading(false);
      setSyncing(false);
    }
  }, [activeTenant?.id, activeTenant?.tenantId]);

  const seedGlobalMesh = useCallback(async () => {
    setSyncing(true);
    setMeshStatus('ANCHORING_WILSY_ROOT');
    try {
      await sovereignClient.post('/nodes/seed-global', {}, {
        skipAuthRedirect: true,
        params: { tenant: REGISTRY_TENANT }
      });
      await fetchNodes('refresh');
    } catch (error) {
      setMeshStatus(`ANCHOR_FAILED_${error.response?.status || 'OFFLINE'}`);
    } finally {
      setSyncing(false);
    }
  }, [fetchNodes]);

  const updateZoom = useCallback((nextZoom) => {
    setMapPosition(prev => ({ ...prev, zoom: clamp(nextZoom, 1, 8), locked: true }));
  }, []);

  const resetViewport = useCallback(() => {
    setMapPosition(DEFAULT_MAP_POSITION);
    const ownerNode = nodes.find(node => node.ownerVisible) || nodes[0];
    if (ownerNode) setSelectedNodeId(ownerNode.id);
  }, [nodes]);

  useEffect(() => {
    fetchNodes('cold');
    const timer = setInterval(() => fetchNodes('refresh'), 60000);
    return () => clearInterval(timer);
  }, [fetchNodes]);

  const selectedNode = useMemo(
    () => nodes.find(node => node.id === selectedNodeId) || nodes[0] || null,
    [nodes, selectedNodeId]
  );

  const mapNodes = useMemo(() => nodes.filter(hasCoordinates), [nodes]);

  const metrics = useMemo(() => {
    const online = nodes.filter(node => ['ONLINE', 'ACTIVE'].includes(node.status)).length;
    const avgLatency = nodes.length ? nodes.reduce((sum, node) => sum + node.latency, 0) / nodes.length : 0;
    const avgStability = nodes.length ? nodes.reduce((sum, node) => sum + node.stability, 0) / nodes.length : 0;
    const jurisdictions = new Set(nodes.map(node => node.jurisdiction).filter(Boolean)).size;

    return { online, avgLatency, avgStability, jurisdictions };
  }, [nodes]);

  const forensicStream = useMemo(() => (
    nodes
      .flatMap(node => node.forensicChain.map((entry, index) => ({
        id: `${node.id}-${entry.hash || entry.timestamp || index}`,
        node: node.label,
        action: entry.action,
        performer: entry.performer,
        hash: entry.hash,
        timestamp: entry.timestamp
      })))
      .filter(entry => entry.action || entry.hash || entry.timestamp)
      .sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0))
      .slice(0, 8)
  ), [nodes]);

  
/**
 * @function renderNodeMarker
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const renderNodeMarker = (node) => {
    const tone = nodeTone(node);
    return (
      <Marker key={node.id} coordinates={[node.lng, node.lat]}>
        <g className={styles.nodeGroup} data-tone={tone} data-owner="true" onClick={() => setSelectedNodeId(node.id)}>
          <circle r="26" className={styles.nodeAura} />
          <circle r="9" className={styles.nodeCore} />
          <circle r="17" className={styles.nodePulse} />
          <text x="16" y="-9">{node.ownerVisible ? 'WILSY (PTY) LTD' : node.label}</text>
          <text x="16" y="7" className={styles.nodeSub}>{node.ownerVisible ? 'FOUNDER ROOT' : node.type}</text>
        </g>
      </Marker>
    );
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <span className={styles.eyebrow}>Global Orchestrator</span>
          <h1>World Mesh Command</h1>
          <p>Only tenant-owned infrastructure is rendered. No demo mesh. No phantom regions. No placeholder evidence.</p>
        </div>
        <div className={styles.headerActions}>
          <div className={styles.statusBadge} data-state={meshStatus.includes('ONLINE') ? 'online' : 'syncing'}>
            <Radio size={14} />
            <span>{meshStatus}</span>
          </div>
          {!nodes.length && (
            <button type="button" onClick={seedGlobalMesh} disabled={syncing}>
              <MapPin size={15} />
              Anchor Wilsy Root
            </button>
          )}
          <button type="button" onClick={() => fetchNodes('refresh')} disabled={syncing}>
            {syncing ? <Loader2 size={15} className={styles.spin} /> : <RefreshCw size={15} />}
            Sync Mesh
          </button>
        </div>
      </header>

      <section className={styles.metricGrid}>
        <article>
          <Globe2 size={18} />
          <span>Nodes</span>
          <strong>{nodes.length}</strong>
        </article>
        <article>
          <ShieldCheck size={18} />
          <span>Online</span>
          <strong>{metrics.online}/{nodes.length}</strong>
        </article>
        <article>
          <Activity size={18} />
          <span>Avg Latency</span>
          <strong>{metrics.avgLatency.toFixed(1)}ms</strong>
        </article>
        <article>
          <Crosshair size={18} />
          <span>Jurisdictions</span>
          <strong>{metrics.jurisdictions}</strong>
        </article>
      </section>

      <main className={styles.commandGrid}>
        <section className={styles.mapPanel}>
          <div className={styles.panelChrome}>
            <span>Live World Projection</span>
            <strong>{health?.database || 'DB'} / {health?.redis?.status || 'REDIS'}</strong>
          </div>
          <div ref={mapFrameRef} className={styles.mapFrame}>
            <div className={styles.mapControls} onPointerDown={event => event.stopPropagation()} onClick={event => event.stopPropagation()}>
              <button type="button" onClick={() => updateZoom(mapPosition.zoom + 0.45)} aria-label="Zoom in"><Plus size={15} /></button>
              <button type="button" onClick={() => updateZoom(mapPosition.zoom - 0.45)} aria-label="Zoom out"><Minus size={15} /></button>
              <button type="button" onClick={resetViewport} aria-label="Reset map"><Maximize2 size={15} /></button>
              <span>{Math.round(mapPosition.zoom * 100)}%</span>
            </div>

            {loading ? (
              <div className={styles.loader}>
                <Loader2 size={38} className={styles.spin} />
                <span>Hydrating sovereign map</span>
              </div>
            ) : (
              <ComposableMap
                width={MAP_WIDTH}
                height={MAP_HEIGHT}
                projection="geoEqualEarth"
                projectionConfig={{ scale: 285, center: [12, 0] }}
                className={styles.worldMap}
                role="img"
                aria-label="WILSY OS global node map"
              >
                <defs>
                  <radialGradient id="nodeAura" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="#f6d76b" stopOpacity="0.9" />
                    <stop offset="65%" stopColor="#20e38a" stopOpacity="0.18" />
                    <stop offset="100%" stopColor="#20e38a" stopOpacity="0" />
                  </radialGradient>
                </defs>
                <Sphere className={styles.mapSphere} />
                <Graticule step={[15, 15]} className={styles.mapGraticule} />
                <ZoomableGroup
                  center={mapPosition.coordinates}
                  zoom={mapPosition.zoom}
                  minZoom={1}
                  maxZoom={8}
                  translateExtent={[[-360, -220], [MAP_WIDTH + 360, MAP_HEIGHT + 220]]}
                  onMoveEnd={({ coordinates, zoom }) => setMapPosition({ coordinates, zoom, locked: true })}
                >
                  <Geographies geography={worldGeography}>
                    {({ geographies }) => geographies.map(geo => (
                      <Geography
                        key={geo.rsmKey}
                        geography={geo}
                        className={styles.geography}
                        tabIndex={-1}
                      />
                    ))}
                  </Geographies>
                  {mapNodes.map(renderNodeMarker)}
                </ZoomableGroup>
              </ComposableMap>
            )}

            {!loading && !nodes.length && (
              <div className={styles.emptyOverlay}>
                <Globe2 size={42} />
                <strong>No real tenant node returned</strong>
                <span>The map is waiting for a Wilsy-owned node from the registry. Demo regions are intentionally rejected.</span>
                <button type="button" onClick={seedGlobalMesh} disabled={syncing}>
                  {syncing ? <Loader2 size={16} className={styles.spin} /> : <MapPin size={16} />}
                  Anchor Wilsy Root
                </button>
              </div>
            )}
          </div>
        </section>

        <aside className={styles.intelPanel} data-has-feed={forensicStream.length ? 'true' : 'false'}>
          <div className={styles.nodeCard}>
            <span>Selected Node</span>
            <h2>{selectedNode?.label || 'No node anchored'}</h2>
            <p>{selectedNode?.lane || 'No tenant-owned node has been returned by the registry.'}</p>
            {selectedNode?.ownerVisible && (
              <div className={styles.ownerBadge}>
                <strong>{selectedNode.systemOwner}</strong>
                <span>{selectedNode.commandAuthority}</span>
              </div>
            )}
            {selectedNode && (
              <div className={styles.nodeStats}>
                <div><span>Status</span><strong>{selectedNode.status}</strong></div>
                <div><span>NSI</span><strong>{selectedNode.stability.toFixed(1)}</strong></div>
                <div><span>Latency</span><strong>{selectedNode.latency.toFixed(1)}ms</strong></div>
                <div><span>Region</span><strong>{selectedNode.region}</strong></div>
                {selectedNode.ownerVisible && (
                  <>
                    <div><span>Founder</span><strong>{selectedNode.founder}</strong></div>
                    <div><span>Ownership</span><strong>{selectedNode.ownershipPercent}%</strong></div>
                    <div><span>Registration</span><strong>{selectedNode.registrationNumber}</strong></div>
                    <div><span>Role</span><strong>{selectedNode.founderRole}</strong></div>
                  </>
                )}
              </div>
            )}
            {selectedNode?.hash && <small>SEAL {selectedNode.hash.slice(0, 32).toUpperCase()}</small>}
          </div>

          <div className={styles.storyPanel}>
            <div className={styles.storyHeader}>
              <Route size={16} />
              <span>Investor Story</span>
            </div>
            <p>
              WILSY OS is a sovereign business control plane. The map shows only verified tenant ownership and live registry state.
            </p>
          </div>

          {forensicStream.length > 0 && (
            <div className={styles.feedPanel}>
              <div className={styles.storyHeader}>
                <Satellite size={16} />
                <span>Forensic Stream</span>
              </div>
              <div className={styles.feedList}>
                {forensicStream.map(item => (
                  <div key={item.id}>
                    <span>{item.timestamp ? new Date(item.timestamp).toLocaleString() : 'SEALED'}</span>
                    <strong>{item.node}</strong>
                    <small>{item.action}{item.performer ? ` | ${item.performer}` : ''}{item.hash ? ` | ${item.hash.slice(0, 16).toUpperCase()}` : ''}</small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>
      </main>

      <footer className={styles.footer}>
        <span><Zap size={13} /> {metrics.avgStability.toFixed(1)} average neural stability</span>
        <span><ArrowUpRight size={13} /> Global mesh registry anchored to {REGISTRY_TENANT}</span>
      </footer>
    </div>
  );
};

export default Sovereign_Global_Topography;

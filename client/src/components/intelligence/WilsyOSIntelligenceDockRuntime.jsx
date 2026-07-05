/* eslint-disable */
import WilsyOSIntelligenceDock from './WilsyOSIntelligenceDock.jsx';

/**
 * @function WilsyOSIntelligenceDockRuntime
 * @description Mounts the Wilsy OS Intelligence dock separately from the launcher so launcher access survives dock render failures.
 * @returns {JSX.Element} Wilsy AI dock runtime.
 * @collaboration WilsyOSIntelligenceDock, split runtime launcher, client index runtime, and tenant productivity shell.
 */
export default function WilsyOSIntelligenceDockRuntime() {
  return <WilsyOSIntelligenceDock />;
}

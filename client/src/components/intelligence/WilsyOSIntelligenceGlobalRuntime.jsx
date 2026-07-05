/* eslint-disable */
import WilsyOSIntelligenceDock from './WilsyOSIntelligenceDock.jsx';
import WilsyOSIntelligenceLauncher from './WilsyOSIntelligenceLauncher.jsx';

/**
 * @function WilsyOSIntelligenceGlobalRuntime
 * @description Mounts exactly one Wilsy AI dock and one compact launcher from the single global AI runtime.
 * @returns {JSX.Element} Single Wilsy AI global runtime.
 * @collaboration WilsyOSIntelligenceDock, WilsyOSIntelligenceLauncher, client index runtime, document review panel, and tenant productivity shell.
 */
export default function WilsyOSIntelligenceGlobalRuntime() {
  return (
    <>
      <WilsyOSIntelligenceDock />
      <WilsyOSIntelligenceLauncher />
    </>
  );
}

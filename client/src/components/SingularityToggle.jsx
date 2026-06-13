/* eslint-disable */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Command, Power, RadioTower, ShieldCheck, Sparkles } from 'lucide-react';
import styles from './SingularityToggle.module.css';

const PRIMARY_STORAGE_KEY = 'wilsy:singularityMode';
const LEGACY_STORAGE_KEY = 'useSingularity';
const TOAST_DURATION = 3200;


/**
 * @function readStoredMode
 * @memberof WILSY_OS_CORE
 * @description Sovereign-grade operational asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix framework core execution output feedback
 */
const readStoredMode = () => {
  try {
    const primary = localStorage.getItem(PRIMARY_STORAGE_KEY);
    if (primary === 'singularity') return true;
    if (primary === 'legacy') return false;
    return localStorage.getItem(LEGACY_STORAGE_KEY) === 'true';
  } catch {
    return false;
  }
};


/**
 * @function persistMode
 * @memberof WILSY_OS_CORE
 * @description Sovereign-grade operational asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix framework core execution output feedback
 */
const persistMode = (enabled) => {
  localStorage.setItem(PRIMARY_STORAGE_KEY, enabled ? 'singularity' : 'legacy');
  localStorage.setItem(LEGACY_STORAGE_KEY, enabled ? 'true' : 'false');
};


/**
 * @function SingularityToggle
 * @memberof WILSY_OS_CORE
 * @description Sovereign-grade operational asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix framework core execution output feedback
 */
const SingularityToggle = () => {
  const [isEnabled, setIsEnabled] = useState(() => readStoredMode());
  const [showToast, setShowToast] = useState(false);
  const [showControl, setShowControl] = useState(() => localStorage.getItem('wilsyDebug') === 'true');
  const toastTimerRef = useRef(null);

  const logDebug = useCallback((message, payload) => {
    const debugEnabled = import.meta.env.DEV || localStorage.getItem('wilsyDebug') === 'true';
    if (debugEnabled) {
      console.info(`[SINGULARITY] ${message}`, payload || '');
    }
  }, []);

  const publishModeChange = useCallback((enabled, source = 'manual') => {
    const previousState = readStoredMode();
    persistMode(enabled);
    setIsEnabled(enabled);
    if (showControl) setShowToast(true);

    if (toastTimerRef.current) {
      clearTimeout(toastTimerRef.current);
    }

    toastTimerRef.current = setTimeout(() => {
      setShowToast(false);
    }, TOAST_DURATION);

    window.dispatchEvent(new CustomEvent('singularity:toggle', {
      detail: {
        enabled,
        mode: enabled ? 'singularity' : 'legacy',
        previousState,
        source,
        timestamp: Date.now()
      }
    }));

    logDebug(`Mode switched to ${enabled ? 'SINGULARITY' : 'LEGACY'}`, { source });
  }, [logDebug, showControl]);

  const toggleMode = useCallback((source = 'manual') => {
    publishModeChange(!readStoredMode(), source);
  }, [publishModeChange]);

  useEffect(() => {
    logDebug(`Mode anchored as ${isEnabled ? 'SINGULARITY' : 'LEGACY'}`);

    
/**
 * @function handleKeyDown
 * @memberof WILSY_OS_CORE
 * @description Sovereign-grade operational asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix framework core execution output feedback
 */
const handleKeyDown = (event) => {
      const isShortcut = (event.ctrlKey || event.metaKey)
        && event.shiftKey
        && event.key.toLowerCase() === 's';

      if (!isShortcut) return;

      event.preventDefault();
      event.stopPropagation();
      toggleMode('keyboard');
    };

    
/**
 * @function handleStorage
 * @memberof WILSY_OS_CORE
 * @description Sovereign-grade operational asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix framework core execution output feedback
 */
const handleStorage = (event) => {
      if (event.key === PRIMARY_STORAGE_KEY || event.key === LEGACY_STORAGE_KEY) {
        setIsEnabled(readStoredMode());
      }
      if (event.key === 'wilsyDebug') {
        setShowControl(localStorage.getItem('wilsyDebug') === 'true');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('storage', handleStorage);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('storage', handleStorage);
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current);
      }
    };
  }, [isEnabled, logDebug, toggleMode]);

  const modeLabel = isEnabled ? 'Singularity' : 'Legacy';
  const modeDescriptor = isEnabled ? 'Founder cockpit active' : 'Compatibility bridge active';

  if (!showControl) return null;

  return (
    <aside className={styles.anchor} aria-label="Singularity mode control">
      <button
        type="button"
        className={`${styles.toggle} ${isEnabled ? styles.enabled : styles.legacy}`}
        aria-pressed={isEnabled}
        aria-label={`Switch ${isEnabled ? 'off' : 'on'} Singularity mode`}
        title="Ctrl+Shift+S or Command+Shift+S"
        onClick={() => toggleMode('button')}
      >
        <span className={styles.iconWell} aria-hidden="true">
          {isEnabled ? <Sparkles size={18} /> : <ShieldCheck size={18} />}
        </span>
        <span className={styles.copy}>
          <span className={styles.eyebrow}>Mode</span>
          <strong>{modeLabel}</strong>
        </span>
        <span className={styles.hotkey} aria-hidden="true">
          <Command size={13} />
          <span>Shift S</span>
        </span>
        <span className={styles.statusDot} aria-hidden="true" />
      </button>

      <div
        className={`${styles.toast} ${showToast ? styles.toastVisible : ''} ${isEnabled ? styles.enabled : styles.legacy}`}
        role="status"
        aria-live="polite"
      >
        <div className={styles.toastRail} aria-hidden="true">
          {isEnabled ? <RadioTower size={18} /> : <Power size={18} />}
        </div>
        <div className={styles.toastCopy}>
          <span>{isEnabled ? 'Singularity Engine Online' : 'Legacy Engine Online'}</span>
          <strong>{modeDescriptor}</strong>
        </div>
      </div>
    </aside>
  );
};

export default SingularityToggle;

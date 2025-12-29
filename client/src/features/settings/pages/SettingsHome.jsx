import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { toggleDarkMode, setLanguage } from '../reducers/settingsSlice';

export default function SettingsHome() {
  const dispatch = useDispatch();
  const settings = useSelector(s => s?.settings) || {};
  const dark = !!settings.darkMode;
  const language = settings.language || 'en';

  return (
    <div style={{ padding: 16, maxWidth: 640 }}>
      <h2>Settings</h2>

      <section style={{ marginTop: 16 }}>
        <h3>Appearance</h3>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={dark}
            onChange={() => dispatch(toggleDarkMode())}
          />
          Dark mode
        </label>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Language</h3>
        <select
          value={language}
          onChange={(e) => dispatch(setLanguage(e.target.value))}
          style={{ padding: '8px 10px', border: '1px solid #ccc', borderRadius: 6 }}
        >
          <option value="en">English</option>
          <option value="zu">Zulu</option>
          <option value="xh">Xhosa</option>
          <option value="af">Afrikaans</option>
        </select>
      </section>

      <p style={{ marginTop: 24, color: '#666' }}>
        Changes persist in Redux; connect your theme provider to settings.darkMode if you’d like global styling to flip.
      </p>
    </div>
  );
}

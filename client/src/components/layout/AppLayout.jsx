import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

import { ThemeProvider as ScThemeProvider } from 'styled-components';
import projectTheme from '../../styles/theme';
import { ThemeProvider as UiModeProvider } from '../../context/ThemeContext';

const fallbackTheme = {
  colors: {
    header: '#ffffff',
    headerText: '#333333',
    footer: '#ffffff',
    textMuted: '#6c757d',
    border: '#e0e0e0',
    primary: '#007bff',
    background: '#ffffff',
    backgroundLight: '#f7f7f7',
    text: '#222222',
    danger: '#dc3545',
  },
};

const theme = projectTheme && typeof projectTheme === 'object' ? projectTheme : fallbackTheme;

export default function AppLayout() {
  return (
    <UiModeProvider>
      <ScThemeProvider theme={theme}>
        <div style={{
          minHeight:'100vh',
          display:'grid',
          gridTemplateRows:'64px 1fr 48px',
          gridTemplateColumns:'220px 1fr',
          gridTemplateAreas:`"header header" "sidebar main" "footer footer"`,
          background:'#fff'
        }}>
          <div style={{gridArea:'header'}}><Header /></div>
          <div style={{gridArea:'sidebar'}}><Sidebar /></div>
          <main style={{gridArea:'main', padding:16}}>
            <Outlet />
          </main>
          <div style={{gridArea:'footer'}}><Footer /></div>
        </div>
      </ScThemeProvider>
    </UiModeProvider>
  );
}

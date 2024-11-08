// ~/legal-doc-system/client/src/GlobalStyle.js

import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  /* CSS Reset */
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  /* Root Variables */
  :root {
    --primary-color: ${({ theme }) => theme.colors?.primary || '#0069d9'};
    --secondary-color: ${({ theme }) => theme.colors?.secondary || '#0053ba'};
    --background-color: ${({ theme }) => theme.colors?.background || '#f4f4f9'};
    --text-color: ${({ theme }) => theme.colors?.text || '#333'};
    --accent-color: ${({ theme }) => theme.colors?.accent || '#007bff'};
    --error-color: ${({ theme }) => theme.colors?.error || '#e74c3c'};
    --success-color: ${({ theme }) => theme.colors?.success || '#28a745'};
    --warning-color: ${({ theme }) => theme.colors?.warning || '#ffc107'};
    --info-color: ${({ theme }) => theme.colors?.info || '#17a2b8'};
    --light-color: ${({ theme }) => theme.colors?.light || '#f8f9fa'};
    --dark-color: ${({ theme }) => theme.colors?.dark || '#343a40'};
    --font-family: ${({ theme }) => theme.fonts?.primary || 'Arial, sans-serif'};
    --heading-font: ${({ theme }) => theme.fonts?.heading || 'Georgia, serif'};
    --mono-font: ${({ theme }) => theme.fonts?.mono || 'Courier New, monospace'};
    --border-radius: ${({ theme }) => theme.borderRadius || '5px'};
    --spacing-xs: ${({ theme }) => theme.spacing?.xs || '4px'};
    --spacing-sm: ${({ theme }) => theme.spacing?.sm || '8px'};
    --spacing-md: ${({ theme }) => theme.spacing?.md || '16px'};
    --spacing-lg: ${({ theme }) => theme.spacing?.lg || '24px'};
    --spacing-xl: ${({ theme }) => theme.spacing?.xl || '32px'};
    --spacing-2xl: ${({ theme }) => theme.spacing?.['2xl'] || '40px'};
    --transition: ${({ theme }) => theme.transition || '0.3s ease-in-out'};
    --shadow: ${({ theme }) => theme.shadow || '0 4px 8px rgba(0, 0, 0, 0.1)'};
    --breakpoint-mobile: ${({ theme }) => theme.breakpoints?.mobile || '480px'};
    --breakpoint-tablet: ${({ theme }) => theme.breakpoints?.tablet || '768px'};
    --breakpoint-laptop: ${({ theme }) => theme.breakpoints?.laptop || '1024px'};
    --breakpoint-desktop: ${({ theme }) => theme.breakpoints?.desktop || '1200px'};
    --breakpoint-2xl: ${({ theme }) => theme.breakpoints?.['2xl'] || '1440px'};
  }

  /* Global Styles */
  html, body {
    height: 100%;
    font-family: var(--font-family);
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  #root {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* Typography */
  h1, h2, h3, h4, h5, h6 {
    font-family: var(--heading-font);
    color: var(--text-color);
    margin-bottom: 1rem;
  }

  p {
    margin-bottom: 1rem;
    line-height: 1.5;
  }

  /* Links */
  a {
    text-decoration: none;
    color: var(--primary-color);
    transition: color var(--transition);

    &:hover {
      color: var(--secondary-color);
    }
  }

  /* Buttons */
  button {
    font-family: var(--font-family);
    cursor: pointer;
    background-color: var(--primary-color);
    color: #ffffff;
    border: none;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--border-radius);
    transition: background-color var(--transition), transform 0.2s;

    &:hover {
      background-color: var(--secondary-color);
      transform: translateY(-2px);
      box-shadow: var(--shadow);
    }

    &:active {
      transform: translateY(0);
      box-shadow: none;
    }

    &:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }
  }

  /* Inputs */
  input, textarea, select {
    font-family: var(--font-family);
    border: 1px solid var(--accent-color);
    padding: var(--spacing-sm);
    border-radius: var(--border-radius);
    transition: border-color var(--transition);
    width: 100%;
    margin-bottom: 1rem;

    &:focus {
      border-color: var(--primary-color);
      outline: none;
      box-shadow: 0 0 0 2px rgba(0, 112, 243, 0.2);
    }
  }

  /* Scrollbar Styling */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-thumb {
    background-color: var(--accent-color);
    border-radius: 4px;
    transition: background-color var(--transition);
  }

  ::-webkit-scrollbar-thumb:hover {
    background-color: var(--primary-color);
  }

  /* Utility Classes */
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);

    @media (max-width: var(--breakpoint-tablet)) {
      padding: 0 var(--spacing-md);
    }

    @media (max-width: var(--breakpoint-mobile)) {
      padding: 0 var(--spacing-sm);
    }
  }

  /* Animations */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Apply Fade-in Animation */
  .fade-in {
    animation: fadeIn 0.5s ease-in-out;
  }

  /* Responsive Images */
  img {
    max-width: 100%;
    height: auto;
    display: block;
  }

  /* Box Shadows */
  .box-shadow {
    box-shadow: var(--shadow);
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: var(--spacing-lg);
  }

  th, td {
    padding: var(--spacing-sm);
    border: 1px solid var(--accent-color);
    text-align: left;
  }

  th {
    background-color: var(--secondary-color);
    color: var(--light-color);
  }

  /* Forms */
  form {
    display: flex;
    flex-direction: column;
  }
`;

export default GlobalStyle;

// ~/client/src/GlobalStyle.js
import { createGlobalStyle } from 'styled-components';
import './assets/fonts/fonts.css'; // ✅ Add the font imports

const GlobalStyle = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html, body {
    font-family: 'Poppins Regular', 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.text};
    font-size: 16px;
    line-height: 1.6;
    transition: background-color 0.3s ease, color 0.3s ease;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins Bold', sans-serif;
    font-weight: 700;
    color: ${({ theme }) => theme.colors.text};
    margin-bottom: 1rem;
    line-height: 1.3;
  }

  h1 { font-size: 2.5rem; }
  h2 { font-size: 2rem; }
  h3 { font-size: 1.75rem; }
  h4 { font-size: 1.5rem; }
  h5 { font-size: 1.25rem; }
  h6 { font-size: 1rem; }

  a {
    color: ${({ theme }) => theme.colors.primary};
    text-decoration: none;
    transition: color 0.2s ease;
  }

  a:hover {
    color: ${({ theme }) => theme.colors.hover || '#0b3954'};
  }

  button {
    font-family: 'Poppins Medium', sans-serif;
    font-size: 1rem;
    padding: 0.5rem 1rem;
    background-color: ${({ theme }) => theme.colors.primary};
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  button:hover {
    background-color: ${({ theme }) => theme.colors.hover || '#0b3954'};
  }

  input, textarea, select {
    font-family: 'Poppins Regular', sans-serif;
    font-size: 1rem;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 100%;
  }

  input:focus, textarea:focus, select:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    outline: none;
  }

  ::-webkit-scrollbar {
    width: 10px;
  }

  ::-webkit-scrollbar-thumb {
    background-color: ${({ theme }) => theme.colors.primary};
    border-radius: 10px;
  }

  ::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.sidebarBg};
  }
`;

export default GlobalStyle;

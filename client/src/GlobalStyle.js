// /src/GlobalStyle.js
import { createGlobalStyle } from 'styled-components';

/**
 * GlobalStyle defines a CSS reset and sets common styles for typography,
 * layout, and interactive elements across the entire application.
 */
const GlobalStyle = createGlobalStyle`
  /* Reset default browser styles for consistency */
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  /* Global styles for the document body */
  body {
    margin: 0;
    font-family: 'Roboto', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f5f5f5;
    color: #212121;
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* Headings */
  h1, h2, h3, h4, h5, h6 {
    font-weight: 500;
    color: #0d47a1; /* Primary blue for headings */
    margin-bottom: 1rem;
    line-height: 1.3;
  }

  h1 { font-size: 2.5rem; }
  h2 { font-size: 2rem; }
  h3 { font-size: 1.75rem; }
  h4 { font-size: 1.5rem; }
  h5 { font-size: 1.25rem; }
  h6 { font-size: 1rem; }

  /* Link styling */
  a {
    text-decoration: none;
    color: #0d47a1;
    transition: color 0.2s ease-in-out;
  }
  a:hover, a:focus {
    color: #0b3954;
    outline: none;
  }

  /* Button styling */
  button {
    font-family: 'Roboto', sans-serif;
    font-size: 1rem;
    padding: 0.5rem 1rem;
    color: #fff;
    background-color: #0d47a1;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
  }
  button:hover, button:focus {
    background-color: #0b3954;
    outline: none;
  }

  /* Input, textarea, select styling */
  input, textarea, select {
    font-family: 'Roboto', sans-serif;
    font-size: 1rem;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 100%;
  }
  input:focus, textarea:focus, select:focus {
    border-color: #0d47a1;
    outline: none;
  }

  /* Responsive images */
  img {
    max-width: 100%;
    height: auto;
    display: block;
  }

  /* List styling */
  ul, ol {
    margin-left: 1.5rem;
    margin-bottom: 1rem;
    padding-left: 1rem;
  }
  ul { list-style-type: disc; }
  ol { list-style-type: decimal; }
  li { margin-bottom: 0.5rem; }

  /* Container for consistent spacing */
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  /* Accessibility: Visible focus outlines */
  :focus {
    outline: 2px solid #0d47a1;
    outline-offset: 2px;
  }

  /* Custom scrollbar for modern browsers */
  ::-webkit-scrollbar { width: 10px; }
  ::-webkit-scrollbar-thumb {
    background: #0d47a1;
    border-radius: 10px;
  }
  ::-webkit-scrollbar-thumb:hover { background: #0b3954; }
  ::-webkit-scrollbar-track { background: #f5f5f5; }
`;

export default GlobalStyle;

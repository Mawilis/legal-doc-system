// ~/legal-doc-system/client/src/theme.js

const theme = {
    colors: {
        primary: '#0070f3',         // Blue
        secondary: '#1c1c1e',       // Dark Gray
        background: '#f5f5f5',      // Light Gray
        text: '#333333',            // Dark Text
        accent: '#e2e2e2',           // Light Accent
        error: '#ff4d4f',            // Red
        success: '#52c41a',          // Green
        warning: '#faad14',          // Yellow
        info: '#1890ff',             // Light Blue
        light: '#ffffff',            // White
        dark: '#000000',             // Black
        // Add more colors as needed
    },
    fonts: {
        primary: '"Roboto", sans-serif',
        heading: '"Montserrat", sans-serif',
        mono: '"Fira Code", monospace',
        // Add more fonts as needed
    },
    spacing: {
        xs: '0.25rem',
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '3rem',
        // Add more spacing as needed
    },
    breakpoints: {
        mobile: '480px',
        tablet: '768px',
        laptop: '1024px',
        desktop: '1280px',
        '2xl': '1536px',
        // Add more breakpoints as needed
    },
    borderRadius: '8px',
    transition: '0.3s ease-in-out',
    shadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    // Add more properties as needed
};

export default theme;

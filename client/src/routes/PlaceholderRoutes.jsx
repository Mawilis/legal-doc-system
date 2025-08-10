// ~/client/src/routes/PlaceholderRoutes.jsx

import React from 'react';
import { Routes, Route } from 'react-router-dom';

const createPlaceholder = (name) => () => (
    <div style={{ padding: '2rem', fontSize: '1.2rem' }}>
        <h2>{name} Page</h2>
        <p>This is a placeholder page for <strong>{name}</strong>.</p>
    </div>
);

const routes = [
    'dashboard', 'documents', 'profile', 'chat', 'settings', 'admin',
    'admin/users', 'search', 'tags', 'shield', 'home', 'trash',
    'pencil', 'create', 'folders', 'lock', 'gear', 'bell', 'login'
];

const PlaceholderRoutes = () => (
    <Routes>
        {routes.map((path) => (
            <Route
                key={path}
                path={`/${path}`}
                element={React.createElement(createPlaceholder(path))}
            />
        ))}
    </Routes>
);

export default PlaceholderRoutes;

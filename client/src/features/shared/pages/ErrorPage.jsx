// ~/legal-doc-system/client/src/pages/ErrorPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

const ErrorPage = () => {
    const navigate = useNavigate();

    return (
        <div>
            <h1>Oops! Something went wrong.</h1>
            <p>The page you are looking for does not exist.</p>
            <button onClick={() => navigate('/')}>Go Back Home</button>
        </div>
    );
};

export default ErrorPage;

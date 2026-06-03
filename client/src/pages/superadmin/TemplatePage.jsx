import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { superAdminAPI } from '../../api/superadmin';

const TemplatePage = ({ title, endpoint }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await superAdminAPI.get(endpoint);
        setData(response.data);
      } catch (err) {
        setError(err.message || 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  if (loading) {
    return <div data-testid="loading">Loading...</div>;
  }

  if (error) {
    return <div data-testid="error">Error: {error}</div>;
  }

  return (
    <div data-testid="data-container">
      <h1>{title}</h1>
      <pre data-testid="json-data">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

TemplatePage.propTypes = {
  title: PropTypes.string.isRequired,
  endpoint: PropTypes.string.isRequired
};

export default TemplatePage;


// ~/client/src/features/settings/pages/Lock.jsx

import React from 'react';
import styled from 'styled-components';
import { useSelector } from 'react-redux';

const Container = styled.div`
  padding: 2rem;
`;

const Heading = styled.h2`
  margin-bottom: 1rem;
`;

const Lock = () => {
    const { user } = useSelector((state) => state.auth);

    if (user?.role !== 'admin') {
        return <Container><h3>Access Denied</h3></Container>;
    }

    return (
        <Container>
            <Heading>Security Settings</Heading>
            <p>Admin-only security and lock controls will appear here.</p>
        </Container>
    );
};

export default Lock;
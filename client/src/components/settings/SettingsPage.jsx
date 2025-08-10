import React from 'react';
import styled from 'styled-components';
import Card from '../atoms/Card';

const Container = styled.div`
  padding: 40px;
`;

const SettingsPage = () => {
    return (
        <Container>
            <Card>
                <h2>Settings</h2>
                <p>This page will allow the user to update preferences and security.</p>
            </Card>
        </Container>
    );
};

export default SettingsPage;

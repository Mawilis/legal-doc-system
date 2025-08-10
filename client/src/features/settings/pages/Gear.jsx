// ~/client/src/features/settings/pages/Gear.jsx

import React, { useState } from 'react';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

const Container = styled.div`
  padding: 2rem;
`;

const Section = styled.div`
  margin-bottom: 2rem;
`;

const Heading = styled.h2`
  margin-bottom: 1rem;
`;

const Gear = () => {
    const { user } = useSelector((state) => state.auth);
    const [featureX, setFeatureX] = useState(false);

    const handleToggle = () => setFeatureX((prev) => !prev);

    if (user?.role !== 'admin') {
        return <Container><h3>Access Denied</h3></Container>;
    }

    return (
        <Container>
            <Heading>Gear Settings</Heading>

            <Section>
                <FormControlLabel
                    control={<Switch checked={featureX} onChange={handleToggle} />}
                    label="Enable Feature X"
                />
            </Section>
        </Container>
    );
};

export default Gear;

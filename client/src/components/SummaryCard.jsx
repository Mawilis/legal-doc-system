// ~/legal-doc-system/client/src/components/SummaryCard.jsx

import React from 'react';
import styled from 'styled-components';

const Card = styled.div`
  background-color: var(--light-color);
  border: 1px solid var(--accent-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  display: flex;
  align-items: center;
  box-shadow: var(--shadow);
  transition: transform var(--transition), box-shadow var(--transition);

  &:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow);
  }
`;

const IconContainer = styled.div`
  font-size: 2rem;
  color: var(--primary-color);
  margin-right: var(--spacing-md);
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.span`
  font-size: 1rem;
  color: var(--secondary-color);
`;

const Value = styled.span`
  font-size: 1.5rem;
  color: var(--text-color);
  font-weight: bold;
`;

const SummaryCard = ({ icon, title, value }) => {
    return (
        <Card>
            <IconContainer>{icon}</IconContainer>
            <Content>
                <Title>{title}</Title>
                <Value>{value}</Value>
            </Content>
        </Card>
    );
};

export default SummaryCard;

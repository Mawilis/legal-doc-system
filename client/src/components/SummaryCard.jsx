// ~/legal-doc-system/client/src/components/SummaryCard.jsx

import React from 'react';
import styled from 'styled-components';

const Card = styled.div`
  background-color: #f9f9f9; // Light background color
  border: 1px solid #ddd; // Subtle border
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); // Subtle shadow
  transition: transform 0.2s ease, box-shadow 0.2s ease; // Add transitions

  &:hover {
    transform: translateY(-2px); // Slightly lift on hover
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15); // More pronounced shadow on hover
  }
`;

const IconContainer = styled.div`
  font-size: 2rem;
  color: #007bff; // Primary color for the icon
  margin-right: 20px;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.span`
  font-size: 1rem;
  color: #6c757d; // Secondary text color
  margin-bottom: 5px; // Add some space below the title
`;

const Value = styled.span`
  font-size: 1.8rem; // Larger font size for the value
  color: #333; // Darker text color
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
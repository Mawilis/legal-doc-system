import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

const Card = styled.div`
  background-color: var(--card-bg, #f9f9f9);
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  }
`;

const IconContainer = styled.div`
  font-size: 2rem;
  color: var(--icon-color, #007bff);
  margin-right: 20px;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.span`
  font-size: 1rem;
  color: #6c757d;
  margin-bottom: 5px;
`;

const Value = styled.span`
  font-size: 1.8rem;
  color: #333;
  font-weight: bold;
`;

/**
 * SummaryCard Component
 * Displays a stylized card with an icon, title, and value.
 */
const SummaryCard = ({ icon, title, value }) => {
  return (
    <Card role="region" aria-label={`${title} summary`}>
      <IconContainer>{icon}</IconContainer>
      <Content>
        <Title>{title}</Title>
        <Value>{value}</Value>
      </Content>
    </Card>
  );
};

SummaryCard.propTypes = {
  icon: PropTypes.element.isRequired,
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
};

SummaryCard.defaultProps = {
  title: 'Untitled',
  value: 0,
};

export default SummaryCard;

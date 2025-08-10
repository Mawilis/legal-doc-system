// ~/client/src/components/LoadingSpinner.jsx

import React from 'react';
import styled, { keyframes } from 'styled-components';
import PropTypes from 'prop-types';

/**
 * Defines the rotation animation for the spinner using keyframes.
 */
const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

/**
 * A styled container that centers the spinner and can display a loading message.
 */
const SpinnerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  gap: 1rem;
`;

/**
 * The visual spinner element, created with pure CSS for high performance.
 * It uses a border trick to create the spinning circle and is theme-aware.
 */
const Spinner = styled.div`
  border: 5px solid rgba(0, 0, 0, 0.1); /* The light grey track */
  border-left-color: ${({ theme }) => theme.colors?.primary || '#007bff'}; /* The colored spinning part */
  border-radius: 50%;
  width: ${({ size }) => size || '50px'};
  height: ${({ size }) => size || '50px'};
  animation: ${spin} 1s linear infinite; /* Apply the rotation animation */
`;

const LoadingText = styled.p`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textSecondary || '#555'};
  font-weight: 500;
`;

/**
 * A lightweight, performant, and theme-aware loading spinner component.
 * It uses styled-components and CSS animations, requiring no external UI libraries.
 *
 * @param {object} props
 * @param {string} [props.size] - The size of the spinner (e.g., '30px', '5rem').
 * @param {string} [props.message] - An optional message to display below the spinner.
 */
const LoadingSpinner = ({ size, message }) => (
  <SpinnerWrapper>
    <Spinner size={size} />
    {message && <LoadingText>{message}</LoadingText>}
  </SpinnerWrapper>
);

// --- PropTypes for Code Quality ---
LoadingSpinner.propTypes = {
  size: PropTypes.string,
  message: PropTypes.string,
};

export default LoadingSpinner;

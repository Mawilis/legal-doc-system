import React from 'react';
import styled, { keyframes } from 'styled-components';

// Define the spin animation
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// Styled component for the spinner
const Spinner = styled.div`
  border: 8px solid #f3f3f3; /* Light gray border */
  border-top: 8px solid #007bff; /* Blue border for the spinning part */
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: ${spin} 1s linear infinite; /* Apply the spin animation */
  margin: 50px auto; /* Center the spinner */
`;

// LoadingSpinner component
const LoadingSpinner = () => {
  return <Spinner />; // Render the styled spinner
};

export default LoadingSpinner;
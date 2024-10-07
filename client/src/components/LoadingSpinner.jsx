import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Spinner = styled.div`
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: ${spin} 2s linear infinite;
  margin: 50px auto;
`;

const LoadingSpinner = () => {
    return <Spinner />;
};

export default LoadingSpinner;

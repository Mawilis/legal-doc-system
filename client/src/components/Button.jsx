// ~/legal-doc-system/client/src/components/Button.jsx

import styled from 'styled-components';

// Creating a reusable Button component using styled-components
const Button = styled.button`
  background-color: ${(props) => props.theme.colors.primary};
  color: white;
  padding: ${(props) => props.theme.spacing.md};
  border: none;
  border-radius: ${(props) => props.theme.borderRadius};
  cursor: pointer;
  transition: ${(props) => props.theme.transition};

  &:hover {
    background-color: ${(props) => props.theme.colors.secondary};
  }

  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
`;

export default Button;

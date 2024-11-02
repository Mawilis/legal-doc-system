import styled from 'styled-components';

const Button = styled.button`
  background: ${(props) => props.theme.colors.primary};
  color: white;
  padding: ${(props) => props.theme.spacing.small};
  border: none;
  border-radius: 4px;
`;

export default Button;

// ~/legal-doc-system/client/src/components/Typography.jsx

import styled from 'styled-components';

export const Heading = styled.h1`
  font-family: ${(props) => props.theme.typography.headingFont};
  font-weight: ${(props) => props.theme.typography.headingWeight};
  color: ${(props) => props.theme.colors.primary};
  margin-bottom: ${(props) => props.theme.spacing.md};
`;

export const Text = styled.p`
  font-family: ${(props) => props.theme.typography.fontFamily};
  color: ${(props) => props.theme.colors.text};
  font-size: ${(props) => props.theme.typography.fontSizeBase};
  line-height: 1.5;
`;

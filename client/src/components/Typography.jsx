// ~/legal-doc-system/client/src/components/Typography.jsx

import styled, { css } from 'styled-components';

export const Heading = styled.h1`
  font-family: ${({ theme }) => theme.typography.headingFont};
  font-weight: ${({ theme }) => theme.typography.headingWeight};
  color: ${({ theme, color }) => color || theme.colors.primary}; // Allow custom color
  margin-bottom: ${({ theme, marginBottom }) => marginBottom || theme.spacing.md}; // Allow custom margin

  /* Add styles for different heading levels (h1, h2, etc.) */
  ${({ level }) => {
    switch (level) {
      case 'h2':
        return css`
          font-size: 2.5rem; /* Example size for h2 */
        `;
      case 'h3':
        return css`
          font-size: 2rem; /* Example size for h3 */
        `;
      // ... more heading levels
      default:
        return css`
          font-size: 3rem; /* Default size for h1 */
        `;
    }
  }}
`;

export const Text = styled.p`
  font-family: ${({ theme }) => theme.typography.fontFamily};
  color: ${({ theme, color }) => color || theme.colors.text}; // Allow custom color
  font-size: ${({ theme, size }) => { // Allow custom size
    switch (size) {
      case 'small':
        return theme.typography.fontSizeSm;
      case 'large':
        return theme.typography.fontSizeLg;
      // ... more sizes
      default:
        return theme.typography.fontSizeBase;
    }
  }};
  line-height: 1.5;
  margin-bottom: ${({ theme, marginBottom }) => marginBottom || theme.spacing.sm}; // Allow custom margin
`;
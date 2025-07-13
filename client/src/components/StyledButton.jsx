import styled, { css } from "styled-components";

const Button = styled.button`
  /* Basic Button Styles */
  background-color: ${({ theme, variant }) => {
    switch (variant) {
      case "primary":
        return theme.colors.primary;
      case "secondary":
        return theme.colors.secondary;
      case "danger":
        return theme.colors.danger;
      // ... more variants
      default:
        return theme.colors.primary;
    }
  }};
  color: white;
  border: none;
  border-radius: 5px; /* Slightly rounded corners */
  cursor: pointer;
  font-weight: 500;
  transition:
    background-color 0.2s ease,
    transform 0.1s ease,
    box-shadow 0.2s ease; /* Add transitions for smooth effects */

  /* Hover State */
  &:hover {
    background-color: ${({ theme, variant }) => {
    switch (variant) {
      case "primary":
        return theme.colors.primaryDark;
      case "secondary":
        return theme.colors.secondaryDark;
      case "danger":
        return theme.colors.dangerDark;
      // ... more variants
      default:
        return theme.colors.primaryDark;
    }
  }};
    transform: translateY(-1px); /* Slightly lift on hover */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Add a subtle shadow on hover */
  }

  /* Active State */
  &:active {
    transform: translateY(1px); /* Slightly push down on click */
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3); /* Add a more pronounced shadow on click */
  }

  /* Focus State */
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25); /* Add a focus ring */
  }

  /* Disabled State */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Size Variations */
  ${({ size }) =>
    size === "large" &&
    css`
      font-size: 1.2rem;
      padding: 12px 20px; /* Adjust padding for large size */
    `}

  ${({ size }) =>
    size === "small" &&
    css`
      font-size: 0.8rem;
      padding: 8px 12px; /* Adjust padding for small size */
    `}

  /* ... more size variations */
`;

export default Button;
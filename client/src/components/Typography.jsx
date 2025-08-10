import styled, { css } from 'styled-components';
import PropTypes from 'prop-types';

// --- Helper Maps for Font Sizes ---

const HEADING_SIZES = {
  h1: { desktop: '3rem', mobile: '2.2rem' },
  h2: { desktop: '2.5rem', mobile: '1.9rem' },
  h3: { desktop: '2rem', mobile: '1.7rem' },
  h4: { desktop: '1.75rem', mobile: '1.5rem' },
  h5: { desktop: '1.5rem', mobile: '1.3rem' },
  h6: { desktop: '1.25rem', mobile: '1.1rem' },
};

const TEXT_SIZES = {
  xs: '0.75rem',
  sm: '0.875rem',
  md: '1rem',
  lg: '1.125rem',
  xl: '1.25rem',
};


/**
 * A responsive and theme-aware heading component.
 * It dynamically sets its tag and styles based on props.
 *
 * @param {object} props
 * @param {('h1'|'h2'|'h3'|'h4'|'h5'|'h6')} [props.as='h1'] - The HTML heading tag to render.
 * @param {string} [props.color] - Custom text color. Defaults to theme's primary color.
 * @param {string} [props.marginBottom] - Custom bottom margin. Defaults to theme spacing.
 */
export const Heading = styled.h1.attrs(({ as }) => ({
  as: as || 'h1',
}))`
  font-family: ${({ theme }) => theme.typography?.headingFont || 'sans-serif'};
  font-weight: ${({ theme }) => theme.typography?.headingWeight || 700};
  color: ${({ theme, color }) => color || theme.colors?.primary || '#333'};
  margin: 0;
  margin-bottom: ${({ theme, marginBottom }) => marginBottom || theme.spacing?.md || '1rem'};
  line-height: 1.2;

  /* Apply font size based on the 'as' prop */
  font-size: ${({ as }) => HEADING_SIZES[as]?.desktop || HEADING_SIZES.h1.desktop};

  /* Responsive font sizes for smaller screens */
  @media (max-width: 768px) {
    font-size: ${({ as }) => HEADING_SIZES[as]?.mobile || HEADING_SIZES.h1.mobile};
  }
`;

/**
 * A flexible and theme-aware text component for paragraphs and other text blocks.
 *
 * @param {object} props
 * @param {('xs'|'sm'|'md'|'lg'|'xl')} [props.size='md'] - The font size of the text.
 * @param {string} [props.color] - Custom text color. Defaults to theme's text color.
 * @param {string} [props.marginBottom] - Custom bottom margin. Defaults to theme spacing.
 * @param {boolean} [props.bold=false] - If true, applies bold font weight.
 * @param {boolean} [props.italic=false] - If true, applies italic font style.
 * @param {boolean} [props.underline=false] - If true, applies an underline text decoration.
 */
export const Text = styled.p`
  font-family: ${({ theme }) => theme.typography?.fontFamily || 'sans-serif'};
  color: ${({ theme, color }) => color || theme.colors?.text || '#555'};
  line-height: 1.6;
  margin: 0;
  margin-bottom: ${({ theme, marginBottom }) => marginBottom || theme.spacing?.sm || '0.75rem'};
  font-size: ${({ theme, size = 'md' }) => TEXT_SIZES[size] || theme.typography?.fontSizeBase || '1rem'};

  /* --- Style Modifiers --- */
  ${({ bold }) => bold && css`font-weight: 700;`}
  ${({ italic }) => italic && css`font-style: italic;`}
  ${({ underline }) => underline && css`text-decoration: underline;`}
`;

// --- PropTypes for Documentation and Type-Checking ---

Heading.propTypes = {
  as: PropTypes.oneOf(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']),
  color: PropTypes.string,
  marginBottom: PropTypes.string,
};

Text.propTypes = {
  size: PropTypes.oneOf(['xs', 'sm', 'md', 'lg', 'xl']),
  color: PropTypes.string,
  marginBottom: PropTypes.string,
  bold: PropTypes.bool,
  italic: PropTypes.bool,
  underline: PropTypes.bool,
};

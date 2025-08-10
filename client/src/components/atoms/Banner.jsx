// ~/legal-doc-system/client/src/components/atoms/Banner.jsx

import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';

// Styled Components
const BannerWrapper = styled.section`
  position: relative;
  width: 100%;
  height: ${({ height }) => height || '300px'};
  background-image: url(${({ backgroundImage }) => backgroundImage});
  background-size: cover;
  background-position: center;
  border-radius: ${({ theme }) => theme?.spacing?.sm || '8px'};
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const Overlay = styled.div`
  background-color: rgba(0, 0, 0, 0.5); /* dark overlay */
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
`;

const Content = styled.div`
  position: relative;
  z-index: 2;
  color: white;
  padding: 20px;
  max-width: 700px;
`;

const Title = styled.h1`
  font-size: 2.4rem;
  margin-bottom: 10px;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  margin-bottom: 20px;
`;

const CTAButton = styled.button`
  background-color: #007bff;
  border: none;
  color: white;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.25s ease;

  &:hover {
    background-color: #0056b3;
  }
`;

// Component
const Banner = ({ title, subtitle, img, height, ctaText, ctaLink }) => {
    const navigate = useNavigate();

    const handleCTA = () => {
        if (ctaLink) navigate(ctaLink);
    };

    return (
        <BannerWrapper backgroundImage={img} height={height} role="banner" aria-label={title}>
            <Overlay />
            <Content>
                <Title>{title}</Title>
                {subtitle && <Subtitle>{subtitle}</Subtitle>}
                {ctaText && ctaLink && (
                    <CTAButton onClick={handleCTA}>{ctaText}</CTAButton>
                )}
            </Content>
        </BannerWrapper>
    );
};

// Prop Types
Banner.propTypes = {
    title: PropTypes.string.isRequired,
    subtitle: PropTypes.string,
    img: PropTypes.string.isRequired,
    height: PropTypes.string,
    ctaText: PropTypes.string,
    ctaLink: PropTypes.string,
};

export default Banner;

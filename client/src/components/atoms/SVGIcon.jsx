// ~/client/src/components/atoms/SVGIcon.jsx
import React from 'react';
import PropTypes from 'prop-types';

const SVGIcon = ({ src, alt, size = 24, ...rest }) => {
    return (
        <img
            src={src}
            alt={alt || 'icon'}
            width={size}
            height={size}
            style={{ display: 'inline-block', verticalAlign: 'middle' }}
            {...rest}
        />
    );
};

SVGIcon.propTypes = {
    src: PropTypes.string.isRequired,
    alt: PropTypes.string,
    size: PropTypes.number,
};

export default SVGIcon;

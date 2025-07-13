// /Users/wilsonkhanyezi/legal-doc-system/client/src/components/atoms/Icon.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faHome,
    faUser,
    faSignOutAlt,
    faFileAlt,
    // ... add more icons as needed
} from '@fortawesome/free-solid-svg-icons';

const Icon = ({ icon, size, color, spin, ...rest }) => { // Add spin and rest props
    const iconsMap = {
        home: faHome,
        user: faUser,
        logout: faSignOutAlt,
        document: faFileAlt,
        // ... add more icons to the map
    };

    return (
        <FontAwesomeIcon
            icon={iconsMap[icon]}
            size={size}
            color={color}
            spin={spin} // Apply spin animation if needed
            {...rest} // Pass any other props to FontAwesomeIcon
        />
    );
};

Icon.propTypes = {
    icon: PropTypes.string.isRequired,
    size: PropTypes.oneOf(['xs', 'sm', 'lg', '1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x', '10x']), // Define allowed sizes
    color: PropTypes.string,
    spin: PropTypes.bool, // Add prop type for spin
};

Icon.defaultProps = {
    size: '1x',
    color: '#000',
    spin: false, // Default spin to false
};

export default Icon;
// /src/components/atoms/Icon.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faHome,
    faUser,
    faSignOutAlt,
    faFileAlt,
    faCog,
    faBell,
    faPlus,
    faTrash,
    faEdit,
} from '@fortawesome/free-solid-svg-icons';

/**
 * Icon component that wraps FontAwesome for centralized control
 */
const Icon = ({ icon, size, color, spin, className, style, ...rest }) => {
    const iconsMap = {
        home: faHome,
        user: faUser,
        logout: faSignOutAlt,
        document: faFileAlt,
        settings: faCog,
        bell: faBell,
        plus: faPlus,
        trash: faTrash,
        edit: faEdit,
        // extend as needed...
    };

    const faIcon = iconsMap[icon];

    if (!faIcon) {
        console.warn(`[Icon] "${icon}" not found in iconsMap.`);
        return null;
    }

    return (
        <FontAwesomeIcon
            icon={faIcon}
            size={size}
            color={color}
            spin={spin}
            className={className}
            style={style}
            {...rest}
        />
    );
};

Icon.propTypes = {
    icon: PropTypes.string.isRequired,
    size: PropTypes.oneOf([
        'xs', 'sm', 'lg', '1x', '2x', '3x',
        '4x', '5x', '6x', '7x', '8x', '9x', '10x',
    ]),
    color: PropTypes.string,
    spin: PropTypes.bool,
    className: PropTypes.string,
    style: PropTypes.object,
};

Icon.defaultProps = {
    size: '1x',
    color: '#000',
    spin: false,
    className: '',
    style: {},
};

export default Icon;

import React from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faUser, faSignOutAlt, faFileAlt } from '@fortawesome/free-solid-svg-icons';

const Icon = ({ icon, size, color }) => {
    const iconsMap = {
        home: faHome,
        user: faUser,
        logout: faSignOutAlt,
        document: faFileAlt,
    };

    return <FontAwesomeIcon icon={iconsMap[icon]} size={size} color={color} />;
};

Icon.propTypes = {
    icon: PropTypes.string.isRequired,
    size: PropTypes.string,
    color: PropTypes.string,
};

Icon.defaultProps = {
    size: '1x',
    color: '#000',
};

export default Icon;

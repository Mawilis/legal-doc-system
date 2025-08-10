// ~/client/src/components/animations/PageTransition.jsx
import React from 'react';
import { motion } from 'framer-motion';
import PropTypes from 'prop-types';

const PageTransition = ({ children }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
    >
        {children}
    </motion.div>
);

PageTransition.propTypes = {
    children: PropTypes.node.isRequired,
};

export default PageTransition;

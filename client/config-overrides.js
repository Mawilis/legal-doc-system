const { override } = require('customize-cra');
const ModuleScopePlugin = require('react-dev-utils/ModuleScopePlugin');
const path = require('path');

module.exports = override((config) => {
    // Remove ModuleScopePlugin so that our aliases can import from node_modules outside of src
    if (config.resolve.plugins) {
        config.resolve.plugins = config.resolve.plugins.filter(
            (plugin) => !(plugin instanceof ModuleScopePlugin)
        );
    }
    config.resolve.alias = {
        ...config.resolve.alias,
        // Force Material UI to use styled-components instead of Emotion:
        '@mui/styled-engine': path.resolve(__dirname, 'node_modules/@mui/styled-engine-sc'),
        // Ensure all styled-components imports use the same copy:
        'styled-components': path.resolve(__dirname, 'node_modules/styled-components')
    };
    return config;
});

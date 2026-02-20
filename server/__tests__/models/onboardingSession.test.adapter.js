/**
 * TEST ADAPTER - Loads the model properly before running tests
 * Use this to wrap your existing test
 */

const modelLoader = require('../helpers/modelLoader');

// Store the loaded model
let OnboardingSession;

// Override the require to use our loaded model
jest.mock('../../models/OnboardingSession', () => {
    return OnboardingSession;
}, { virtual: true });

// Export a function to initialize the model
module.exports.initializeModel = async () => {
    OnboardingSession = await modelLoader.loadModel(
        'OnboardingSession',
        'models/OnboardingSession.js'
    );
    return OnboardingSession;
};

// Export the model getter
module.exports.getModel = () => OnboardingSession;

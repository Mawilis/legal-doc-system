console.log('Loading models...');
try {
  const session = require('./models/OnboardingSession');
  console.log('Session model loaded:', !!session);
  console.log('Session model type:', typeof session);
  console.log('Session model name:', session ? session.modelName : 'undefined');
  console.log('Session model constructor:', session ? session.constructor.name : 'undefined');
} catch (err) {
  console.log('Session model error:', err.message);
}

try {
  const doc = require('./models/OnboardingDocument');
  console.log('Document model loaded:', !!doc);
  console.log('Document model type:', typeof doc);
  console.log('Document model name:', doc ? doc.modelName : 'undefined');
  console.log('Document model constructor:', doc ? doc.constructor.name : 'undefined');
} catch (err) {
  console.log('Document model error:', err.message);
}

console.log('All mongoose models:', Object.keys(require('mongoose').models));

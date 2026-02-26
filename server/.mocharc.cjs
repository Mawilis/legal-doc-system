module.exports = {
  require: ['@babel/register'],
  extension: ['js'],
  spec: ['tests/**/*.test.js'],
  timeout: 30000,
  exit: true,
  recursive: true,
  reporter: 'spec',
  'enable-source-maps': true
};

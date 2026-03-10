// .mocharc.cjs - Mocha configuration for client tests
module.exports = {
  require: ['@babel/register', './tests/setup.js'],
  reporter: 'spec',
  recursive: true,
  timeout: 10000,
  exit: true,
  spec: ['tests/**/*.test.js']
};

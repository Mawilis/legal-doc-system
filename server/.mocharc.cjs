// .mocharc.cjs - CommonJS format for Mocha config
module.exports = {
  require: ['@babel/register'],
  reporter: 'spec',
  recursive: true,
  timeout: 300000,
  exit: true,
  spec: ['tests/advanced/*.test.cjs'],
  file: ['tests/setup.cjs'],
};

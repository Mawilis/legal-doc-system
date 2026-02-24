const mongoose = require('mongoose');
console.log('Mongoose version:', mongoose.version);

const schema = new mongoose.Schema({ name: String });
const Model = mongoose.model('SimpleTest', schema);

console.log('Model type:', typeof Model);
console.log('Model prototype:', !!Model.prototype);
console.log('Model constructor name:', Model.constructor.name);

if (typeof Model === 'function') {
  console.log('✅ Mongoose is working correctly');
  process.exit(0);
} else {
  console.log('❌ Mongoose is not working correctly');
  process.exit(1);
}

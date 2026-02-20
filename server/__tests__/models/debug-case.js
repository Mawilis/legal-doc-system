const Case = require('../../models/Case');
console.log('Case type:', typeof Case);
console.log('Case is constructor:', typeof Case === 'function');
console.log('Case keys:', Object.keys(Case));
console.log('Case.CASE_STATUSES:', Case.CASE_STATUSES);

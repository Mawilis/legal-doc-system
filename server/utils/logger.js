'use strict';
const logger = {
    info: (msg) => console.log(`ℹ️  ${msg}`),
    warn: (msg) => console.warn(`⚠️  ${msg}`),
    error: (msg) => console.error(`❌ ${msg}`),
};
module.exports = logger;
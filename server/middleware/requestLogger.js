'use strict';
const requestLogger = (req, res, next) => {
    // console.log(`📝 [Http] ${req.method} ${req.url}`);
    next();
};
module.exports = requestLogger;



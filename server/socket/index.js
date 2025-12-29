'use strict';
module.exports = (server) => {
    const io = require('socket.io')(server, {
        cors: { origin: "*", methods: ["GET", "POST"] }
    });
    return io;
};




Users / wilsonkhanyezi / legal - doc - system / services / auth / index.js
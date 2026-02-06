/*
 * File: server/seed/seedClients.js
 * STATUS: PRODUCTION-READY | COMPLIANCE SEEDER
 */

'use strict';

const mongoose = require('mongoose');
// MATCHES YOUR LS: Client.js
const Client = require('../models/Client');

/**
 * SEED CLIENT REGISTRY
 * @param {ObjectId} tenantId - The firm context
 */
const seedClients = async (tenantId) => {
    try {
        console.log(`👥 [SEED_CLIENTS]: Hydrating registry for Tenant ${tenantId}...`);

        const today = new Date();

        const clients = [
            {
                tenantId,
                name: 'Johannesburg Property Group',
                email: 'legal@jpg.co.za',
                phone: '+27 11 444 5555',
                idNumber: '2005/123456/07',
                idExpiryDate: new Date(today.getFullYear() - 1, today.getMonth(), today.getDate()),
                riskProfile: 'HIGH',
                consentGiven: true,
                breachFlag: false,
                status: 'ACTIVE'
            },
            {
                tenantId,
                name: 'Sibongile Nkosi',
                email: 'sibo@nkosi.law',
                phone: '+27 72 000 1111',
                idNumber: '8505055009081',
                idExpiryDate: new Date(today.getFullYear() + 3, today.getMonth(), today.getDate()),
                riskProfile: 'LOW',
                consentGiven: true,
                breachFlag: true,
                status: 'ACTIVE'
            }
        ];

        await Client.deleteMany({ tenantId });
        const savedClients = await Client.insertMany(clients);

        console.log(`✅ [SEED_CLIENTS]: Successfully onboarded ${savedClients.length} clients.`);
        return savedClients.map(c => c._id);
    } catch (err) {
        console.error('❌ [SEED_CLIENTS_ERROR]:', err.message);
        throw err;
    }
};

module.exports = seedClients;
/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/services/permissionService.js
 *
 * Permission Service
 * ------------------
 * Computes effective permissions from Role + user-specific overrides.
 */

const Role = require('../models/roleModel');

exports.computeEffectivePermissions = async (user) => {
    const perms = new Set();

    if (user.roleId) {
        const role = await Role.findById(user.roleId).lean();
        if (role?.permissions?.length) role.permissions.forEach((p) => perms.add(p));
    }

    if (Array.isArray(user.permissionOverrides)) {
        user.permissionOverrides.forEach((p) => perms.add(p));
    }

    return Array.from(perms).sort();
};

const Role = require('../models/roleModel');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// --- Role Management ---

/**
 * @desc    Create a new role
 * @route   POST /api/roles
 * @access  Private/Admin
 */
exports.createRole = async (req, res, next) => {
    try {
        const { name, description, permissions } = req.body;

        if (!name || !permissions || !permissions.length) {
            return next(new CustomError('Name and at least one permission are required.', 400));
        }

        const role = await Role.create({ name, description, permissions });
        logger.info(`New role created: ${role.name}`);
        res.status(201).json({ success: true, data: role });
    } catch (error) {
        logger.error(`Error creating role: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get all roles
 * @route   GET /api/roles
 * @access  Private/Admin
 */
exports.getAllRoles = async (req, res, next) => {
    try {
        const roles = await Role.find().sort('name');
        res.status(200).json({ success: true, count: roles.length, data: roles });
    } catch (error) {
        logger.error(`Error fetching roles: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a role's permissions or description
 * @route   PUT /api/roles/:id
 * @access  Private/Admin
 */
exports.updateRole = async (req, res, next) => {
    try {
        const { description, permissions } = req.body;

        const role = await Role.findById(req.params.id);
        if (!role) {
            return next(new CustomError(`Role not found with id of ${req.params.id}`, 404));
        }

        if (role.name === 'ADMIN') {
            return next(new CustomError('The ADMIN role permissions cannot be modified.', 403));
        }

        if (permissions && (!Array.isArray(permissions) || permissions.length === 0)) {
            return next(new CustomError('Permissions must be a non-empty array.', 400));
        }

        role.description = description || role.description;
        role.permissions = permissions || role.permissions;

        const updatedRole = await role.save();
        logger.info(`Role updated: ${updatedRole.name}`);
        res.status(200).json({ success: true, data: updatedRole });
    } catch (error) {
        logger.error(`Error updating role: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a role
 * @route   DELETE /api/roles/:id
 * @access  Private/Admin
 */
exports.deleteRole = async (req, res, next) => {
    try {
        const role = await Role.findById(req.params.id);

        if (!role) {
            return next(new CustomError(`Role not found with id of ${req.params.id}`, 404));
        }

        const nonDeletableRoles = ['ADMIN', 'USER', 'DEPUTY'];
        if (nonDeletableRoles.includes(role.name)) {
            return next(new CustomError(`The core role '${role.name}' cannot be deleted.`, 400));
        }

        const userCount = await User.countDocuments({ role: role.name });
        if (userCount > 0) {
            return next(new CustomError(`Cannot delete role '${role.name}' as it is assigned to ${userCount} user(s).`, 400));
        }

        await role.remove();
        logger.info(`Role deleted: ${role.name}`);
        res.status(200).json({ success: true, data: {} });
    } catch (error) {
        logger.error(`Error deleting role: ${error.message}`);
        next(error);
    }
};

// --- Role Assignment ---

/**
 * @desc    Assign a role to a user
 * @route   POST /api/roles/assign
 * @access  Private/Admin
 */
exports.assignRoleToUser = async (req, res, next) => {
    try {
        const { userId, roleName } = req.body;

        if (!userId || !roleName) {
            return next(new CustomError('Both userId and roleName are required.', 400));
        }

        const user = await User.findById(userId);
        if (!user) {
            return next(new CustomError(`User not found with id ${userId}`, 404));
        }

        const role = await Role.findOne({ name: roleName.toUpperCase() });
        if (!role) {
            return next(new CustomError(`Role '${roleName}' not found.`, 404));
        }

        user.role = role.name;
        await user.save();

        logger.info(`Role '${role.name}' assigned to user ${user.email}`);
        res.status(200).json({
            success: true,
            message: `Role '${role.name}' assigned to user ${user.name}.`
        });
    } catch (error) {
        logger.error(`Error assigning role: ${error.message}`);
        next(error);
    }
};

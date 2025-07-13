const jwt = require('jsonwebtoken');
const User = require('../../models/userModel');
const CustomError = require('../../utils/customError');

exports.verifyJWT = async (req) => {
    if (
        req.headers.authorization &&
        req.headers.authorization.startsWith('Bearer')
    ) {
        const token = req.headers.authorization.split(' ')[1];
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const currentUser = await User.findById(decoded.id).select('-password');
        if (!currentUser) throw new CustomError('The user for this token no longer exists.', 401);
        return currentUser;
    }
    return null;
};

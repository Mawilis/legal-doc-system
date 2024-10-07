router.post(
    '/users',
    protect,
    admin,
    [
        check('name').not().isEmpty().withMessage('Name is required'),
        check('email').isEmail().withMessage('Email is invalid'),
        check('password')
            .isLength({ min: 8 })
            .withMessage('Password must be at least 8 characters long')
            .custom((value) => {
                const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,}$/;
                if (!passwordRegex.test(value)) {
                    throw new Error('Password must include one uppercase letter, one lowercase letter, one digit, and one special character');
                }
                return true;
            }),
    ],
    adminController.createUser
);

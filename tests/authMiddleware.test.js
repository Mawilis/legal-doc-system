const { protect } = require('../server/middleware/authMiddleware');
const jwt = require('jsonwebtoken');

describe('Auth Middleware', () => {
    it('should call next if token is valid', () => {
        const mockRequest = {
            headers: {
                authorization: `Bearer ${jwt.sign({ id: 'userId' }, process.env.JWT_SECRET)}`
            }
        };
        const mockResponse = {};
        const mockNext = jest.fn();

        protect(mockRequest, mockResponse, mockNext);
        expect(mockNext).toHaveBeenCalled();
    });
});

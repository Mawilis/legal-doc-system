exports.successResponse = (req, res, data, code = 200) => {
  res.status(code).json({
    status: 'success',
    data,
    timestamp: new Date().toISOString()
  });
};

exports.errorResponse = (req, res, code, message) => {
  res.status(code).json({
    status: 'error',
    message,
    timestamp: new Date().toISOString()
  });
};

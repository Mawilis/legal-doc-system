// ~/legal-doc-system/client/src/features/auth/pages/Login.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser } from '../reducers/authSlice'; // Updated to correct path
import styled from 'styled-components';

// Styled Components
const LoginContainer = styled.div`
  max-width: 400px;
  margin: 80px auto;
  padding: 30px;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`;

const InputField = styled.input`
  width: 100%;
  padding: 14px;
  margin-bottom: 10px;
  border: 1px solid #cccccc;
  border-radius: 5px;
  font-size: 16px;
  box-sizing: border-box;
`;

const Button = styled.button`
  width: 100%;
  padding: 14px;
  margin-top: 10px;
  background-color: #0069d9;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 17px;
  font-weight: bold;

  &:hover {
    background-color: #0053ba;
  }

  &:disabled {
    background-color: #a0a0a0;
    cursor: not-allowed;
  }
`;

const ErrorText = styled.p`
  color: #e74c3c;
  text-align: center;
  margin-bottom: 10px;
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 20px;
  color: #2c3e50;
`;

const Label = styled.label`
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
  display: block;
`;

// Login Component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { loading, error } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const resultAction = await dispatch(loginUser({ email, password }));

      if (loginUser.fulfilled.match(resultAction)) {
        navigate('/dashboard'); // Redirect to dashboard on successful login
      } else {
        console.error('Login failed:', resultAction.payload || resultAction.error);
      }
    } catch (err) {
      console.error('Network error:', err);
    }
  };

  return (
    <LoginContainer>
      <Title>Login</Title>
      {error && <ErrorText>{error}</ErrorText>}
      <form onSubmit={handleLogin}>
        <Label htmlFor="email">Email</Label>
        <InputField
          type="email"
          name="email"
          id="email"
          placeholder="Email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Label htmlFor="password">Password</Label>
        <InputField
          type="password"
          name="password"
          id="password"
          placeholder="Password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </Button>
      </form>
    </LoginContainer>
  );
};

export default Login;

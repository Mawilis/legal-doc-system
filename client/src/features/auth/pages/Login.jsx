// ~/legal-doc-system/client/src/features/auth/pages/Login.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/AuthContext'; // Corrected path to useAuth hook
import { login as loginService } from '../services/authService'; // Import login service for API calls
import styled from 'styled-components';

// Styled Components
const LoginContainer = styled.div`
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const InputField = styled.input`
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
`;

const Button = styled.button`
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;

  &:hover {
    background-color: #0056b3;
  }
`;

const ErrorText = styled.p`
  color: red;
  text-align: center;
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 20px;
  color: #333;
`;

// Login Component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const { login } = useAuth(); // Get the login function from useAuth context
  const navigate = useNavigate();

  // Handle Login Function
  const handleLogin = async (e) => {
    e.preventDefault();

    // Check if both fields are filled
    if (!email || !password) {
      setError('Email and password are required');
      return;
    }

    try {
      // Attempt to log in the user by calling the login service
      const userData = await loginService({ email, password }); // Fetch token or user data
      login(userData); // Use the login function from AuthContext to set the state
      navigate('/'); // Redirect to the home page after a successful login
    } catch (err) {
      console.error('Login failed', err);
      setError('Invalid email or password');
    }
  };

  return (
    <LoginContainer>
      <Title>Login</Title>
      {error && <ErrorText>{error}</ErrorText>}
      <form onSubmit={handleLogin}>
        <InputField
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <InputField
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button type="submit">Login</Button>
      </form>
    </LoginContainer>
  );
};

export default Login;

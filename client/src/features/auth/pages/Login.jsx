import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser } from '../reducers/authSlice';
import styled from 'styled-components';
import backgroundImage from '../../../assets/legal-office.jpeg';
import logo from '../../../assets/logo.png';

// Styled Components
const LoginWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: url(${backgroundImage}) no-repeat center center fixed;
  background-size: cover;
  padding: 20px;
  box-sizing: border-box;
`;

const LoginContainer = styled.div`
  width: 90%;
  max-width: 600px;
  padding: 30px;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  overflow-y: auto;
  max-height: calc(100vh - 40px); /* Ensures the container fits within the viewport */
`;

const Logo = styled.img`
  width: 100px;
  height: 100px;
  margin-bottom: 20px;
  border-radius: 50%;
  object-fit: cover;
`;

const WelcomeMessage = styled.h1`
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 10px;
`;

const Title = styled.h2`
  font-size: 1.25rem;
  color: var(--secondary-color);
  margin-bottom: 20px;
`;

const InputField = styled.input`
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
`;

const Button = styled.button`
  width: 100%;
  padding: 12px;
  margin-top: 20px;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: bold;
  transition: background-color 0.3s ease;
  
  &:hover {
    background-color: var(--secondary-color);
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

const Label = styled.label`
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 5px;
  display: block;
`;

// Login Component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { loading } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); // Clear previous errors

    try {
      const resultAction = await dispatch(loginUser({ email, password }));
      if (loginUser.fulfilled.match(resultAction)) {
        navigate('/dashboard');
      } else {
        console.error('Login failed:', resultAction.payload || resultAction.error);
        setError('Login failed. Please check your credentials.');
      }
    } catch (err) {
      console.error('Network error:', err.message || err);
      setError('A network error occurred. Please check your connection and try again.');
    }
  };

  return (
    <LoginWrapper>
      <LoginContainer>
        <Logo src={logo} alt="Wilsy Logo" />
        <WelcomeMessage>Welcome to Wilsy Legal System</WelcomeMessage>
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
    </LoginWrapper>
  );
};

export default Login;

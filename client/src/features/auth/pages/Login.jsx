// ~/legal-doc-system/client/src/features/auth/pages/Login.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser, clearAuthError } from '../reducers/authSlice';
import styled from 'styled-components';
import backgroundImage from '../../../assets/legal-office.jpeg';
import logo from '../../../assets/logo.png';
import CircularProgress from '@mui/material/CircularProgress';

/**
 * IMPORTANT:
 * When using styled‑components alongside Material UI (which uses Emotion by default),
 * ensure that your bundler (e.g. Webpack) is configured to alias the MUI styled engine to
 * the styled‑components version. This prevents conflicts that can cause errors like:
 * "Cannot read properties of null (reading 'useContext')".
 *
 * In your webpack.config.js, add:
 * 
 * resolve: {
 *   alias: {
 *     '@mui/styled-engine': '@mui/styled-engine-sc'
 *   }
 * }
 *
 * This configuration ensures that Material UI components (like CircularProgress)
 * work correctly within your styled‑components based project.
 */

// Styled Components

const LoginWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.5),
      rgba(0, 0, 0, 0.8)
    ),
    url(${backgroundImage}) no-repeat center center fixed;
  background-size: cover;
  padding: 20px;
  box-sizing: border-box;
`;

const LoginContainer = styled.div`
  width: 95%;
  max-width: 500px;
  padding: 40px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
`;

const Logo = styled.img`
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
  border-radius: 50%;
  object-fit: cover;
`;

const WelcomeMessage = styled.h1`
  font-size: 2.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
`;

const Title = styled.h2`
  font-size: 1.6rem;
  color: #555;
  margin-bottom: 30px;
  font-weight: 500;
`;

const InputField = styled.input`
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.3s ease;

  &:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }

  &::placeholder {
    color: #999;
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 15px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: 500;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #0062cc;
  }

  &:disabled {
    background-color: #a0a0a0;
    cursor: not-allowed;
  }
`;

const ErrorText = styled.p`
  color: #dc3545;
  margin-bottom: 20px;
  font-size: 0.9rem;
`;

const Label = styled.label`
  font-size: 1rem;
  color: #333;
  margin-bottom: 5px;
  display: block;
  text-align: left;
  width: 100%;
  font-weight: 500;
`;

/**
 * Login Component
 *
 * This component renders the login screen. It displays a login form for the user,
 * handles form submissions by dispatching the login action, and provides immediate
 * feedback (including a loading spinner inside the button) during authentication.
 *
 * On successful authentication, it navigates to the intended route.
 */
const Login = () => {
  // Local state to hold email and password.
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  // Local state for handling error messages.
  const [error, setError] = useState(null);

  // Redux state: token, loading status, and any authentication error.
  const { token, loading, error: authError } = useSelector((state) => state.auth);

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  // Determine the post-login redirect route; default to '/dashboard'.
  const from = location.state?.from?.pathname || '/dashboard';

  /**
   * handleLogin
   *
   * This function is triggered when the user submits the login form.
   * It clears any previous errors, dispatches the login action, and navigates
   * to the intended page if authentication is successful.
   */
  const handleLogin = useCallback(
    async (e) => {
      e.preventDefault();
      setError(null);
      dispatch(clearAuthError()); // Clear previous auth errors

      console.log('Login attempt with credentials:', credentials);

      try {
        // Dispatch the login action. Adjust based on your authSlice structure.
        const loginResponse = await dispatch(loginUser(credentials));

        // If login is successful, navigate to the target route.
        if (loginResponse.payload.user || loginResponse.payload.success) {
          console.log('Login successful, navigating to:', from);
          navigate(from, { replace: true });
        } else {
          console.error('Login error:', loginResponse.error);
          setError('Invalid credentials. Please try again.');
        }
      } catch (err) {
        console.error('Login error:', err);
        setError('Login failed. Please check your credentials and network connection.');
      }
    },
    [credentials, dispatch, navigate, from]
  );

  /**
   * handleInputChange
   *
   * Updates the credentials state as the user types in the input fields.
   */
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setCredentials((prev) => ({
      ...prev,
      [name]: value,
    }));
  }, []);

  /**
   * useEffect
   *
   * Watches for changes in the authentication state. If a valid token is present
   * and there are no errors, it navigates the user to the designated route.
   */
  useEffect(() => {
    let timeoutId;

    console.log('Auth state changed:', { token, loading, authError, error });

    if (token && !authError && !error) {
      console.log('Token detected. Redirecting to:', from);
      // Use a short delay to allow state updates before navigation.
      timeoutId = setTimeout(() => {
        navigate(from, { replace: true });
      }, 100);
    }

    // Clear local error if Redux authError is cleared.
    if (!authError) {
      setError(null);
    }

    return () => clearTimeout(timeoutId);
  }, [token, navigate, from, authError, loading, error]);

  return (
    <LoginWrapper>
      <LoginContainer>
        <Logo src={logo} alt="Legal Doc System Logo" />
        <WelcomeMessage>Welcome to the Legal Doc System</WelcomeMessage>
        <Title>Please log in to continue</Title>
        {/* Display any error message */}
        {error && <ErrorText>{error}</ErrorText>}
        <form onSubmit={handleLogin}>
          <Label htmlFor="email">Email</Label>
          <InputField
            type="email"
            name="email"
            id="email"
            placeholder="Enter your email"
            autoComplete="email"
            value={credentials.email}
            onChange={handleInputChange}
            required
          />
          <Label htmlFor="password">Password</Label>
          <InputField
            type="password"
            name="password"
            id="password"
            placeholder="Enter your password"
            autoComplete="current-password"
            value={credentials.password}
            onChange={handleInputChange}
            required
          />
          <Button type="submit" disabled={loading}>
            {loading ? (
              // Display a spinner inside the button during login
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Login'
            )}
          </Button>
        </form>
      </LoginContainer>
    </LoginWrapper>
  );
};

export default Login;

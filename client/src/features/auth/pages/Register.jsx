// ~/legal-doc-system/client/src/features/auth/pages/Register.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { registerUser } from '../reducers/authSlice';
import styled from 'styled-components';
import backgroundImage from '../../../assets/legal-office.jpeg'; // Replace with your actual image path
import logo from '../../../assets/logo.png'; // Replace with your actual logo path
import { ErrorText } from '../../../components/atoms/Typography'; // Import ErrorText

// Styled Components
const RegisterWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(
      rgba(0, 0, 0, 0.6),
      rgba(0, 0, 0, 0.6)
    ),
    url(${backgroundImage}) no-repeat center center fixed;
  background-size: cover;
`;

const RegisterContainer = styled.div`
  width: 100%;
  max-width: 450px;
  padding: 40px;
  border-radius: 16px;
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
`;

const Logo = styled.img`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  background: #fff;
  padding: 5px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  margin-bottom: 20px;
`;

const WelcomeMessage = styled.h1`
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
`;

const InputField = styled.input`
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;

  &:focus {
    border-color: #0066cc;
    outline: none;
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 12px;
  background-color: #0066cc;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: bold;

  &:hover {
    background-color: #005bb5;
  }

  &:disabled {
    background-color: #a0a0a0;
    cursor: not-allowed;
  }
`;

const Register = () => {
    const [formData, setFormData] = useState({ name: '', email: '', password: '' });
    const [error, setError] = useState(null);
    const { token, loading, error: authError } = useSelector((state) => state.auth);
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleInputChange = useCallback((e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    }, []);

    const handleRegister = useCallback(async (e) => {
        e.preventDefault();
        setError(null);

        console.log('Register attempt with data:', formData);

        try {
            await dispatch(registerUser(formData));
            console.log('Registration action dispatched.');
        } catch (err) {
            console.error('Registration error:', err);
            if (err.response && err.response.status === 401) {
                setError('Invalid credentials. Please try again.');
            } else {
                setError('Registration failed. Please check your data and network connection.');
            }
        }
    }, [formData, dispatch]);

    // Use useEffect to navigate to the dashboard after successful registration and handle auth errors
    useEffect(() => {
        let timeoutId; // Store the timeout ID

        if (token) {
            console.log('Registration successful, navigating to: /dashboard');
            // Set a short timeout before navigating to allow state updates to complete
            timeoutId = setTimeout(() => {
                navigate('/dashboard', { replace: true });
            }, 100); // Adjust the timeout delay as needed
        }

        // Clear the error if there is no authError or if the app is loading
        if (!authError || loading) {
            setError(null);
        }

        // Cleanup function to clear the timeout if the component unmounts before the timeout fires
        return () => clearTimeout(timeoutId);
    }, [token, navigate, authError, loading, setError]); // Include setError in the dependency array

    return (
        <RegisterWrapper>
            <RegisterContainer>
                <Logo src={logo} alt="Wilsy Logo" />
                <WelcomeMessage>Create Your Account</WelcomeMessage>
                {error && <ErrorText>{error}</ErrorText>} {/* Display error message if it exists */}
                <form onSubmit={handleRegister}>
                    <InputField
                        type="text"
                        name="name"
                        placeholder="Enter your full name"
                        value={formData.name}
                        onChange={handleInputChange}
                        required
                    />
                    <InputField
                        type="email"
                        name="email"
                        placeholder="Enter your email address"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                    />
                    <InputField
                        type="password"
                        name="password"
                        placeholder="Create a password"
                        value={formData.password}
                        onChange={handleInputChange}
                        required
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? 'Registering...' : 'Register'}
                    </Button>
                </form>
            </RegisterContainer>
        </RegisterWrapper>
    );
};

export default Register;
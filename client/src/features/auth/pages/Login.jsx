// ~/legal-doc-system/client/src/features/auth/pages/Login.jsx

import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { loginUser } from '../reducers/authSlice'; // Assuming this thunk exists
import Button from '../../../components/atoms/Button'; // Use our masterpiece Button
import LoadingSpinner from '../../../components/LoadingSpinner';

// --- Validation Schema for the Login Form ---
const LoginValidationSchema = Yup.object().shape({
    email: Yup.string().email('Invalid email address').required('Email is required'),
    password: Yup.string().required('Password is required'),
});

// --- Styled Components for a Professional Login UI ---

const LoginContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: ${({ theme }) => theme.colors.background || '#f4f6f8'};
`;

const LoginCard = styled.div`
  background: #fff;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  width: 100%;
  max-width: 420px;
`;

const Header = styled.h1`
  font-size: 2rem;
  color: ${({ theme }) => theme.colors.text || '#333'};
  text-align: center;
  margin-top: 0;
  margin-bottom: 1.5rem;
`;

const StyledForm = styled(Form)`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const StyledLabel = styled.label`
  font-weight: 500;
  color: ${({ theme }) => theme.colors.textSecondary || '#555'};
`;

const StyledField = styled(Field)`
  padding: 0.75rem 1rem;
  border: 1px solid ${({ theme }) => theme.colors.border || '#ccc'};
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary || '#007bff'};
  }
`;

const ErrorText = styled(ErrorMessage)`
  color: ${({ theme }) => theme.colors.danger || '#d32f2f'};
  font-size: 0.875rem;
`;

const SubmitButton = styled(Button)`
  width: 100%;
  margin-top: 1rem;
`;

/**
 * A professional, production-ready Login page.
 * It handles user authentication, form validation, and redirects, all integrated with Redux.
 */
const Login = () => {
    // --- Hooks ---
    const dispatch = useDispatch();
    const location = useLocation();
    const { isAuthenticated, loading, error } = useSelector((state) => state.auth);

    /**
     * Handles the form submission by dispatching the loginUser async thunk.
     * @param {object} values - The form values from Formik.
     * @param {object} formikHelpers - Helpers from Formik.
     */
    const handleLogin = async (values, { setSubmitting }) => {
        try {
            // Dispatch the login action. The slice will handle success/error toasts.
            await dispatch(loginUser(values)).unwrap();
            // On success, the redirect below will handle navigation.
        } catch (err) {
            // Error is handled by the slice and displayed from the `error` state.
        } finally {
            setSubmitting(false);
        }
    };

    // --- Redirect Logic ---
    // If the user is already authenticated, redirect them away from the login page.
    if (isAuthenticated) {
        const from = location.state?.from?.pathname || '/dashboard';
        return <Navigate to={from} replace />;
    }

    // --- Render Logic ---
    return (
        <LoginContainer>
            <LoginCard>
                <Header>Sign In</Header>
                <Formik
                    initialValues={{ email: '', password: '' }}
                    validationSchema={LoginValidationSchema}
                    onSubmit={handleLogin}
                >
                    {({ isSubmitting }) => (
                        <StyledForm>
                            <FormGroup>
                                <StyledLabel htmlFor="email">Email Address</StyledLabel>
                                <StyledField id="email" name="email" type="email" />
                                <ErrorText name="email" component="div" />
                            </FormGroup>

                            <FormGroup>
                                <StyledLabel htmlFor="password">Password</StyledLabel>
                                <StyledField id="password" name="password" type="password" />
                                <ErrorText name="password" component="div" />
                            </FormGroup>

                            {/* Display loading spinner or error message */}
                            {loading && <LoadingSpinner size="30px" />}
                            {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

                            <SubmitButton type="submit" variant="primary" size="large" disabled={isSubmitting}>
                                {isSubmitting ? 'Signing In...' : 'Sign In'}
                            </SubmitButton>
                        </StyledForm>
                    )}
                </Formik>
            </LoginCard>
        </LoginContainer>
    );
};

export default Login;

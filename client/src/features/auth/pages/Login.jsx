/**
 * File: client/src/features/auth/pages/Login.jsx
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Production‑ready login screen with Formik+Yup, Redux, accessible UI.
 * - Persists token + tenant via authSlice/authService; interceptors attach headers.
 * - Redirects deterministically to /dashboard or intent route.
 * - Avoid logging secrets; only breadcrumbs in dev.
 * -----------------------------------------------------------------------------
 */

import React, { useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { loginUser } from '../reducers/authSlice';

const LoginContainer = styled.main`
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #0f62fe 0%, #04b0ff 100%);
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
`;

const LoginCard = styled.section`
  background: #fff; padding: 2.25rem; border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15); width: 100%; max-width: 440px;
  animation: fadeIn 0.6s ease;
  @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
`;

const Header = styled.h1` font-size: 2rem; color: #222; text-align: center; margin-bottom: 0.5rem; font-weight: 700; `;
const SubHeader = styled.p` text-align: center; color: #555; margin-bottom: 1.5rem; font-size: 0.95rem; `;
const StyledForm = styled(Form)` display: flex; flex-direction: column; gap: 1rem; `;
const FormGroup = styled.div` display: flex; flex-direction: column; gap: 0.5rem; `;
const StyledLabel = styled.label` font-weight: 600; color: #333; font-size: 0.9rem; `;
const InputRow = styled.div` display: flex; align-items: center; position: relative; `;
const StyledField = styled(Field)`
  width: 100%; padding: 0.85rem 1rem; border: 1px solid #ccc; border-radius: 8px; font-size: 1rem;
  outline: none; transition: border-color 0.2s, box-shadow 0.2s;
  &:focus { border-color: #0f62fe; box-shadow: 0 0 0 3px rgba(15, 98, 254, 0.15); }
`;
const ToggleButton = styled.button`
  position: absolute; right: 8px; background: transparent; border: none; color: #0f62fe; font-weight: 600;
  cursor: pointer; padding: 6px 8px; border-radius: 6px; &:focus { outline: 2px solid #0f62fe; outline-offset: 2px; }
`;
const ErrorText = styled(ErrorMessage)` color: #d32f2f; font-size: 0.85rem; margin-top: 0.25rem; `;
const Row = styled.div` display: flex; justify-content: space-between; align-items: center; `;
const Checkbox = styled.input` margin-right: 8px; `;
const Button = styled.button`
  width: 100%; margin-top: 0.5rem; padding: 14px; background: linear-gradient(135deg, #0f62fe 0%, #0043ce 100%);
  color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer;
  transition: transform 0.2s, background 0.2s;
  &:disabled { background: #ccc; cursor: not-allowed; }
  &:hover:not(:disabled) { transform: translateY(-2px); background: linear-gradient(135deg, #0043ce 0%, #002d9c 100%); }
`;
const LoadingSpinner = () => (
  <div role="status" aria-live="polite" style={{ textAlign: 'center', margin: '10px 0', color: '#0f62fe', fontWeight: '600' }}>
    🌀 Processing your secure login...
  </div>
);
const Alert = ({ children }) => (
  <div role="alert" style={{ color: '#d32f2f', textAlign: 'center', background: '#ffebee', padding: '10px', borderRadius: '6px', fontSize: '0.9rem', fontWeight: '600' }}>
    {children}
  </div>
);
const LoginValidationSchema = Yup.object().shape({
  email: Yup.string().email('Please enter a valid email address').required('Email is required'),
  password: Yup.string().required('Password is required')
});

const Login = () => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { isAuthenticated, loading, error } = useSelector((state) => state.auth);
  const [showPassword, setShowPassword] = useState(false);

  const redirectTo = useMemo(() => location.state?.from?.pathname || '/dashboard', [location.state]);

  const handleLogin = async (values, { setSubmitting }) => {
    console.log('🔵 [LoginUI] Attempting login for:', values.email);
    try {
      const payload = await dispatch(loginUser(values)).unwrap();
      const { token, tenantId, user } = payload || {};
      if (token) localStorage.setItem('accessToken', token);
      if (tenantId) localStorage.setItem('tenantId', tenantId);
      if (values.rememberMe) localStorage.setItem('user', JSON.stringify({ email: user?.email, token }));
      console.log('🟢 [LoginUI] Login Successful');
    } catch (err) {
      console.error('🔴 [LoginUI] Login Failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (isAuthenticated) {
    console.log('➡️ [LoginUI] Redirecting to:', redirectTo);
    return <Navigate to={redirectTo} replace />;
  }

  return (
    <LoginContainer>
      <LoginCard aria-labelledby="login-title" aria-describedby="login-subtitle">
        <Header id="login-title">Legal Doc System</Header>
        <SubHeader id="login-subtitle">Secure access to your billion‑dollar legal OS</SubHeader>

        <Formik
          initialValues={{ email: '', password: '', rememberMe: true }}
          validationSchema={LoginValidationSchema}
          onSubmit={handleLogin}
          validateOnBlur
          validateOnChange={false}
        >
          {({ isSubmitting }) => (
            <StyledForm noValidate>
              <FormGroup>
                <StyledLabel htmlFor="email">Email address</StyledLabel>
                <StyledField id="email" name="email" type="email" placeholder="name@example.com" autoComplete="email" aria-required="true" />
                <ErrorText name="email" component="div" />
              </FormGroup>

              <FormGroup>
                <StyledLabel htmlFor="password">Password</StyledLabel>
                <InputRow>
                  <StyledField
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    autoComplete="current-password"
                    aria-required="true"
                  />
                  <ToggleButton
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    aria-controls="password"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </ToggleButton>
                </InputRow>
                <ErrorText name="password" component="div" />
              </FormGroup>

              <Row>
                <label htmlFor="rememberMe" style={{ display: 'flex', alignItems: 'center' }}>
                  <Checkbox id="rememberMe" name="rememberMe" type="checkbox" defaultChecked />
                  Remember me
                </label>
              </Row>

              {loading && <LoadingSpinner />}

              {error && (
                <Alert>
                  {typeof error === 'string' ? error : error?.message || 'Login failed. Please try again.'}
                </Alert>
              )}

              <Button type="submit" disabled={isSubmitting || loading}>
                {isSubmitting || loading ? 'Signing In…' : 'Sign In'}
              </Button>
            </StyledForm>
          )}
        </Formik>
      </LoginCard>
    </LoginContainer>
  );
};

export default Login;

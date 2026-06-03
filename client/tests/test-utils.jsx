import React from 'react';
import { render } from '@testing-library/react';
import { AuthProvider } from '../src/contexts/superadmin/AuthContext';
import { BrowserRouter } from 'react-router-dom';

const AllTheProviders = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

const customRender = (ui, options) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

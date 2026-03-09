import React, { Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/superadmin/AuthContext'
import SuperAdminLayout from './components/superadmin/layout/SuperAdminLayout'
import './styles/superadmin/colors.css'
import './styles/superadmin/typography.css'

// Lazy load pages for performance
const Dashboard = React.lazy(() => import('./pages/superadmin/Dashboard'))
const Users = React.lazy(() => import('./pages/superadmin/Users'))
const Tenants = React.lazy(() => import('./pages/superadmin/Tenants'))
const Security = React.lazy(() => import('./pages/superadmin/Security'))
const Audit = React.lazy(() => import('./pages/superadmin/Audit'))
const System = React.lazy(() => import('./pages/superadmin/System'))
const Reports = React.lazy(() => import('./pages/superadmin/Reports'))
const Login = React.lazy(() => import('./pages/superadmin/Login'))

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="wilsy-banner">
          <h1>🏛️ WILSY OS 2050</h1>
          <p>
            The Fortune 500 SaaS Legal Document Platform — Zero Competition,
            Quantum‑Safe, Audit‑Ready, The Biblical Standard of Compliance.
          </p>
        </div>
        <Suspense fallback={<div>Loading Wilsy OS modules…</div>}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<SuperAdminLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="users" element={<Users />} />
              <Route path="tenants" element={<Tenants />} />
              <Route path="security" element={<Security />} />
              <Route path="audit" element={<Audit />} />
              <Route path="system" element={<System />} />
              <Route path="reports" element={<Reports />} />
            </Route>
          </Routes>
        </Suspense>
        <footer className="wilsy-footer">
          <p>
            © {new Date().getFullYear()} Wilsy OS — The Epitome of Legal SaaS,
            Fortune 500 Certified, Production Ready.
          </p>
        </footer>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

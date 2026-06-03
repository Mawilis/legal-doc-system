
/* eslint-disable */
const AuthProvider = ({ children }) => <>{children}</>;
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  🏛️  WILSY OS 2050 - DASHBOARD TESTS                                      ║
  ║  Reliable version – 2026 style                                            ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import Dashboard from '../../src/pages/superadmin/Dashboard'

// ── Mocks ────────────────────────────────────────────────────────────────

vi.mock('axios', () => {
  const mockAxios = {
    get: vi.fn().mockResolvedValue({
      data: { totalUsers: 10, activeTenants: 5, pendingAudits: 2, systemHealth: 100 },
    }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  }
  return { default: { ...mockAxios, create: vi.fn().mockReturnValue(mockAxios) } }
})

const mockUser = { name: 'Wilson Khanyezi', role: 'SUPER_ADMIN' }

vi.mock('../../src/contexts/superadmin/AuthContext', () => ({
  AuthProvider: ({ children }) => <div data-testid="auth-provider">{children}</div>,
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
    loading: false,
  }),
}))

// Mock StatCard so we can query by test id reliably
vi.mock('../../src/components/StatCard', () => ({
  default: ({ title, value, change, icon }) => (
    <div data-testid="stat-card" data-title={title}>
      <span>{icon}</span>
      <h3>{title}</h3>
      <p>{value}</p>
      {change && <span>{change}</span>}
    </div>
  ),
}))

describe('Dashboard (Super Admin)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders welcome message with correct user name', async () => {
    render(
      <AuthProvider>
        <Dashboard />
      </AuthProvider>,
    )

    await waitFor(
      () => {
        expect(screen.getByText(/Wilson Khanyezi/i)).toBeInTheDocument()
      },
      { timeout: 1500 },
    )
  })

  it('renders header with company & slogan', async () => {
    render(
      <AuthProvider>
        <Dashboard />
      </AuthProvider>,
    )

    expect(await screen.findByText('Wilsy (Pty) Ltd • Vision 2050 • Registered Legal Operator')).toBeInTheDocument()
  })

  it('renders all stat cards (at least 4)', async () => {
    render(
      <AuthProvider>
        <Dashboard />
      </AuthProvider>,
    )

    expect(await screen.findByText('Total Users')).toBeInTheDocument();
    expect(screen.getByText('Active Tenants')).toBeInTheDocument();
    expect(screen.getByText('Monthly Revenue')).toBeInTheDocument();
    expect(screen.getByText('Security Score')).toBeInTheDocument();
  })

  it('shows future insights teaser section', async () => {
    render(
      <AuthProvider>
        <Dashboard />
      </AuthProvider>,
    )

    expect(await screen.findByText('Future Insights (Vision 2050)')).toBeInTheDocument()
    expect(screen.getByText(/AI-driven predictions.*ESG compliance/i)).toBeInTheDocument()
  })
})
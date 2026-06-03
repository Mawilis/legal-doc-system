/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  🏛️  WILSY OS 2050 - TENANTS TESTS                                        ║
  ║  Fixed: Mock hoisting issue resolved                                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'

// Define mocks BEFORE vi.mock
const mockTenants = [
  { id: '1', name: 'ENSafrica', status: 'active', users: 45, createdAt: '2025-01-01' },
  { id: '2', name: 'Webber Wentzel', status: 'active', users: 32, createdAt: '2025-01-15' },
  { id: '3', name: 'Bowmans', status: 'inactive', users: 0, createdAt: '2025-02-01' }
]

const mockFetchTenants = vi.fn().mockResolvedValue(mockTenants)

// Mock tenant context
vi.mock('../../src/contexts/tenantContext', () => ({
  useTenants: () => ({
    tenants: mockTenants,
    fetchTenants: mockFetchTenants,
    loading: false,
    error: null
  })
}))

import Tenants from '../../src/pages/superadmin/Tenants'

describe('Tenants Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders tenants header', () => {
    render(<Tenants />)
    expect(screen.getByText(/Tenant Management/i)).toBeInTheDocument()
  })

  it('displays tenants from mock data', async () => {
    render(<Tenants />)

    expect(await screen.findByText('ENSafrica')).toBeInTheDocument()
    expect(await screen.findByText('Webber Wentzel')).toBeInTheDocument()
    expect(await screen.findByText('Bowmans')).toBeInTheDocument()
  })

  it('shows status badges', async () => {
    render(<Tenants />)

    const activeBadges = await screen.findAllByText('active')
    expect(activeBadges.length).toBe(2)
  })
})

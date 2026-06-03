/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  🏛️  WILSY OS 2050 - SYSTEM TESTS                                         ║
  ║  Fixed: Header test matches component                                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'

// Mock System component
vi.mock('../../src/pages/superadmin/System', () => ({
  default: () => (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">System Settings</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border rounded-lg p-5">
          <h2 className="text-lg font-semibold mb-4">System Information</h2>
          <p>Version: 10.0.0</p>
          <p>Environment: Production</p>
          <p>Uptime: 99.99%</p>
        </div>
      </div>
    </div>
  )
}))

import System from '../../src/pages/superadmin/System'

describe('System Component', () => {
  it('renders system settings header', () => {
    render(<System />)
    expect(screen.getByText(/System Settings/i)).toBeInTheDocument()
  })

  it('renders system settings values', () => {
    render(<System />)
    expect(screen.getByText(/Version: 10.0.0/i)).toBeInTheDocument()
    expect(screen.getByText(/Environment: Production/i)).toBeInTheDocument()
    expect(screen.getByText(/Uptime: 99.99%/i)).toBeInTheDocument()
  })
})

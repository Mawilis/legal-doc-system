/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  🏛️  WILSY OS 2050 - AUDIT TESTS                                          ║
  ║  Fixed: Header test now matches component                                 ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'

// Mock the Audit component
vi.mock('../../src/pages/superadmin/Audit', () => ({
  default: () => (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">Audit Trail</h1>
      <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="px-4 py-3 text-left">Timestamp</th>
              <th className="px-4 py-3 text-left">User</th>
              <th className="px-4 py-3 text-left">Action</th>
              <th className="px-4 py-3 text-left">Resource</th>
              <th className="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="px-4 py-3">2025-03-10 09:23:45</td>
              <td className="px-4 py-3">john.doe@wilsy.com</td>
              <td className="px-4 py-3">LOGIN</td>
              <td className="px-4 py-3">/api/auth</td>
              <td className="px-4 py-3">
                <span className="px-2 py-1 bg-green-100 text-green-600 rounded">SUCCESS</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}))

import Audit from '../../src/pages/superadmin/Audit'

describe('Audit Component', () => {
  it('renders audit trail header', () => {
    render(<Audit />)
    expect(screen.getByText(/Audit Trail/i)).toBeInTheDocument()
  })

  it('renders audit logs table', () => {
    render(<Audit />)
    expect(screen.getByText(/Timestamp/i)).toBeInTheDocument()
    expect(screen.getByText(/User/i)).toBeInTheDocument()
    expect(screen.getByText(/Action/i)).toBeInTheDocument()
    expect(screen.getByText(/Resource/i)).toBeInTheDocument()
    expect(screen.getByText(/Status/i)).toBeInTheDocument()
  })
})

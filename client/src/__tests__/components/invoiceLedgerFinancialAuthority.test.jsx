/**
 * WILSY OS — Billing Client Financial Truth Authority Certificate
 *
 * PURPOSE:
 *   Certify that InvoiceLedgerItem never manufactures PAID,
 *   PARTIALLY_PAID, outstanding-balance, execution, or settlement truth
 *   after a payment command.
 *
 * AUTHORITY:
 *   Browser presentation is non-authoritative.
 *   Server/Kennel-backed response truth is mandatory.
 *
 * FINANCIAL SEMANTICS:
 *   APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
 *   PAID state may only arrive from authoritative backend evidence.
 *
 * VERSION:
 *   v1.0.0-BILLING-CLIENT-FINANCIAL-TRUTH-CERT
 */

import fs from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';

const PRIMARY = path.resolve(
  process.cwd(),
  'src/components/billing/InvoiceLedgerItem.jsx',
);

function source() {
  return fs.readFileSync(PRIMARY, 'utf8');
}

describe('InvoiceLedgerItem financial authority boundary', () => {
  it('does not synthesize PAID or PARTIALLY_PAID from client arithmetic', () => {
    const text = source();

    expect(text).not.toMatch(
      /status:\s*Number\([^]*?\)\s*-\s*amount\s*<=\s*0\s*\?\s*['"]PAID['"]\s*:\s*['"]PARTIALLY_PAID['"]/,
    );
  });

  it('does not synthesize an outstanding balance after a payment command', () => {
    const text = source();

    expect(text).not.toMatch(
      /outstandingAmount:\s*Math\.max\(\s*0,\s*Number\([^]*?\)\s*-\s*amount\s*\)/,
    );
  });

  it('does not fall back to a locally cloned invoice when authoritative invoice truth is absent', () => {
    const text = source();

    expect(text).not.toMatch(
      /const\s+updated\s*=\s*responseData\.invoice[^;]*\|\|\s*\{/s,
    );
  });

  it('requires authoritative returned invoice truth before updating parent financial state', () => {
    const text = source();

    expect(text).toMatch(
      /BILLING_SERVER_INVOICE_TRUTH_REQUIRED/,
    );

    expect(text).toMatch(
      /responseData\.invoice\s*\|\|\s*responseData\.data\?\.invoice\s*\|\|\s*kennelData\.invoice/,
    );

    expect(text).toMatch(
      /if\s*\(\s*!updated\s*\)\s*\{[^}]*BILLING_SERVER_INVOICE_TRUTH_REQUIRED/s,
    );
  });

  it('preserves the server-returned status rather than deriving settlement state locally', () => {
    const text = source();

    expect(text).toMatch(
      /if\s*\(\s*updated\?\.status\s*\)\s*setStatus\(String\(updated\.status\)\.toUpperCase\(\)\)/,
    );

    expect(text).toMatch(
      /onUpdateInvoice\?\.\(updated\)/,
    );
  });
});

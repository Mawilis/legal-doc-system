/**
 * TITLE: WILSY OS Billing Forensic Proof Display
 * VERSION: v3.0.0-EOS-LEGACY-QR-VERIFY
 * AUTHORITY: Wilsy OS Core Governance; Python EOS owns billing evidence and IAM.
 * EPITOME: Displays invoice proof references, requests the compatible signed QR
 *          envelope, and verifies it against a persisted invoice in current tenant scope.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/billing/ForensicProofBlock.jsx
 * COLLABORATION / OWNERSHIP: BillingHUD supplies a read projection; the
 *                            authenticated API client and Python EOS bind access.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG:
 *   v3.0.0-EOS-LEGACY-QR-VERIFY adds authenticated legacy-compatible QR issue
 *     and signature verification while retaining the separate seal-reference check.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ECT Act section 15.
 * SECURITY / PRIVACY POSTURE: Only the invoice reference is sent; API bearer and
 *                             authenticated tenant scope come from the shared client.
 * TENANT BOUNDARY: Python EOS derives tenant scope from TenantAuthorizationContext;
 *                  invoice props and encoded tenant labels never authorize lookup.
 * AUTHORITY BOUNDARY: Signed QR validity establishes neither PKI document signature,
 *                     legal-content correctness, payment, execution, nor settlement.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import QRCode from 'qrcode';
import api from '../../services/api.js';

const textValue = (value) => (
  typeof value === 'string' && value.trim() ? value.trim() : ''
);

const isSha3Reference = (value) => /^[A-Fa-f0-9]{128}$/.test(value);

const referenceLabels = Object.freeze({
  not_checked: 'NOT CHECKED',
  checking: 'CHECKING',
  matched: 'SEAL REFERENCE MATCHED',
  missing: 'SEAL REFERENCE NOT FOUND',
  unavailable: 'VERIFICATION UNAVAILABLE',
});

const qrLabels = Object.freeze({
  loading: 'QR CONFIGURATION CHECK',
  ready: 'SIGNED QR AVAILABLE',
  unavailable: 'SIGNED QR UNAVAILABLE',
  checking: 'VERIFYING SIGNED QR',
  valid: 'SIGNED QR VERIFIED',
  invalid: 'SIGNED QR NOT VERIFIED',
});

const safeHttpsUrl = (value) => {
  if (typeof value !== 'string' || !value.trim()) return '';
  try {
    const url = new URL(value.trim());
    return url.protocol === 'https:' && !url.username && !url.password ? url.toString() : '';
  } catch {
    return '';
  }
};

const encodedPayloadFromUrl = (value) => {
  const safeUrl = safeHttpsUrl(value);
  if (!safeUrl) return '';
  try {
    const segments = new URL(safeUrl).pathname.split('/').filter(Boolean);
    const token = decodeURIComponent(segments.at(-1) || '');
    return token.includes('.') ? token : '';
  } catch {
    return '';
  }
};

const apiErrorCode = (error) => (
  error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'QR_SERVICE_UNAVAILABLE'
);

/**
 * @description Renders source proof references and authenticated Python EOS checks.
 * @collaboration BillingHUD supplies the invoice ID and display projection; the
 * shared API client forwards the current bearer and authenticated workspace scope.
 * @institutional Keeps legacy QR signature verification distinct from stored
 *                 seal-reference lookup and stored browser QR flags.
 * @param {{invoice: object, className?: string, status?: string}} props
 * @returns {JSX.Element} Bounded invoice QR and seal-reference verification controls.
 */
export default function ForensicProofBlock({ invoice, className = '' }) {
  const [qrImage, setQrImage] = useState(null);
  const [qrUrl, setQrUrl] = useState('');
  const [qrState, setQrState] = useState('loading');
  const [qrMessage, setQrMessage] = useState('Checking authenticated Python EOS QR availability.');
  const [displayError, setDisplayError] = useState('');
  const [referenceCheck, setReferenceCheck] = useState({
    kind: 'not_checked',
    message: 'No persisted seal-reference check has been performed.',
  });
  const [qrCheck, setQrCheck] = useState({ kind: 'not_checked', message: '' });
  const referenceController = useRef(null);
  const qrController = useRef(null);

  const invoiceId = textValue(
    invoice?.invoiceId || invoice?.invoice_id || invoice?.id || invoice?.invoiceNumber,
  );
  const invoiceNumber = textValue(invoice?.invoiceNumber || invoice?.invoice_number || invoiceId) || 'Not provided';
  const traceId = textValue(invoice?.traceId || invoice?.trace_id) || 'Not provided';
  const sealHash = textValue(invoice?.sealHash || invoice?.seal_hash || invoice?.proofHash || invoice?.proof_hash);
  const merkleRoot = textValue(invoice?.merkleRoot || invoice?.merkle_root);
  const currency = textValue(invoice?.currency) || 'Not provided';
  const rawAmount = Number(invoice?.totalAmount ?? invoice?.total_amount ?? invoice?.amount);
  const amount = Number.isFinite(rawAmount) ? rawAmount.toFixed(2) : 'Not provided';
  const storedLegacyFlag = invoice?.qrVerified === true;
  const suppliedUrl = useMemo(
    () => safeHttpsUrl(invoice?.qrVerificationUrl || invoice?.qr_verification_url),
    [invoice?.qrVerificationUrl, invoice?.qr_verification_url],
  );
  const encodedPayload = useMemo(() => encodedPayloadFromUrl(qrUrl), [qrUrl]);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    qrController.current?.abort();
    qrController.current = controller;
    setQrUrl('');
    setQrImage(null);
    setQrCheck({ kind: 'not_checked', message: '' });

    if (suppliedUrl) {
      setQrUrl(suppliedUrl);
      setQrState('ready');
      setQrMessage('Using the supplied HTTPS QR URL; Python EOS will validate its signed payload on request.');
      return () => {
        active = false;
        controller.abort();
      };
    }

    if (!invoiceId) {
      setQrState('unavailable');
      setQrMessage('A persisted invoice identifier is not available for authenticated QR issuance.');
      return () => {
        active = false;
        controller.abort();
      };
    }

    setQrState('loading');
    setQrMessage('Requesting a signed QR URL from authenticated Python EOS.');
    api.get(`/billing/invoices/${encodeURIComponent(invoiceId)}/qr`, {
      signal: controller.signal,
    }).then((response) => {
      if (!active) return;
      const payload = response?.data ?? response;
      const generatedUrl = safeHttpsUrl(payload?.verificationUrl);
      if (!generatedUrl || typeof payload?.encodedPayload !== 'string') {
        setQrState('unavailable');
        setQrMessage('Python EOS did not return a bounded HTTPS signed QR reference.');
        return;
      }
      setQrUrl(generatedUrl);
      setQrState('ready');
      setQrMessage('Signed QR reference issued from the persisted tenant-owned invoice.');
    }).catch((error) => {
      if (!active || error?.name === 'AbortError' || error?.name === 'CanceledError') return;
      setQrUrl('');
      setQrState('unavailable');
      setQrMessage(`Signed QR issuance unavailable: ${apiErrorCode(error)}`);
    });

    return () => {
      active = false;
      controller.abort();
      if (qrController.current === controller) qrController.current = null;
    };
  }, [invoiceId, suppliedUrl]);

  useEffect(() => {
    let active = true;
    setQrImage(null);
    if (!qrUrl) return () => { active = false; };

    QRCode.toDataURL(qrUrl, {
      width: 200,
      margin: 2,
      errorCorrectionLevel: 'M',
    }).then((image) => {
      if (active) setQrImage(image);
    }).catch(() => {
      if (active) setDisplayError('The signed QR URL could not be rendered locally.');
    });

    return () => { active = false; };
  }, [qrUrl]);

  useEffect(() => {
    setReferenceCheck({
      kind: 'not_checked',
      message: 'No persisted seal-reference check has been performed.',
    });
    referenceController.current?.abort();
    referenceController.current = null;
    return () => {
      referenceController.current?.abort();
      referenceController.current = null;
    };
  }, [sealHash]);

  const verifySealReference = async () => {
    if (!isSha3Reference(sealHash)) {
      setReferenceCheck({
        kind: 'unavailable',
        message: 'A valid SHA3-512 seal reference is not available for this invoice.',
      });
      return;
    }

    referenceController.current?.abort();
    const controller = new AbortController();
    referenceController.current = controller;
    setReferenceCheck({
      kind: 'checking',
      message: 'Checking the persisted reference in the authenticated tenant scope.',
    });
    setDisplayError('');

    try {
      const response = await api.post(
        '/billing/merkle/verify',
        { seal_hash: sealHash },
        { signal: controller.signal },
      );
      if (controller.signal.aborted) return;
      const result = response?.data ?? response;
      if (result?.valid === true) {
        setReferenceCheck({
          kind: 'matched',
          message: 'Python EOS found this persisted seal reference in the authenticated tenant scope.',
        });
      } else if (result?.valid === false) {
        setReferenceCheck({
          kind: 'missing',
          message: 'Python EOS found no matching persisted seal reference in the authenticated tenant scope.',
        });
      } else {
        setReferenceCheck({
          kind: 'unavailable',
          message: 'Python EOS returned no bounded seal-reference result.',
        });
      }
    } catch (error) {
      if (controller.signal.aborted || error?.name === 'CanceledError' || error?.name === 'AbortError') return;
      setReferenceCheck({
        kind: 'unavailable',
        message: 'The authenticated seal-reference check is unavailable.',
      });
    } finally {
      if (referenceController.current === controller) referenceController.current = null;
    }
  };

  const verifySignedQr = async () => {
    if (!encodedPayload) {
      setQrCheck({
        kind: 'unavailable',
        message: 'A compatible signed QR payload is not available for verification.',
      });
      return;
    }

    qrController.current?.abort();
    const controller = new AbortController();
    qrController.current = controller;
    setQrState('checking');
    setQrCheck({
      kind: 'checking',
      message: 'Validating signature, expiry, tenant scope, and persisted invoice match in Python EOS.',
    });
    try {
      const response = await api.get(
        `/qr/verify/${encodeURIComponent(encodedPayload)}`,
        { signal: controller.signal },
      );
      if (controller.signal.aborted) return;
      const result = response?.data ?? response;
      if (result?.valid === true && result?.verificationMode === 'LEGACY_SIGNED_QR_PERSISTED_INVOICE_MATCH') {
        setQrState('valid');
        setQrCheck({
          kind: 'valid',
          message: 'Python EOS verified the legacy signature and matched the invoice inside the authenticated tenant scope. PKI, payment, and settlement were not evaluated.',
        });
      } else {
        setQrState('unavailable');
        setQrCheck({ kind: 'invalid', message: 'Python EOS returned no verified legacy QR result.' });
      }
    } catch (error) {
      if (controller.signal.aborted || error?.name === 'CanceledError' || error?.name === 'AbortError') return;
      setQrState('unavailable');
      setQrCheck({
        kind: 'invalid',
        message: `Signed QR validation failed closed: ${apiErrorCode(error)}`,
      });
    } finally {
      if (qrController.current === controller) qrController.current = null;
    }
  };

  const copySeal = async () => {
    if (!sealHash) return;
    if (typeof navigator === 'undefined' || !navigator.clipboard?.writeText) {
      setDisplayError('Clipboard access is unavailable. Select and copy the seal manually.');
      return;
    }
    try {
      await navigator.clipboard.writeText(sealHash);
      setDisplayError('');
    } catch {
      setDisplayError('Clipboard access is unavailable. Select and copy the seal manually.');
    }
  };

  if (!invoice || typeof invoice !== 'object') {
    return (
      <div className="w-full rounded border border-red-500/20 bg-red-50/5 p-4 text-sm text-red-300">
        No invoice proof references were supplied.
      </div>
    );
  }

  return (
    <section
      className={`mx-auto w-full max-w-3xl rounded-xl border border-amber-500/30 bg-stone-900 p-6 font-sans shadow-2xl ${className}`}
      aria-labelledby="forensic-proof-title"
      aria-busy={referenceCheck.kind === 'checking' || qrState === 'checking'}
      data-testid="forensic-proof-block"
    >
      <header className="mb-4 flex items-center justify-between border-b border-stone-700 pb-3">
        <div>
          <h3 id="forensic-proof-title" className="font-mono text-base font-bold uppercase tracking-wider text-amber-400">
            Forensic proof references
          </h3>
          <p className="mt-1 text-xs text-stone-400">Invoice {invoiceNumber}</p>
        </div>
        <span
          className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 font-mono text-xs font-semibold text-amber-300"
          data-testid="forensic-proof-status"
        >
          {referenceLabels[referenceCheck.kind]}
        </span>
      </header>

      <div className="mb-4 rounded border border-amber-500/20 bg-amber-950/20 p-3 font-mono text-xs text-amber-100" role="status">
        {referenceCheck.message}
        {storedLegacyFlag && (
          <p className="mt-2 text-amber-200">
            A stored legacy qrVerified flag is present. It has not been revalidated and is not shown as verified.
          </p>
        )}
        <p className="mt-2 text-stone-300">
          Seal-reference lookup does not verify a QR signature or invoice content. Signed QR verification does not prove PKI authenticity, legal correctness, payment execution, or settlement.
        </p>
      </div>

      <div className="mb-2 flex items-center justify-center">
        {qrImage ? (
          <img
            src={qrImage}
            alt={`Signed QR reference for invoice ${invoiceNumber}; not verified until EOS validation succeeds`}
            className="h-36 w-36 rounded-lg border-2 border-amber-500/30 bg-white/5 object-contain"
          />
        ) : (
          <div className="flex h-36 w-36 items-center justify-center rounded-lg border-2 border-dashed border-stone-600 p-3 text-center text-xs text-stone-500">
            {qrState === 'unavailable' ? 'QR unavailable' : 'Preparing signed QR'}
          </div>
        )}
      </div>
      <p className="mb-4 text-center font-mono text-xs text-stone-400" data-testid="signed-qr-state">
        {qrLabels[qrState] || qrLabels.unavailable}: {qrCheck.message || qrMessage}
      </p>

      <dl className="mb-4 grid grid-cols-2 gap-2 font-mono text-xs text-stone-400">
        <div><dt className="inline text-amber-400">Invoice:</dt> <dd className="inline">{invoiceNumber}</dd></div>
        <div><dt className="inline text-amber-400">Trace ID:</dt> <dd className="inline">{traceId || 'Not provided'}</dd></div>
        <div><dt className="inline text-amber-400">Amount:</dt> <dd className="inline">{currency} {amount}</dd></div>
        <div><dt className="inline text-amber-400">Legacy flag:</dt> <dd className="inline">{storedLegacyFlag ? 'present, unverified' : 'absent'}</dd></div>
        <div className="col-span-2">
          <dt className="inline text-amber-400">Seal reference:</dt>{' '}
          <dd className="inline break-all text-stone-300">{sealHash || 'Not provided'}</dd>
        </div>
        <div className="col-span-2">
          <dt className="inline text-amber-400">Merkle reference:</dt>{' '}
          <dd className="inline break-all text-stone-300">{merkleRoot || 'Not provided'}</dd>
        </div>
      </dl>

      {displayError && (
        <p className="mb-3 rounded border border-amber-500/20 bg-amber-950/30 p-2 font-mono text-xs text-amber-200" role="alert">
          {displayError}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={verifySignedQr}
          disabled={!encodedPayload || qrState === 'checking' || qrState === 'loading'}
          className="rounded bg-cyan-800 px-3 py-2 text-xs font-semibold text-cyan-50 transition-colors hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50"
          title="Validate the legacy signature and invoice only inside the authenticated tenant scope"
        >
          {qrState === 'checking' ? 'Verifying signed QR…' : 'Verify signed QR'}
        </button>
        {isSha3Reference(sealHash) && (
          <button
            type="button"
            onClick={verifySealReference}
            disabled={referenceCheck.kind === 'checking'}
            className="rounded bg-amber-700 px-3 py-2 text-xs font-semibold text-amber-50 transition-colors hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
            title="Check this persisted seal reference inside the authenticated tenant scope"
          >
            {referenceCheck.kind === 'checking' ? 'Checking seal reference…' : 'Check seal reference'}
          </button>
        )}
        {sealHash && (
          <button
            type="button"
            onClick={copySeal}
            className="rounded bg-stone-800 px-3 py-2 text-xs text-stone-300 transition-colors hover:bg-stone-700"
            title="Copy the displayed seal reference"
          >
            Copy seal reference
          </button>
        )}
      </div>
    </section>
  );
}

/**
 * ARTIFACT: WILSY OS Billing Forensic Proof Display
 * VERSION: v3.0.0-EOS-LEGACY-QR-VERIFY
 * AUTHORITY BOUNDARY: Authenticated Python EOS QR and seal-reference checks only.
 * TENANT POSTURE: EOS derives scope from the current authorized session.
 * FAIL-CLOSED POSTURE: Missing config, malformed payload, mismatch, and transport errors never report verification.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */

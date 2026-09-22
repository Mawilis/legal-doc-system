/**
 * WILSY OS — BFF INTERNAL RECOVERY DELIVERY MOUNT CERTIFICATE
 * VERSION: v1.0.0-R10E6-BFF-INTERNAL-RECOVERY-MOUNT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies middleware ordering for the internal recovery delivery
 *          bridge without starting Node, Python, MongoDB, or SMTP.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/passwordRecoveryDeliveryMount.test.js
 * COLLABORATION / OWNERSHIP: Static topology evidence for server/server.js;
 *                            route semantics are certified separately.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E6-BFF-INTERNAL-RECOVERY-MOUNT-CERT — Certifies import/mount identity,
 *            body-parser ordering, public-auth proxy preservation, API catch-all
 *            ordering, and current runtime version.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Source-only assertions; no secrets or requests.
 * TENANT BOUNDARY: No tenant authority is exercised.
 * AUTHORITY BOUNDARY: BFF route composition evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { expect } from 'chai';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SERVER_PATH = path.resolve(HERE, '../../server.js');

describe('BFF internal recovery delivery mount', () => {
  it('mounts the recovery bridge only after body parsing and before API catch-all', () => {
    const source = fs.readFileSync(SERVER_PATH, 'utf8');
    const authProxy = source.indexOf("app.use('/api/auth', buildKennelProxy");
    const jsonParser = source.indexOf("app.use(express.json({ limit: '50mb' }));");
    const internalMount = source.indexOf("app.use('/internal/auth', passwordRecoveryDeliveryRouter);");
    const apiCatchall = source.indexOf("app.use('/api', (req, res) =>");

    expect(authProxy).to.be.greaterThan(-1);
    expect(jsonParser).to.be.greaterThan(authProxy);
    expect(internalMount).to.be.greaterThan(jsonParser);
    expect(apiCatchall).to.be.greaterThan(internalMount);
  });

  it('imports one dedicated transport-only internal recovery router', () => {
    const source = fs.readFileSync(SERVER_PATH, 'utf8');
    expect(source).to.contain(
      "import passwordRecoveryDeliveryRouter from './routes/passwordRecoveryDelivery.js';",
    );
    expect(source.match(/passwordRecoveryDeliveryRouter/g)).to.have.lengthOf(2);
    expect(source).not.to.contain("app.post('/api/auth/password-recovery-delivery'");
    expect(source).not.to.contain("app.use('/api/auth', passwordRecoveryDeliveryRouter");
  });

  it('preserves the Python auth proxy and current recovery-mount runtime version', () => {
    const source = fs.readFileSync(SERVER_PATH, 'utf8');
    expect(source).to.contain(
      "app.use('/api/auth', buildKennelProxy({ mountPrefix: '/api/auth', targetPrefix: '/api/auth' }));",
    );
    expect(source).to.contain(
      "const VERSION = 'v5.5.0-R10E6-RECOVERY-DELIVERY-INTERNAL-MOUNT';",
    );
  });
});

/**
 * ARTIFACT: server/tests/routes/passwordRecoveryDeliveryMount.test.js
 * VERSION: v1.0.0-R10E6-BFF-INTERNAL-RECOVERY-MOUNT-CERT
 * AUTHORITY BOUNDARY: static BFF middleware-order evidence only
 * TENANT POSTURE: public auth proxy remains upstream Python transport
 * FAIL-CLOSED POSTURE: recovery route cannot precede body parsing or replace public auth proxy
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */

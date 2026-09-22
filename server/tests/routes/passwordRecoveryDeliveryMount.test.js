/**
 * WILSY OS — BFF INTERNAL RECOVERY DELIVERY MOUNT CERTIFICATE
 * VERSION: v1.1.0-R10E17-BFF-SEPARATED-RECOVERY-MOUNTS-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies middleware ordering for the internal recovery delivery
 *          bridge without starting Node, Python, MongoDB, or SMTP.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/passwordRecoveryDeliveryMount.test.js
 * COLLABORATION / OWNERSHIP: Static topology evidence for server/server.js;
 *                            route semantics are certified separately.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.1.0-R10E17-BFF-SEPARATED-RECOVERY-MOUNTS-CERT — Adds static evidence for the separately keyed
 *            recovery-contact-verification bridge beside the password-recovery
 *            bridge, preserving body-parser order, public-auth proxy topology,
 *            API catch-all order, and current runtime version.
 *            v1.0.0-R10E6-BFF-INTERNAL-RECOVERY-MOUNT-CERT — Certifies import/mount identity,
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
    const passwordRecoveryMount = source.indexOf("app.use('/internal/auth', passwordRecoveryDeliveryRouter);");
    const contactVerificationMount = source.indexOf(
      "app.use('/internal/auth', recoveryContactVerificationDeliveryRouter);",
    );
    const apiCatchall = source.indexOf("app.use('/api', (req, res) =>");

    expect(authProxy).to.be.greaterThan(-1);
    expect(jsonParser).to.be.greaterThan(authProxy);
    expect(passwordRecoveryMount).to.be.greaterThan(jsonParser);
    expect(contactVerificationMount).to.be.greaterThan(passwordRecoveryMount);
    expect(apiCatchall).to.be.greaterThan(contactVerificationMount);
  });

  it('imports two dedicated transport-only internal recovery routers', () => {
    const source = fs.readFileSync(SERVER_PATH, 'utf8');
    expect(source).to.contain(
      "import passwordRecoveryDeliveryRouter from './routes/passwordRecoveryDelivery.js';",
    );
    expect(source).to.contain(
      "import recoveryContactVerificationDeliveryRouter from './routes/recoveryContactVerificationDelivery.js';",
    );
    expect(source.match(/passwordRecoveryDeliveryRouter/g)).to.have.lengthOf(2);
    expect(source.match(/recoveryContactVerificationDeliveryRouter/g)).to.have.lengthOf(2);
    expect(source).not.to.contain("app.use('/api/auth', passwordRecoveryDeliveryRouter");
    expect(source).not.to.contain("app.use('/api/auth', recoveryContactVerificationDeliveryRouter");
  });

  it('preserves the Python auth proxy and current recovery-mount runtime version', () => {
    const source = fs.readFileSync(SERVER_PATH, 'utf8');
    expect(source).to.contain(
      "app.use('/api/auth', buildKennelProxy({ mountPrefix: '/api/auth', targetPrefix: '/api/auth' }));",
    );
    expect(source).to.contain(
      "const VERSION = 'v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT';",
    );
  });
});

/**
 * ARTIFACT: server/tests/routes/passwordRecoveryDeliveryMount.test.js
 * VERSION: v1.1.0-R10E17-BFF-SEPARATED-RECOVERY-MOUNTS-CERT
 * AUTHORITY BOUNDARY: static BFF middleware-order evidence only
 * TENANT POSTURE: public auth proxy remains upstream Python transport
 * FAIL-CLOSED POSTURE: recovery route cannot precede body parsing or replace public auth proxy
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */

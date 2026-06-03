/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - INSTITUTIONAL MAILER SERVICE [V1.0.1-OMEGA-ALIGNMENT]                                                                       ║
 * ║ [BOARDROOM DISPATCH | FORENSIC SEAL VERIFICATION | INVESTOR TELEMETRY | BIBLICAL WORTH]                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.1-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/email.js                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated secure investor distribution for $1B valuation artifacts. [2026-05-04]               ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Engineered the forensic mailer with SHA3-512 signature verification.                          ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Hardened attachment buffers and boardroom HTML for high-velocity strikes. [2026-05-04]          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import nodemailer from 'nodemailer';
import { verifyForensicSeal } from '../utils/forensicSigner.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import brandingConfig from '../config/brandingConfig.js';

const router = express.Router();

/**
 * @route POST /api/email/send
 * @description Executes an institutional mail strike, delivering forensic PDF artifacts to the Board.
 * @access SOVEREIGN_ONLY
 */
router.post('/send', async (req, res) => {
  const { subject, recipients, traceId } = req.body;
  const file = req.files?.file;

  console.log(`[MAIL-STRIKE] Initiating distribution for Trace: ${traceId || 'UNTRACKED'}`);

  // 🛡️ FORENSIC INTEGRITY CHECK: Reject any strike without a biblically valid seal
  const isAuthorized = verifyForensicSeal(req.headers, req.body);
  if (!isAuthorized) {
    console.error(`[SECURITY-BREACH] Unauthorized mail strike attempted. Trace: ${traceId}`);
    return res.status(403).json({
      status: 'FRACTURE',
      message: 'CRYPTOGRAPHIC_SEAL_INVALID'
    });
  }

  if (!file) {
    return res.status(400).json({ status: 'FRACTURE', message: 'ARTIFACT_MISSING' });
  }

  try {
    // 🏛️ TRANSPORTER CONFIGURATION: Utilizing high-velocity institutional SMTP
    const transporter = nodemailer.createTransport({
      service: process.env.MAIL_SERVICE || 'SendGrid',
      auth: {
        user: process.env.MAIL_USER,
        pass: process.env.MAIL_PASS
      }
    });

    const targetRecipients = JSON.parse(recipients || '[]');

    // 📧 INSTITUTIONAL DISPATCH
    await transporter.sendMail({
      from: `"Wilsy OS Reports" <reports@wilsyos.com>`,
      to: targetRecipients,
      subject: subject || brandingConfig.headers.dashboardReport,
      text: `Institutional Finality reached. Attached is the Wilsy OS Investor Report for Trace: ${traceId}.`,
      html: `
        <div style="font-family: 'Helvetica', sans-serif; background: #000; color: #fff; padding: 40px; border: 2px solid #D4AF37;">
          <h2 style="color: #D4AF37; letter-spacing: 2px; text-transform: uppercase;">Wilsy OS</h2>
          <p style="color: #888; font-size: 12px; text-transform: uppercase;">Sovereign Investor Dispatch</p>
          <hr style="border: 0; border-top: 1px solid #333; margin: 20px 0;" />
          <p style="font-size: 14px;">The latest high-fidelity institutional artifact (Revenue, Compliance, Forensics) has been generated and forensically sealed.</p>
          <div style="background: #0a0a0a; padding: 15px; margin: 20px 0; border-left: 4px solid #D4AF37;">
             <p style="font-size: 11px; color: #666; margin: 0;">TRACE_ID: ${traceId}</p>
             <p style="font-size: 11px; color: #666; margin: 5px 0 0 0;">EPITOME: BIBLICAL WORTH BILLIONS</p>
          </div>
          <p style="font-size: 12px; color: #888; margin-top: 30px;">This artifact is legally non-repudiable and anchored to the Wilsy OS Sovereign Nucleus.</p>
        </div>
      `,
      attachments: [{
        filename: file.name || 'WilsyOS-InvestorReport.pdf',
        content: file.data
      }]
    });

    // 📡 TELEMETRY BROADCAST: Logging the successful distribution strike
    broadcastTelemetry('WILSY_GLOBAL_ROOT', 'INVESTOR_REPORT_DISPATCHED', 'SUCCESS', {
      traceId,
      recipientCount: targetRecipients.length
    });

    res.json({
      status: 'SENT',
      traceId,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error(`💥 [MAIL-FRACTURE] Strike failed: ${error.message}`);

    broadcastTelemetry('WILSY_GLOBAL_ROOT', 'INVESTOR_REPORT_DISPATCHED', 'FAILURE', {
      error: error.message,
      traceId
    });

    res.status(500).json({
      status: 'FRACTURE',
      message: 'DISTRIBUTION_FAILED',
      trace: error.message
    });
  }
});

export default router;

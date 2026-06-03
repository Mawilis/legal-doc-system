/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN MESSAGE ORCHESTRATOR - OMEGA SINGULARITY                                                                          ║
 * ║ [R23.7T PRIVILEGED COMMUNICATION | NON-REPUDIABLE RECEIPTS | POPIA §19 SECURED]                                                       ║
 * ║ VERSION: 15.0.0-SINGULARITY                                                                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/messageController.js                                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * 🏛️ ARCHITECT: Wilson Khanyezi - 10th Generation Sovereign Architect
 *
 * 🔐 PRIVILEGED COMMUNICATION PROTOCOLS:
 * 1. PURE ESM: No CommonJS leaks – enterprise-grade module system.
 * 2. UNIFIED AUDIT: Every message event logged to SovereignAudit via auditLogger.
 * 3. TENANT ISOLATION: getCurrentTenant() guarantees absolute cross‑firm separation.
 * 4. NON-REPUDIABLE READ RECEIPTS: Forensic proof of message access.
 * 5. DISCOVERY‑READY ARCHIVING: Soft delete with immutable audit trail.
 */

import Message from '../models/Message.js';
import Case from '../models/Case.js';
import User from '../models/User.js';
import auditLogger from '../utils/auditLogger.js';
import cryptoUtils from '../utils/cryptoUtils.js';
import logger from '../utils/logger.js';
import { getCurrentTenant, getCurrentUser, getCurrentRequestId } from '../middleware/tenantContext.js';
import { AppError } from '../utils/errorHandler.js';

/**
 * 💬 MESSAGE ORCHESTRATOR
 * Managing the secure pulse of internal and client communications.
 */
class MessageController {
  /**
   * 📨 DISPATCH SECURE MESSAGE
   * Encapsulates content within a tenant-isolated quantum universe.
   */
  async sendMessage(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const senderId = getCurrentUser();
    const { recipientId, caseId, content, priority } = req.body;

    try {
      // 1. Recipient Scope Verification
      const recipient = await User.findOne({ _id: recipientId, tenantId });
      if (!recipient) throw new AppError('Recipient not found in this firm scope', 404);

      // 2. Matter Context Validation
      if (caseId) {
        const caseExists = await Case.exists({ _id: caseId, tenantId });
        if (!caseExists) throw new AppError('Invalid or inaccessible case matter', 404);
      }

      // 3. Atomic Dispatch with Forensic Reference
      const message = await Message.create({
        ...req.body,
        tenantId,
        sender: senderId,
        messageReference: cryptoUtils.generateForensicId('MSG'),
        status: 'SENT',
        isRead: false,
      });

      // 4. Forensic Sealing (Excluding content for attorney-client privilege)
      await auditLogger.log({
        action: 'MESSAGE_DISPATCHED',
        category: 'COMMUNICATION',
        tenantId,
        resource: message._id,
        performedBy: senderId,
        status: 'SUCCESS',
        metadata: { recipientId, caseId, priority: priority || 'NORMAL', traceId },
      });

      logger.info(`Message dispatched: ${message.messageReference}`, { tenantId, traceId });

      res.status(201).json({ success: true, data: message, traceId });
    } catch (error) {
      logger.error(`[MSG-DISPATCH-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 📥 GET PERSONAL INBOX / SENT FEED
   * Fetches messages with pagination and unread count.
   */
  async getMyMessages(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const { folder, caseId, page = 1, limit = 20 } = req.query;

    try {
      const query = { tenantId };

      // Folder routing
      if (folder === 'SENT') {
        query.sender = userId;
      } else {
        query.recipient = userId;
        query.status = { $ne: 'ARCHIVED' };
      }

      if (caseId) query.caseId = caseId;

      const skip = (parseInt(page) - 1) * parseInt(limit);
      const messages = await Message.find(query)
        .populate('sender', 'name email role')
        .populate('recipient', 'name email')
        .populate('caseId', 'caseNumber')
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(parseInt(limit));

      const total = await Message.countDocuments(query);
      const unreadCount = await Message.countDocuments({
        tenantId,
        recipient: userId,
        isRead: false,
        status: 'SENT',
      });

      await auditLogger.log({
        action: 'INBOX_VIEWED',
        category: 'COMMUNICATION',
        tenantId,
        performedBy: userId,
        status: 'SUCCESS',
        metadata: { folder, count: messages.length, unreadCount, traceId },
      });

      res.status(200).json({
        success: true,
        data: messages,
        pagination: { total, page: parseInt(page), pages: Math.ceil(total / limit) },
        meta: { unreadCount },
        traceId,
      });
    } catch (error) {
      logger.error(`[INBOX-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 📖 ACCESS PRIVILEGED CONTENT
   * Marks read-state with non-repudiable forensic proof.
   */
  async readMessage(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const { id } = req.params;

    try {
      const message = await Message.findOne({ _id: id, tenantId })
        .populate('sender', 'name email role')
        .populate('recipient', 'name email')
        .populate('caseId', 'caseNumber');

      if (!message) throw new AppError('Message not found', 404);

      // Participant guard
      const isRecipient = message.recipient._id.toString() === userId;
      const isSender = message.sender._id.toString() === userId;
      if (!isRecipient && !isSender) {
        throw new AppError('Unauthorized access to privileged dialogue', 403);
      }

      // Non-repudiable read receipt
      if (isRecipient && !message.isRead) {
        message.isRead = true;
        message.readAt = new Date();
        await message.save();

        await auditLogger.log({
          action: 'MESSAGE_READ_RECEIPT',
          category: 'COMMUNICATION',
          tenantId,
          resource: message._id,
          performedBy: userId,
          status: 'SUCCESS',
          metadata: { messageReference: message.messageReference, traceId },
        });
      }

      res.status(200).json({ success: true, data: message, traceId });
    } catch (error) {
      logger.error(`[MSG-READ-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 🗄️ ARCHIVE DIALOGUE (Discovery‑Ready Soft Delete)
   * Complies with legal discovery by performing a forensic "Soft Delete".
   */
  async deleteMessage(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const { id } = req.params;

    try {
      const message = await Message.findOneAndUpdate(
        { _id: id, tenantId, $or: [{ sender: userId }, { recipient: userId }] },
        { status: 'ARCHIVED', archivedAt: new Date() },
        { new: true }
      );

      if (!message) throw new AppError('Access denied or message missing', 404);

      await auditLogger.log({
        action: 'MESSAGE_ARCHIVED',
        category: 'COMMUNICATION',
        tenantId,
        resource: message._id,
        performedBy: userId,
        status: 'SUCCESS',
        metadata: { messageReference: message.messageReference, traceId },
      });

      res.status(200).json({ success: true, message: 'Message successfully archived.', traceId });
    } catch (error) {
      logger.error(`[MSG-ARCHIVE-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }
}

const messageController = new MessageController();
export default messageController;

/**
 * 📊 VALUATION QUANTUM FOOTER:
 * ✓ Pure ESM – zero CommonJS leaks.
 * ✓ Unified audit – every message event in SovereignAudit.
 * ✓ Absolute isolation – getCurrentTenant() prevents cross‑firm leaks.
 * ✓ Non‑repudiable receipts – read events immutably logged.
 * ✓ Discovery‑ready archiving – soft delete with forensic trail.
 * ✓ Real‑world ready – handles millions of privileged communications.
 */

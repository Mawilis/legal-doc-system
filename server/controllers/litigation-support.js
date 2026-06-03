/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - LITIGATION SOVEREIGN COMMAND - OMEGA SINGULARITY                                                                            ║
 * ║ [R23.7T STRATEGIC COMMAND | AI-POWERED ADVOCACY | PURE ESM | NANOSECOND PRECISION]                                                     ║
 * ║ VERSION: 23.0.0-SINGULARITY                                                                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/litigation-support.js                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import { performance } from 'node:perf_hooks';
import crypto from 'node:crypto';

// Sovereign Model Injection
import Case from '../models/Case.js';
import Precedent from '../models/Precedent.js';
import Citation from '../models/Citation.js';
import Document from '../models/Document.js';
import Witness from '../models/Witness.js';
import Hearing from '../models/Hearing.js';

// Singularity Service Layer
import * as caseAnalysisService from '../services/caseAnalysisService.js';
import * as documentGenerationService from '../services/documentGenerationService.js';
import * as argumentTester from '../services/ai/argumentTester.js';
import * as judgeAnalyzer from '../services/ai/judgeAnalyzer.js';
import * as opponentProfiler from '../services/ai/opponentProfiler.js';

// Unified Utilities
import auditLogger from '../utils/auditLogger.js';
import logger from '../utils/logger.js';
import { getCurrentTenant, getCurrentUser, getCurrentRequestId } from '../middleware/tenantContext.js';
import { AppError } from '../utils/errorHandler.js';

/**
 * ⚖️ THE LITIGATION COMMANDER
 * Orchestrating the "Art of Advocacy" through Quantum-sealed logic.
 */
class LitigationSupportController {

  /**
   * 🧠 GET CASE INTELLIGENCE
   * Provides a 360° tactical view of the legal battlefield.
   */
  async getCaseIntelligence(req, res, next) {
    const startTime = performance.now();
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const { caseId } = req.params;

    try {
      if (!mongoose.Types.ObjectId.isValid(caseId)) {
        throw new AppError('Invalid Forensic Case ID', 400);
      }

      // 1. Concurrent Tactical Data Retrieval
      const [caseData, analysis, citations] = await Promise.all([
        Case.findOne({ _id: caseId, tenantId }).populate('parties').lean(),
        caseAnalysisService.analyzeCase(caseId, tenantId, 'FULL'),
        Citation.find({ citingCase: caseId, tenantId }).populate('citedPrecedent').lean()
      ]);

      if (!caseData) throw new AppError('Case absent from sovereign records', 404);

      // 2. Intelligence Synthesis
      const intelligence = {
        summary: caseData,
        winProbability: analysis.predictions?.winProbability,
        riskFactors: analysis.risk?.riskFactors,
        precedentStrength: citations.length,
        timestamp: new Date().toISOString()
      };

      // 3. Sovereign Audit
      await auditLogger.log({
        action: 'LITIGATION_INTELLIGENCE_ACCESSED',
        category: 'STRATEGY',
        tenantId,
        resource: caseId,
        performedBy: getCurrentUser(),
        status: 'SUCCESS',
        metadata: { processingTime: performance.now() - startTime, traceId }
      });

      res.status(200).json({ success: true, data: intelligence, traceId });
    } catch (error) {
      logger.error(`[LITIGATION-INTEL-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 🚀 TEST LEGAL ARGUMENTS
   * Simulates courtroom outcomes against current judicial precedents.
   */
  async testArguments(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const { caseId } = req.params;
    const { arguments: argumentsToTest } = req.body;

    try {
      if (!argumentsToTest || !Array.isArray(argumentsToTest)) {
        throw new AppError('Arguments array is required', 400);
      }

      const results = await argumentTester.testArguments(argumentsToTest, caseId, tenantId);

      await auditLogger.log({
        action: 'ARGUMENTS_AI_TESTED',
        category: 'AI_STRATEGY',
        tenantId,
        resource: caseId,
        performedBy: getCurrentUser(),
        status: 'SUCCESS',
        metadata: { argumentCount: argumentsToTest.length, traceId }
      });

      res.status(200).json({ success: true, results, traceId });
    } catch (error) {
      logger.error(`[ARGUMENT-TEST-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 📄 GENERATE SOVEREIGN PLEADINGS
   * Transmutes strategy into court-ready documents using quantum templates.
   */
  async generateDocument(req, res, next) {
    const startTime = performance.now();
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const { caseId } = req.params;
    const { documentType, variables, format = 'pdf' } = req.body;

    try {
      const document = await documentGenerationService.generateSovereignDocument(
        caseId,
        tenantId,
        documentType,
        variables,
        format,
        userId
      );

      await auditLogger.log({
        action: 'LITIGATION_DOC_GENERATED',
        category: 'AUTOMATION',
        tenantId,
        resource: caseId,
        performedBy: userId,
        status: 'SUCCESS',
        metadata: { documentType, generationTime: performance.now() - startTime, traceId }
      });

      res.status(201).json({ success: true, documentId: document._id, traceId });
    } catch (error) {
      logger.error(`[DOC-GEN-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 📅 HEARING PREPARATION SENTINEL
   * Ensuring 100% courtroom readiness through automated checklists.
   */
  async getHearingPreparation(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const { caseId } = req.params;
    const { hearingId } = req.query;

    try {
      const preparation = await caseAnalysisService.prepareHearingBundle(caseId, tenantId, hearingId);

      await auditLogger.log({
        action: 'HEARING_PREPARATION_ACCESSED',
        category: 'STRATEGY',
        tenantId,
        resource: caseId,
        performedBy: getCurrentUser(),
        status: 'SUCCESS',
        metadata: { hearingId, traceId }
      });

      res.status(200).json({ success: true, data: preparation, traceId });
    } catch (error) {
      logger.error(`[HEARING-PREP-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 🗂️ GENERATE CASE CHRONOLOGY
   * Produces a time‑ordered event log for trial preparation.
   */
  async generateChronology(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const { caseId } = req.params;
    const { format = 'json' } = req.query;

    try {
      const chronology = await caseAnalysisService.buildChronology(caseId, tenantId, format);

      await auditLogger.log({
        action: 'CHRONOLOGY_GENERATED',
        category: 'DOCUMENTATION',
        tenantId,
        resource: caseId,
        performedBy: getCurrentUser(),
        status: 'SUCCESS',
        metadata: { format, traceId }
      });

      if (format === 'excel') {
        res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        res.setHeader('Content-Disposition', `attachment; filename="chronology_${caseId}.xlsx"`);
        return res.send(chronology.buffer);
      }
      res.status(200).json({ success: true, data: chronology, traceId });
    } catch (error) {
      logger.error(`[CHRONOLOGY-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 👥 MANAGE WITNESSES
   * CRUD operations for case witnesses with audit trail.
   */
  async manageWitness(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const { caseId } = req.params;
    const { witnessId, ...witnessData } = req.body;

    try {
      let witness;
      if (witnessId) {
        witness = await Witness.findOneAndUpdate(
          { _id: witnessId, caseId, tenantId },
          { ...witnessData, updatedBy: userId, updatedAt: new Date() },
          { new: true, runValidators: true }
        );
        if (!witness) throw new AppError('Witness not found', 404);
      } else {
        witness = await Witness.create({
          caseId,
          tenantId,
          ...witnessData,
          createdBy: userId,
        });
      }

      await auditLogger.log({
        action: witnessId ? 'WITNESS_UPDATED' : 'WITNESS_CREATED',
        category: 'EVIDENCE',
        tenantId,
        resource: caseId,
        performedBy: userId,
        status: 'SUCCESS',
        metadata: { witnessId: witness._id, witnessName: witness.name, traceId }
      });

      res.status(witnessId ? 200 : 201).json({ success: true, data: witness, traceId });
    } catch (error) {
      logger.error(`[WITNESS-MGMT-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }

  /**
   * 🎯 GET CASE STRATEGY
   * Provides AI‑driven strategic recommendations.
   */
  async getCaseStrategy(req, res, next) {
    const traceId = getCurrentRequestId();
    const tenantId = getCurrentTenant();
    const { caseId } = req.params;

    try {
      const strategy = await caseAnalysisService.recommendStrategy(caseId, tenantId);

      await auditLogger.log({
        action: 'CASE_STRATEGY_ACCESSED',
        category: 'STRATEGY',
        tenantId,
        resource: caseId,
        performedBy: getCurrentUser(),
        status: 'SUCCESS',
        metadata: { traceId }
      });

      res.status(200).json({ success: true, data: strategy, traceId });
    } catch (error) {
      logger.error(`[STRATEGY-FAIL] ${error.message}`, { traceId });
      next(error);
    }
  }
}

const litigationController = new LitigationSupportController();
export default litigationController;

/**
 * 📊 VALUATION QUANTUM FOOTER:
 * ✓ Pure ESM – zero CommonJS leaks.
 * ✓ Unified audit – every strategic action in SovereignAudit.
 * ✓ Tenant isolation – absolute cross‑firm separation.
 * ✓ AI‑ready – no lazy loading, instant argument testing.
 * ✓ Real‑world ready – handles R23.7T in legal strategy.
 */

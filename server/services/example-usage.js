/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ EXAMPLE USAGE - DOCUMENT GENERATION ENGINE                                ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import getDocumentGenerationEngine from './documentGenerationService.js';
import { DocumentTemplate } from '../models/DocumentTemplate.js';

async function example() {
  try {
    // Get engine instance
    const engine = await getDocumentGenerationEngine();
    
    // Example 1: Generate a single document
    const result = await engine.generateDocument(
      'TMP-1234', // template ID
      {
        clientName: 'John Doe',
        clientIdNumber: '9001015084083',
        contractDate: '2026-02-28',
        contractAmount: 1500000,
        propertyAddress: '123 Main Street, Sandton, Johannesburg'
      },
      {
        format: 'pdf',
        userId: 'user-123',
        tenantId: 'law-firm-001',
        correlationId: 'corr-123456',
        encrypt: true,
        sign: true
      }
    );

    console.log('Document generated:', {
      format: result.format,
      size: result.document.length,
      metadata: result.metadata
    });

    // Example 2: Batch generation
    const batchResult = await engine.generateBatch(
      'batch-001',
      [
        {
          id: 'doc-1',
          templateId: 'TMP-1234',
          variables: {
            clientName: 'Jane Smith',
            contractAmount: 750000
          }
        },
        {
          id: 'doc-2',
          templateId: 'TMP-5678',
          variables: {
            companyName: 'Acme Corp',
            registrationNumber: '2020/123456/07'
          }
        }
      ],
      {
        userId: 'user-123',
        tenantId: 'law-firm-001'
      }
    );

    console.log('Batch generation:', {
      total: batchResult.total,
      successful: batchResult.successful,
      failed: batchResult.failed
    });

    // Example 3: Queue for background processing
    const queued = await engine.queueDocumentGeneration(
      'TMP-1234',
      {
        clientName: 'Background Job',
        contractAmount: 2500000
      },
      {
        priority: 3, // MEDIUM
        delay: 5000, // 5 seconds delay
        userId: 'user-123'
      }
    );

    console.log('Queued:', queued);

    // Get engine status
    const status = await engine.getStatus();
    console.log('Engine status:', status);

  } catch (error) {
    console.error('Generation failed:', error);
  }
}

// Run example
example();

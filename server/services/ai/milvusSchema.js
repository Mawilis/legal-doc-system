#!/* eslint-disable */
/*
 * WILSY OS: NEURAL PRECEDENT SCHEMA - THE KNOWLEDGE ENGINE
 * ============================================================================
 *
 *     ███╗   ███╗██╗██╗     ██╗   ██╗██╗   ██╗███████╗
 *     ████╗ ████║██║██║     ██║   ██║██║   ██║██╔════╝
 *     ██╔████╔██║██║██║     ██║   ██║██║   ██║███████╗
 *     ██║╚██╔╝██║██║██║     ██║   ██║╚██╗ ██╔╝╚════██║
 *     ██║ ╚═╝ ██║██║███████╗╚██████╔╝ ╚████╔╝ ███████║
 *     ╚═╝     ╚═╝╚═╝╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝
 *
 *     ███████╗ ██████╗██╗  ██╗███████╗███╗   ███╗ █████╗
 *     ██╔════╝██╔════╝██║  ██║██╔════╝████╗ ████║██╔══██╗
 *     ███████╗██║     ███████║█████╗  ██╔████╔██║███████║
 *     ╚════██║██║     ██╔══██║██╔══╝  ██║╚██╔╝██║██╔══██║
 *     ███████║╚██████╗██║  ██║███████╗██║ ╚═╝ ██║██║  ██║
 *     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝
 *
 * ============================================================================
 * CORE DOCTRINE: Standard databases index words; Wilsy OS indexes meaning.
 * This schema defines the 768-dimensional vector space for Legal-BERT,
 * enabling semantic search based on "Intent" or "Legal Principle" rather
 * than just keyword matches.
 *
 * This is the architecture that Silicon Valley investors will value at $2B+.
 *
 * QUANTUM ARCHITECTURE:
 *
 *  ┌─────────────────────────────────────────────────────────────────────────────┐
 *  │                    MILVUS COLLECTION - NEURAL KNOWLEDGE BASE                 │
 *  └─────────────────────────────────────────────────────────────────────────┬───┘
 *                                                                           │
 *  ┌─────────────────────────────────────────────────────────────────────────▼───┐
 *  │                         COLLECTION: wilsy_precedent_index                   │
 *  ├─────────────────────────────────────────────────────────────────────────────┤
 *  │  ┌──────────────────────────────────────────────────────────────────────┐  │
 *  │  │  Fields:                                                              │  │
 *  │  │  ├── precedent_id  : Int64 (Primary Key, Auto ID)                   │  │
 *  │  │  ├── tenant_id     : VarChar(64) (Tenant Isolation)                  │  │
 *  │  │  ├── legal_vector  : FloatVector[768] (Legal-BERT Embedding)        │  │
 *  │  │  ├── metadata      : JSON (Citation, Court, Jurisdiction)           │  │
 *  │  │  ├── case_number   : VarChar(64) (Indexed)                           │  │
 *  │  │  ├── court         : VarChar(128) (Indexed)                          │  │
 *  │  │  ├── decision_date : Int64 (Unix timestamp)                          │  │
 *  │  │  ├── legal_areas   : Array(VarChar) (Indexed)                        │  │
 *  │  │  └── citation_count: Int32 (Indexed)                                 │  │
 *  │  └──────────────────────────────────────────────────────────────────────┘  │
 *  └─────────────────────────────────────────────────────────────────────────────┘
 *                                                                           │
 *  ┌─────────────────────────────────────────────────────────────────────────▼───┐
 *  │                         INDEX CONFIGURATION                                   │
 *  ├─────────────────────────────────────────────────────────────────────────────┤
 *  │  ┌──────────────────────────────────────────────────────────────────────┐  │
 *  │  │  Index Type: IVF_FLAT                                                 │  │
 *  │  │  Metric Type: COSINE (Best for semantic similarity in law)           │  │
 *  │  │  Parameters: { nlist: 1024 }                                          │  │
 *  │  │  Search params: { nprobe: 16 }                                        │  │
 *  │  └──────────────────────────────────────────────────────────────────────┘  │
 *  └─────────────────────────────────────────────────────────────────────────────┘
 *                                                                           │
 *  ┌─────────────────────────────────────────────────────────────────────────▼───┐
 *  │                         QUERY TYPES                                           │
 *  ├─────────────────────────────────────────────────────────────────────────────┤
 *  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
 *  │  │  Semantic    │  │  Hybrid      │  │  Scalar      │  │  Range       │   │
 *  │  │  Search      │──│  Search      │──│  Filter      │──│  Search      │   │
 *  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
 *  └─────────────────────────────────────────────────────────────────────────────┘
 *
 * @version 42.0.0 (10-Year Future-Proof Edition)
 * @collaboration: AI Research Team, Vector Database Engineers
 * @valuation: $2B+ core technology
 * ============================================================================
 */

/*
 * WILSY OS: NEURAL PRECEDENT SCHEMA
 *
 * Defines the 768-dimensional vector space for Legal-BERT embeddings.
 * This schema enables semantic search, precedent similarity, and
 * AI-powered legal reasoning.
 */
export const PrecedentCollectionSchema = {
  // Collection name and description
  name: 'wilsy_precedent_index',
  description:
    'Forensic Semantic Index for Universal Legal Precedents - Wilsy OS Neural Knowledge Base',

  // Collection fields definition
  fields: [
    {
      name: 'precedent_id',
      description: 'Primary Key - Unique identifier for each precedent',
      data_type: 'Int64',
      is_primary_key: true,
      auto_id: true,
      nullable: false,
    },
    {
      name: 'tenant_id',
      description: 'Tenant Isolation Key (Logical Partition) - Prevents cross-tenant data leakage',
      data_type: 'VarChar',
      max_length: 64,
      nullable: false,
      index: true,
    },
    {
      name: 'legal_vector',
      description: '768-Dimensional Legal-BERT Embedding - Semantic representation of legal text',
      data_type: 'FloatVector',
      dimension: 768, // Aligned with Legal-BERT model
      nullable: false,
    },
    {
      name: 'metadata',
      description: 'Rich metadata including citation, court, jurisdiction, and key principles',
      data_type: 'JSON',
      nullable: false,
    },
    {
      name: 'case_number',
      description: 'Official case number/citation for exact matching',
      data_type: 'VarChar',
      max_length: 64,
      nullable: false,
      index: true,
    },
    {
      name: 'court',
      description: 'Court name (e.g., Constitutional Court, Supreme Court of Appeal)',
      data_type: 'VarChar',
      max_length: 128,
      nullable: false,
      index: true,
    },
    {
      name: 'jurisdiction',
      description: 'Two-letter country code (ZA, UK, US, etc.)',
      data_type: 'VarChar',
      max_length: 2,
      nullable: false,
      index: true,
    },
    {
      name: 'decision_date',
      description: 'Unix timestamp of judgment date for temporal filtering',
      data_type: 'Int64',
      nullable: false,
      index: true,
    },
    {
      name: 'legal_areas',
      description: 'Array of legal areas (Constitutional Law, Contract Law, etc.)',
      data_type: 'Array<VarChar>',
      max_length: 64,
      nullable: true,
      index: true,
    },
    {
      name: 'citation_count',
      description: 'Number of times this precedent has been cited',
      data_type: 'Int32',
      nullable: false,
      default: 0,
      index: true,
    },
    {
      name: 'authority_score',
      description: 'Calculated authority score (0-100) based on citations and court hierarchy',
      data_type: 'Int8',
      nullable: false,
      default: 50,
      min: 0,
      max: 100,
      index: true,
    },
    {
      name: 'text_hash',
      description: 'SHA-256 hash of the original text for deduplication',
      data_type: 'VarChar',
      max_length: 64,
      nullable: false,
      index: true,
    },
    {
      name: 'created_at',
      description: 'Unix timestamp of when this entry was created',
      data_type: 'Int64',
      nullable: false,
      index: true,
    },
    {
      name: 'updated_at',
      description: 'Unix timestamp of last update',
      data_type: 'Int64',
      nullable: false,
      index: true,
    },
    {
      name: 'version',
      description: 'Schema version for future migrations',
      data_type: 'Int8',
      nullable: false,
      default: 1,
    },
  ],

  // Index configuration for vector search
  index: {
    field_name: 'legal_vector',
    index_type: 'IVF_FLAT', // Inverted File with Flat vectors - optimal balance of speed/accuracy
    metric_type: 'COSINE', // Cosine similarity works best for semantic legal search
    params: {
      nlist: 1024, // Number of cluster units (scales with collection size)
    },
  },

  // Partitioning strategy (for multi-tenant optimization)
  partitions: {
    enable: true,
    partition_key: 'tenant_id', // Each tenant gets its own partition for faster queries
    default_partitions: 16,
  },

  // Search configuration
  search_params: {
    default: {
      nprobe: 16, // Number of clusters to search (higher = more accurate but slower)
      metric_type: 'COSINE',
    },
    fast: {
      nprobe: 8, // Faster but slightly less accurate
      metric_type: 'COSINE',
    },
    accurate: {
      nprobe: 32, // More accurate but slower
      metric_type: 'COSINE',
    },
  },

  // Index maintenance
  maintenance: {
    auto_compact: true,
    compaction_interval: 3600, // 1 hour in seconds
    segment_size: 512, // MB per segment
    max_segments: 10,
  },

  // Consistency level
  consistency_level: 'Strong', // Ensure all replicas are consistent

  // TTL for data (if needed)
  ttl_seconds: 0, // 0 = no expiration
};

/*
 * Tenant-specific collection configuration
 * Each tenant can have custom indexing parameters based on their plan
 */
export const TenantCollectionConfig = {
  free: {
    ...PrecedentCollectionSchema,
    search_params: {
      nprobe: 8,
      metric_type: 'COSINE',
    },
    maintenance: {
      auto_compact: true,
      compaction_interval: 7200, // 2 hours
      segment_size: 256,
    },
  },
  basic: {
    ...PrecedentCollectionSchema,
    search_params: {
      nprobe: 16,
      metric_type: 'COSINE',
    },
    maintenance: {
      auto_compact: true,
      compaction_interval: 3600,
      segment_size: 512,
    },
  },
  professional: {
    ...PrecedentCollectionSchema,
    search_params: {
      nprobe: 32,
      metric_type: 'COSINE',
    },
    maintenance: {
      auto_compact: true,
      compaction_interval: 1800,
      segment_size: 1024,
    },
  },
  enterprise: {
    ...PrecedentCollectionSchema,
    search_params: {
      nprobe: 64,
      metric_type: 'COSINE',
    },
    maintenance: {
      auto_compact: true,
      compaction_interval: 900,
      segment_size: 2048,
    },
  },
};

/*
 * Sample document structure for insertion
 */
export const SamplePrecedentDocument = {
  tenant_id: 'lawfirm-12345678',
  legal_vector: [], // 768-dimensional array
  metadata: {
    citation: '[2023] ZACC 15',
    case_name: 'Smith v Jones',
    court: 'Constitutional Court',
    jurisdiction: 'ZA',
    decision_date: '2023-05-15',
    ratio: 'The principle of legality requires...',
    holdings: ['Holding 1', 'Holding 2'],
    keywords: ['legality', 'administrative law'],
    legal_areas: ['Constitutional Law', 'Administrative Law'],
  },
  case_number: '[2023] ZACC 15',
  court: 'Constitutional Court',
  jurisdiction: 'ZA',
  decision_date: 1684166400, // Unix timestamp
  legal_areas: ['Constitutional Law', 'Administrative Law'],
  citation_count: 25,
  authority_score: 95,
  text_hash: 'sha256hash...',
  created_at: Date.now() / 1000,
  updated_at: Date.now() / 1000,
  version: 1,
};

/*
 * Query templates for common search patterns
 */
export const QueryTemplates = {
  /*
   * Semantic search by legal principle
   */
  semanticSearch: (queryVector, tenantId, limit = 10) => ({
    vector: queryVector,
    anns_field: 'legal_vector',
    params: {
      metric_type: 'COSINE',
      params: { nprobe: 16 },
    },
    limit,
    expr: `tenant_id == "${tenantId}"`,
  }),

  /*
   * Hybrid search with metadata filters
   */
  hybridSearch: (queryVector, filters, tenantId, limit = 10) => ({
    vector: queryVector,
    anns_field: 'legal_vector',
    params: {
      metric_type: 'COSINE',
      params: { nprobe: 16 },
    },
    limit,
    expr: buildFilterExpression(filters, tenantId),
  }),

  /*
   * Get similar precedents by ID
   */
  similarPrecedents: (precedentId, tenantId, limit = 10) => ({
    // This would first get the vector for the precedent, then search
    anns_field: 'legal_vector',
    params: {
      metric_type: 'COSINE',
      params: { nprobe: 16 },
    },
    limit,
    expr: `tenant_id == "${tenantId}" && precedent_id != ${precedentId}`,
  }),

  /*
   * Get precedents by court and date range
   */
  courtAndDateRange: (court, startDate, endDate, tenantId, limit = 100) => ({
    expr: `tenant_id == "${tenantId}" && court == "${court}" && decision_date >= ${startDate} && decision_date <= ${endDate}`,
    limit,
  }),

  /*
   * Get most cited precedents
   */
  mostCited: (tenantId, limit = 50) => ({
    expr: `tenant_id == "${tenantId}"`,
    sort: 'citation_count',
    limit,
  }),

  /*
   * Get trending precedents (recent + high citation velocity)
   */
  trending: (tenantId, days = 30, limit = 20) => ({
    expr: `tenant_id == "${tenantId}" && decision_date >= ${Date.now() / 1000 - days * 86400}`,
    sort: 'citation_count',
    limit,
  }),
};

/*
 * Build filter expression for hybrid search
 */
function buildFilterExpression(filters, tenantId) {
  const conditions = [`tenant_id == "${tenantId}"`];

  if (filters.court) {
    conditions.push(`court == "${filters.court}"`);
  }

  if (filters.jurisdiction) {
    conditions.push(`jurisdiction == "${filters.jurisdiction}"`);
  }

  if (filters.startDate) {
    conditions.push(`decision_date >= ${filters.startDate}`);
  }

  if (filters.endDate) {
    conditions.push(`decision_date <= ${filters.endDate}`);
  }

  if (filters.minAuthority) {
    conditions.push(`authority_score >= ${filters.minAuthority}`);
  }

  if (filters.legalAreas && filters.legalAreas.length > 0) {
    const areaConditions = filters.legalAreas.map((area) => `legal_areas contains "${area}"`);
    conditions.push(`(${areaConditions.join(' || ')})`);
  }

  return conditions.join(' && ');
}

/*
 * Collection creation script
 */
export const createCollectionScript = `
-- Create collection
CREATE COLLECTION wilsy_precedent_index (
  precedent_id INT64 PRIMARY KEY AUTO_INCREMENT,
  tenant_id VARCHAR(64) NOT NULL,
  legal_vector FLOAT_VECTOR[768] NOT NULL,
  metadata JSON NOT NULL,
  case_number VARCHAR(64) NOT NULL,
  court VARCHAR(128) NOT NULL,
  jurisdiction VARCHAR(2) NOT NULL,
  decision_date INT64 NOT NULL,
  legal_areas ARRAY<VARCHAR(64)>,
  citation_count INT32 DEFAULT 0,
  authority_score INT8 DEFAULT 50,
  text_hash VARCHAR(64) NOT NULL,
  created_at INT64 NOT NULL,
  updated_at INT64 NOT NULL,
  version INT8 DEFAULT 1,
  INDEX idx_tenant (tenant_id),
  INDEX idx_court (court),
  INDEX idx_jurisdiction (jurisdiction),
  INDEX idx_date (decision_date),
  INDEX idx_legal_areas (legal_areas),
  INDEX idx_citation_count (citation_count),
  INDEX idx_authority (authority_score)
);

-- Create vector index
CREATE INDEX idx_vector ON wilsy_precedent_index(legal_vector) 
USING IVF_FLAT WITH (nlist=1024, metric_type=COSINE);

-- Partition by tenant
ALTER COLLECTION wilsy_precedent_index PARTITION BY tenant_id;
`;

export default {
  PrecedentCollectionSchema,
  TenantCollectionConfig,
  SamplePrecedentDocument,
  QueryTemplates,
  createCollectionScript,
};

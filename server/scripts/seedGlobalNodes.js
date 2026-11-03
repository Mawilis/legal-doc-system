/**
 * Legacy global-node seeding is retired.
 * The historical implementation deleted records and recreated a synthetic
 * WILSY_ROOT master node. EOS infrastructure must be provisioned by governed
 * infrastructure workflows, never by a tenant-scoped seeder.
 */
export const seedGlobalNodes = async () => {
  const error = new Error('EOS_GLOBAL_NODE_SEEDER_RETIRED');
  error.code = 'EOS_GLOBAL_NODE_SEEDER_RETIRED';
  throw error;
};

export default seedGlobalNodes;

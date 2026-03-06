/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ USAGE EXAMPLE - QUANTUM TEST FORTRESS                                    ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import {
  setupTestDB,
  teardownTestDB,
  clearCollections,
  cleanupModels,
  createTransactionContext,
  measurePerformance,
  getQuantumState
} from './testDatabaseHelper.js';

import mongoose from 'mongoose';

/**
 * Example: Testing with Quantum Isolation
 */
async function exampleTestSuite() {
  try {
    // 1. Setup isolated test database
    const uri = await setupTestDB();
    console.log('🔌 Connected to:', uri);

    // 2. Define your models
    const userSchema = new mongoose.Schema({
      name: String,
      email: String,
      createdAt: { type: Date, default: Date.now }
    });

    const User = mongoose.model('User', userSchema);

    // 3. Use transaction for atomic operations
    const transaction = createTransactionContext();
    await transaction.start();

    try {
      // 4. Measure performance
      const users = await measurePerformance(async () => {
        return User.create([
          { name: 'Alice', email: 'alice@wilsy.io' },
          { name: 'Bob', email: 'bob@wilsy.io' }
        ]);
      }, 'createUsers');

      console.log('👥 Created users:', users.length);

      // 5. Commit transaction
      await transaction.commit();
      console.log('✅ Transaction committed');

      // 6. Query with isolation
      const count = await User.countDocuments();
      console.log('📊 Total users:', count);

      // 7. Clear collections (clean slate)
      await clearCollections();
      
      const afterClear = await User.countDocuments();
      console.log('🧹 After clear:', afterClear);

      // 8. Get quantum state summary
      const state = getQuantumState();
      console.log('🔍 Quantum State:', JSON.stringify(state, null, 2));

    } catch (error) {
      await transaction.rollback();
      console.error('❌ Transaction failed:', error);
      throw error;
    }

    // 9. Cleanup models (prevent index conflicts)
    await cleanupModels(['User']);

    // 10. Teardown database
    await teardownTestDB();

  } catch (error) {
    console.error('💥 Test suite failed:', error);
    process.exit(1);
  }
}

// Run the example
exampleTestSuite();

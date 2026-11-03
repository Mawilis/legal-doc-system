/**
 * Legacy root/master tenant seeding has been retired.
 *
 * EOS now has one canonical tenant identity. This historical script used to
 * create five synthetic tenant_configs records and delete/recreate associated
 * node records. It must never run against an operational database.
 *
 * System authority and infrastructure topology must be represented by their
 * dedicated EOS registries, not tenant-shaped aliases.
 */

console.error(
  '[EOS] LEGACY_ROOT_ALIAS_SEEDER_RETIRED: use governed EOS system-authority and canonical tenant provisioning workflows.'
);
process.exitCode = 1;

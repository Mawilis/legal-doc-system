/**
 * Retired legacy Node scheduler.
 * Statutory, financial, and compliance work is owned by Kennel EOS durable
 * workers and schedulers under tools/eos/runtime.
 *
 * No Redis, MongoDB, timer, cron, or worker connections are created here.
 */
const retiredScheduler = Object.freeze({
  start: async () => {
    throw new Error("LEGACY_NODE_SCHEDULER_RETIRED_USE_KENNEL_EOS");
  },
});

export default retiredScheduler;

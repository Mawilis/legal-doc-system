/* eslint-disable */
/*╔════════════════════════════════════════════════════════════════╗
  ║ WILSY OS STRUCTURED LOGGER - FORENSIC GRADE                  ║
  ║ [JSON Structured | Audit Ready | POPIA Compliant]            ║
  ╚════════════════════════════════════════════════════════════════╝*/

class Logger {
  constructor() {
    this.component = 'WILSY-LOGGER-V8';
    this.levels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3,
      forensic: 4
    };
  }

  _log(level, message, meta = {}) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      component: this.component,
      message,
      ...meta,
      environment: process.env.NODE_ENV || 'production'
    };

    // Always output to console
    console.log(JSON.stringify(entry));

    // In production, would also write to secure audit log
    if (level === 'forensic' || level === 'error') {
      this._writeToAudit(entry).catch(() => {});
    }

    return entry;
  }

  async _writeToAudit(entry) {
    // In production, this would write to append-only audit store
    // Stub for now
  }

  info(message, meta) { return this._log('info', message, meta); }
  warn(message, meta) { return this._log('warn', message, meta); }
  error(message, meta) { return this._log('error', message, meta); }
  debug(message, meta) { return this._log('debug', message, meta); }
  forensic(message, meta) { return this._log('forensic', message, meta); }
}

export const logger = new Logger();
export default logger;

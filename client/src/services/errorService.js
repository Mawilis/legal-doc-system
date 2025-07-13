import * as Sentry from '@sentry/react';

Sentry.init({ dsn: process.env.REACT_APP_SENTRY_DSN });

export default Sentry;

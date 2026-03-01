#!import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '1m', target: 100 }, // ramp up to 100 users
    { duration: '3m', target: 500 }, // stay at 500 users
    { duration: '1m', target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<100'], // 95% of requests must complete below 100ms
    errors: ['rate<0.01'], // error rate must be below 1%
  },
};

export default function () {
  const url = `${__ENV.TARGET_URL}/api/predict/analyze`;

  const payload = JSON.stringify({
    template: {
      templateId: `test-${Math.floor(Math.random() * 1000)}`,
      practiceArea: 'corporate',
      jurisdiction: 'ZA',
      content: { raw: 'Test content' },
    },
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: '30s',
  };

  const res = http.post(url, payload, params);

  const success = check(res, {
    'status is 202': (r) => r.status === 202,
    'response time < 100ms': (r) => r.timings.duration < 100,
  });

  errorRate.add(!success);

  sleep(1);
}

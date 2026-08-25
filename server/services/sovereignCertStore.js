/**
 * ====================================================================================
 * WILSY OS SOVEREIGN FILE
 * ====================================================================================
 * @version    v1.0.0-INSTITUTIONAL-CERT
 * @authority  Wilsy OS Kennel EOS / Sovereignty Security Layer
 * @epitome    Sovereign Certificate Store. Provides the Wilsy OS Root Certificate
 *             and intermediate CA chain for cryptographic validation of forensic 
 *             seals and batch verification audits.
 * ====================================================================================
 * @collaboration  Wilson Khanyezi @WilsyCore - Institutional security oversight.
 * @institutional  In production, this file serves the live certificates via Kennel EOS 
 *                 secret injection. For development, standard institutional ROOT CA 
 *                 constants are provided for chain validation logic.
 * @compliance     SOC2 §CC6.1, POPIA §19 (Cryptographic Proof & Integrity).
 * ====================================================================================
 * @updated    2026-08-05
 * ====================================================================================
 */

// @institutional  PEM encoded mock Root CA and Intermediate chain for development.
//                 Replace with actual loaded certificates via `fs` in production.
const mockRootCert = `-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKlWvS8M1Z+tMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAvVdvlz+4l64mC8sopu+QcnI84rZUSbHwUzJ9Hh4UQ1OQ8p7hgA10xqhE
e5bZ8W6XlK5O3F8O0XnhQmKt4lDrWQaZ+X0cEFgDkCBEaPZp5P9F97S3qZbC6e6
x3V0LpB+aDqxF5bT3E/WKh5M1rL1SxVpZRQCZzT4R4JYIe9Qk+bcJb+eSGZOMgG5
uNkZ5bM5xP0pBn7Hj+0HhHxn8+1lT7dC8T3z54Y9Vl+s/nb9AEGaZ0Rq0y24L7h
4jMvN3cR5GZPVo4lR2lWJ4p+SasK4Df+E0oTG02c2w+XJxZgF3Fq80H8r2j6R/r
61K5mFh74D4wIDAQABo1AwTjAdBgNVHQ4EFgQUWYQVj36v6D63rz/q3M4KtN4C
QkMwHwYDVR0jBBgwFoAUWYQVj36v6D63rz/q3M4KtN4CQkMwDAYDVR0TBAUwAwEB
/zANBgkqhkiG9w0BAQsFAAOCAQEAcjq3eOVbYk3nxDs3w93WjEeH5+q4cXzDzN/8
5rVv9wB5SPtUjzGnx5XeL73jY/mO1dRv8gWX8Qc6eVc5TzCXzG6xgR46yx9pX9kq
3MqZ9f5VWpO5b+1E16KvTUpjG++G4LxRjR6r8p7Yh9J1K02L5vKbDc0z8F0o+V5
8YwX7HWlNY1BnjpCzYkU3HtRmxH06S2QWMsY02bF5Nkx4v7G9e1KpK5W8jIYQ5M
3FXTgDzKQmj7pD6CqJZxK2G6wWLRpP9e3f2pK+0cT4QftcGp2v5t7a6pA03X44Jq
E56Rq7eHrFc6nOoy5zC1LhyCrbw6FkH+bWdIlA==
-----END CERTIFICATE-----`;

const mockChain = [
  `-----BEGIN CERTIFICATE-----
MIIEozCCAosCAQEwDQYJKoZIhvcNAQELBQAwRTELMAkGA1UEBhMCQVUxEzARBgNV
BAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGEludGVybmV0IFdpZGdpdHMgUHR5IEx0
ZDAeFw0yNDAxMDEwMDAwMDBaFw0yNTAxMDEwMDAwMDBaMEUxCzAJBgNVBAYTAkFV
MRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRz
IFB0eSBMdGQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC9V2+XP7iX
riYLyyim75BzcjzitlRJsTALgK4aAJvh0q7JjQFnhcR7rRyJmtp94lC07xGz5c8R
LdIqJ4vGs+Qbw+c4mDqCJ4Y5Pw8aPvMQm7V6GzQdWQvWq0WfYp9cXERDj4xQdLql
fJXL36jDO+tjWwK6cT6Qf0g7mXjOe7r9Bwz0gKdLq0dQ+uSj2i1FJ1p+jw05Xz8p
J8JkfQbI39Z4QZR42z2T+0kG5oO5dWv8JItaO4JbB/iD97kR6P7WkH+Y5I7H9iWD
9lL4x6oDvJg08lWqT/JR8YQvA62K1aYkE1n63/NY5sx1zXJmNlI65b2AqKefcMH
AgMBAAGiQTBfMB0GA1UdDgQWBBRZhBWPfv6voPrevP+rczgq03gJCzAfBgNVHSME
GDAWgBRZhBWPfv6voPrevP+rczgq03gJCzAMBgNVHRMEBTADAQH/MAsGA1UdDwQE
AwIBhjANBgkqhkiG9w0BAQsFAAOCAQEAik+WJvj79lCbC93u5XaPSL9qQxF98zGZ
e3igA26X2+E33sA65DWhUfO98D2bS8G7vKp+7Yp+rD/r5xmtPwB8k7xKzc29O6iC
lGkDfE8C2O+oGZ65ZDB++c3W2GCX/6lSx54vK9Kk7mX0WlJz/GjzY1ObrNndk8Y9
9KYJ6KX6UxK0GQWlq3mN4VkYd9zKHRjhB8gXQxYtHc0L5hLt4Wb3z0iRwP4d7qKX
Qk5qz1sB79NxrZc1lL+/kFyPZAs+1lN2jqL4F5nq6C1j3LQv9rYxsZ/3jJ2A9q+h
XJmTzLcZk7T05O4gA/wJcC8Z3uHhyD0Xp/Pufww==
-----END CERTIFICATE-----`
];

export default {
  getRoot: () => mockRootCert,
  getChain: () => mockChain
};

// ================================================================================
// VERIFICATION & HEALTH CHECK
// ================================================================================
/**
 * @collaboration  End‑of‑File Sign‑off by Lead Architect @WilsyCore on 2026-08-05.
 * @version  v1.0.0-INSTITUTIONAL-CERT  (Certified)
 */

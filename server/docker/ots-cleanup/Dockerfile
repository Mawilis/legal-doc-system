# ==============================================================================
# WILSY OS - OTS CLEANUP SENTINEL CONTAINER
# Version: 2.1.0
# Build Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
# Security Level: SA-CSF (South Africa Cyber Security Framework) Compliant
# ==============================================================================

# STAGE 1: Builder - Secure Dependency Installation
# -------------------------------------------------
FROM node:18-alpine AS builder

# Security: Set non-root user from the start
RUN addgroup -g 1001 -S wilsy && \
    adduser -S wilsy -u 1001 -G wilsy

# Set secure working directory with proper permissions
WORKDIR /usr/src/app

# Install system dependencies for security scanning
RUN apk add --no-cache \
    tini=0.19.0-r1 \
    su-exec=0.2-r2 \
    && apk add --no-cache --virtual .build-deps \
    python3=3.10.12-r0 \
    make=4.3-r1 \
    g++=12.2.1_git20220924-r4

# Copy package files with proper ownership
COPY --chown=wilsy:wilsy server/package*.json ./

# Security: Install dependencies with audit and production-only flags
USER wilsy
RUN npm ci --only=production --audit --fund=false \
    && npm cache clean --force

# Security: Remove build dependencies
USER root
RUN apk del .build-deps \
    && rm -rf /var/cache/apk/*

# STAGE 2: Production - Minimal Secure Image
# ------------------------------------------
FROM node:18-alpine AS production

# Security: Metadata labels for compliance tracking
LABEL org.opencontainers.image.title="Wilsy OS OTS Cleanup Sentinel" \
    org.opencontainers.image.description="Secure container for timestamp proof cache maintenance" \
    org.opencontainers.image.version="2.1.0" \
    org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    org.opencontainers.image.authors="Wilson Khanyezi <wilsy.wk@gmail.com>" \
    org.opencontainers.image.licenses="Proprietary" \
    org.opencontainers.image.source="https://github.com/wilsonkhanyezi/wilsy-os" \
    org.opencontainers.image.vendor="Wilsy Legal Tech (Pty) Ltd" \
    com.wilsy.security.profile="SA-CSF-3" \
    com.wilsy.compliance.popia="true" \
    com.wilsy.compliance.companies-act="true"

# Security: Create non-root user with specific UID/GID
RUN addgroup -g 1001 -S wilsy && \
    adduser -S wilsy -u 1001 -G wilsy && \
    mkdir -p /usr/src/app && \
    chown -R wilsy:wilsy /usr/src/app

# Install security essentials
RUN apk add --no-cache \
    tini=0.19.0-r1 \
    su-exec=0.2-r2 \
    libcap=2.68-r1 \
    && setcap 'cap_net_bind_service=+ep' /usr/local/bin/node

# Security: Set secure defaults
ENV NODE_ENV=production \
    OTS_CACHE_DIR=/var/lib/wilsy/ots-cache \
    OTS_MAX_AGE_DAYS=30 \
    OTS_RETENTION_DAYS=365 \
    TZ=Africa/Johannesburg \
    NODE_OPTIONS="--max-old-space-size=512 --enable-source-maps --unhandled-rejections=strict"

# Security: Create secure directories with proper permissions
RUN mkdir -p /var/lib/wilsy/ots-cache \
    /var/lib/wilsy/ots-cache/.trash \
    /var/log/wilsy \
    /usr/src/app/logs \
    && chown -R wilsy:wilsy /var/lib/wilsy \
    /var/log/wilsy \
    /usr/src/app \
    && chmod 750 /var/lib/wilsy \
    /var/log/wilsy \
    && chmod 770 /var/lib/wilsy/ots-cache \
    /var/lib/wilsy/ots-cache/.trash

WORKDIR /usr/src/app

# Copy installed dependencies from builder
COPY --from=builder --chown=wilsy:wilsy /usr/src/app/node_modules ./node_modules

# Security: Copy only necessary files with strict permissions
COPY --chown=wilsy:wilsy server/scripts/ots-cleanup.js ./scripts/
COPY --chown=wilsy:wilsy server/lib/ots.js ./lib/
COPY --chown=wilsy:wilsy server/config/logger.js ./config/
COPY --chown=wilsy:wilsy server/models/AuditLedger.js ./models/
COPY --chown=wilsy:wilsy server/package.json ./

# Security: Create health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('fs').accessSync('/tmp/.healthcheck', fs.constants.F_OK);" || exit 1

# Security: Switch to non-root user
USER wilsy

# Security: Create entrypoint with proper signal handling
ENTRYPOINT ["/sbin/tini", "--", "su-exec", "wilsy"]

# Default command (override in Kubernetes CronJob)
CMD ["node", "scripts/ots-cleanup.js"]

# Security: Expose no ports (internal service only)
# Security: Run as non-root user (uid=1001)
# Security: Read-only root filesystem (mount volumes as needed)
# Security: Set resource limits via Docker/K8s

# ==============================================================================
# BUILD & DEPLOYMENT NOTES
# ==============================================================================
# Build Command:
#   docker build -t wilsy/ots-cleanup:2.1.0 -f docker/ots-cleanup/Dockerfile .
#
# Security Scan:
#   docker scan wilsy/ots-cleanup:2.1.0
#
# Run Locally:
#   docker run --rm \
#     -e MONGO_URI="mongodb+srv://wilsonkhanyezi:***********@legaldocsystem.knucgy2.mongodb.net/wilsy?retryWrites=true&w=majority&appName=legalDocSystem" \
#     -e DRY_RUN="true" \
#     -v /tmp/wilsy-ots-cache:/var/lib/wilsy/ots-cache \
#     wilsy/ots-cleanup:2.1.0
#
# Kubernetes CronJob Example:
#   apiVersion: batch/v1
#   kind: CronJob
#   metadata:
#     name: wilsy-ots-cleanup
#   spec:
#     schedule: "0 2 * * *"  # Daily at 02:00 SAST
#     jobTemplate:
#       spec:
#         template:
#           spec:
#             securityContext:
#               runAsUser: 1001
#               runAsGroup: 1001
#               fsGroup: 1001
#             containers:
#             - name: ots-cleanup
#               image: wilsy/ots-cleanup:2.1.0
#               env:
#               - name: MONGO_URI
#                 valueFrom:
#                   secretKeyRef:
#                     name: wilsy-secrets
#                     key: mongo-uri
#               - name: OTS_MAX_AGE_DAYS
#                 value: "30"
#               volumeMounts:
#               - name: ots-cache
#                 mountPath: /var/lib/wilsy/ots-cache
#             restartPolicy: Never
# ==============================================================================

# Mermaid Diagram: Container Security Layers
# 
# @mermaid
# flowchart TD
#     subgraph "Container Security Stack"
#         A[Host Kernel] --> B[Namespaces & Cgroups]
#         B --> C[Docker Runtime]
#         C --> D[Alpine Linux Base]
#         D --> E[Node.js 18 LTS]
#         E --> F[Non-Root User wilsy]
#         F --> G[AppArmor/SELinux Profile]
#         G --> H[Read-Only Root FS]
#         H --> I[Capabilities Dropped]
#         I --> J[Seccomp BPF Filter]
#         J --> K[Health Checks]
#         K --> L[Resource Limits]
#     end
#     
#     subgraph "Application Security"
#         M[Tini Init System] --> N[Su-Exec]
#         N --> O[Audit Logging]
#         O --> P[Tenant Isolation]
#         P --> Q[Secure Env Vars]
#         Q --> R[File Permissions]
#     end
#     
#     L --> M
#     R --> S[✓ Secure Execution]
#     
#     style S fill:#e1f5e1
#     style A fill:#f0f8ff
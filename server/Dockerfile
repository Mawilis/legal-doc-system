# WILSY OS 2050 - Quantum Production Dockerfile
# Version: 10.0.1-quantum-2050 [RECTIFIED: SHIELD INTEGRATION]

FROM node:20-alpine AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++ git

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY .env* ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Production stage
FROM node:20-alpine

# Install runtime dependencies
RUN apk add --no-cache tini curl

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy from builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .

# Create necessary directories
RUN mkdir -p /var/log/wilsy-os && \
    mkdir -p /app/data/forensic && \
    mkdir -p /app/reports && \
    chown -R nodejs:nodejs /var/log/wilsy-os /app/data /app/reports

# Switch to non-root user
USER nodejs

# 🛡️ RECTIFIED: Aligning Port to Wilsy OS Standard (4000)
ENV PORT=4000
EXPOSE 4000

# 🛡️ RECTIFIED: Health check now monitors the correct port
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:4000/health || exit 1

# Use tini as init
ENTRYPOINT ["/sbin/tini", "--"]

# 🛡️ RECTIFIED: Enforcing the Preload Shield
CMD ["node", "--import", "./preload-shield.js", "server.js"]

# WILSY OS 2050 - Quantum Production Dockerfile
# Version: 10.0.0-quantum-2050

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

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Use tini as init
ENTRYPOINT ["/sbin/tini", "--"]

# Start the server
CMD ["node", "server.js"]

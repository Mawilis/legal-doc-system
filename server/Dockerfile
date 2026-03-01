# ============================================================================
# WILSY OS v3.0 - PRODUCTION DOCKERFILE
# Multi-stage build | Security-hardened | Optimized for scale
# ============================================================================

# Stage 1: Builder - Install dependencies and build native modules
FROM node:20-slim AS builder

WORKDIR /build

# Install build essentials for native modules
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including dev for building)
RUN npm ci

# Stage 2: Dependency layer - Only production dependencies
FROM node:20-slim AS deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ONLY production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Stage 3: Runtime - Final production image
FROM gcr.io/distroless/nodejs20-debian12 AS runtime

# Create non-root user
USER nonroot:nonroot

WORKDIR /app

# Copy production dependencies
COPY --from=deps --chown=nonroot:nonroot /app/node_modules ./node_modules

# Copy application code
COPY --chown=nonroot:nonroot . .

# Create snapshots directory with proper permissions
RUN mkdir -p /app/snapshots

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["node", "/app/scripts/healthcheck.js"]

# Expose application port
EXPOSE 4000

# Set production environment
ENV NODE_ENV=production
ENV PORT=4000

# Run the application
CMD ["/app/server.js"]

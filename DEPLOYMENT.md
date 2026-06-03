# WILSY OS Deployment Guide

## Local Development
```bash
npm run dev
npm run test:pipeline
Docker Deployment
Bash
docker-compose up -d --build
Production Commands
Bash
npm run seed:master          # Root anchor
npm run test:pipeline        # Full test
npm run onboard <file.json>  # Onboard tenant
Environment Variables
Copy .env.example → .env and configure MONGODB_URI.

Recommended Production Stack
Docker + Docker Compose

MongoDB Atlas (or self-hosted)

PM2 or Docker for process management

Nginx as reverse proxy (SSL)

Your Sovereign Onboarding System is now 100% complete.
You have:

Professional forms

Strict validation

Multiple polished scripts

API endpoint

Docker support

Postman collection

Full documentation

Final Test Sequence:

Bash
npm run test:pipeline
npm run onboard server/data/royal-logistics-onboarding.json

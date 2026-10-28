# ==============================================================================
# WILSY OS — PYTHON EOS API CONTAINER
#
# TITLE: Python EOS API Container
# VERSION: v1.0.0-PYTHON-EOS-API
# AUTHORITY: Wilsy OS Core Governance
# EPITOME: Minimal non-root container for the canonical Python EOS ASGI API.
# ABSOLUTE CANONICAL PATH: Dockerfile
# COLLABORATION / OWNERSHIP: Python EOS, pinned requirements, Uvicorn.
# CERTIFICATION / UPDATE DATE: 2026-10-27
# CHANGELOG: v1.0.0 replaces the obsolete Node 14 / npm start container with
#            the Python EOS application on port 9095.
# SECURITY / PRIVACY POSTURE: No secrets or production database URI is baked in.
# TENANT BOUNDARY: Tenant admission remains in canonical Python EOS authorities.
# AUTHORITY BOUNDARY: Container runtime only; no IAM, legal, or financial authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# FAIL-CLOSED POSTURE: Runtime configuration is supplied by deployment controls.
# ==============================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    WILSY_ENV=production

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --requirement /app/requirements.txt \
    && groupadd --system --gid 10001 wilsy \
    && useradd --system --uid 10001 --gid 10001 --home-dir /nonexistent --shell /usr/sbin/nologin wilsy

COPY --chown=10001:10001 tools /app/tools

USER 10001:10001
EXPOSE 9095

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:9095/', timeout=3); raise SystemExit(0 if r.status == 200 else 1)"]

CMD ["python", "-m", "uvicorn", "tools.eos.api.server:app", "--host", "0.0.0.0", "--port", "9095"]

# ARTIFACT: Dockerfile
# VERSION: v1.0.0-PYTHON-EOS-API
# AUTHORITY BOUNDARY: Python EOS runtime only.
# FAIL-CLOSED POSTURE: No production database credentials are baked into image.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT

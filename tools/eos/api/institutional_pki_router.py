"""Public, read-only CRL distribution endpoint for the EOS private PKI."""
from __future__ import annotations

from hashlib import sha256

from fastapi import APIRouter, HTTPException, Request, Response

from tools.eos.security.institutional_pki import InstitutionalPKIError, InstitutionalPKIVerifier

router = APIRouter(prefix="/security/pki", tags=["institutional-pki"])


@router.get("/crl/{issuer_subject_sha256}", include_in_schema=False)
def get_institutional_crl(issuer_subject_sha256: str, request: Request) -> Response:
    """Publish only a CRL already loaded and validated by canonical EOS startup."""
    if len(issuer_subject_sha256) != 64:
        raise HTTPException(status_code=404, detail="PKI_CRL_NOT_FOUND")
    verifier = getattr(request.app.state, "institutional_pki_verifier", None)
    if not isinstance(verifier, InstitutionalPKIVerifier):
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_REVOCATION_PUBLICATION_UNAVAILABLE")
    try:
        body = verifier.crl_der_for_issuer_subject_sha256(issuer_subject_sha256)
    except InstitutionalPKIError as error:
        if error.code == "INSTITUTIONAL_PKI_CRL_ISSUER_NOT_FOUND_OR_AMBIGUOUS":
            raise HTTPException(status_code=404, detail="PKI_CRL_NOT_FOUND") from error
        raise HTTPException(status_code=503, detail="INSTITUTIONAL_PKI_REVOCATION_PUBLICATION_UNAVAILABLE") from error
    etag = sha256(body).hexdigest()
    return Response(
        content=body,
        media_type="application/pkix-crl",
        headers={
            "ETag": f'"{etag}"',
            "Cache-Control": "public, max-age=300, must-revalidate",
            "X-Content-Type-Options": "nosniff",
        },
    )

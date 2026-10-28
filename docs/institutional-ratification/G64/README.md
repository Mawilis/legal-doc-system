# G64 Institutional Ratification Evidence — Staging Record

## Scope

This branch stages the SHA-256 manifest for the G64 institutional ratification document package. The manifest was obtained from the user's verified Library package dated 2026-10-28.

## Integrity evidence

The source archive `G64-GOT-CLEAN.zip` had SHA-256:

`8e5b819645ba843b41d8879cfe1e6874c4d1fa0332c173bd1cf7897cc8d725c5`

The manifest file had SHA-256:

`783e31525d41e0f4e85f8ceb5d20b260af2795f82524f2d176e44f715ac043f2`

All five assets listed in the manifest matched their hashes when checked against the extracted archive bytes in the review environment. These results establish package integrity, not signature authenticity or institutional authority.

## Package status

The five binary assets are present in this repository directory and have been
checked against `SHA256-MANIFEST-FINAL-ALIGNED.txt`. The source package and
manifest hashes are recorded above. Repository completeness is verified by
recomputing the listed hashes against the committed files.

The institutional package is recorded as approved by the user. This evidence
package records document and asset integrity; it does not independently certify
runtime access or production deployment.

## Release control

This branch does not authorize runtime enablement, Legal Operations access, production deployment, or removal of the Node PDF fallback. Keep affected operations fail-closed until the required evidence is completed and the approved authorization contract is implemented and certified.

## Manifest

See `SHA256-MANIFEST-FINAL-ALIGNED.txt`. Its hashes must be checked against the actual repository files after the binary transfer; do not infer a successful check from this staging record.

# Electrum PayShap onboarding and sandbox certification

## Status

The WILSY OS partner-side completion receiver is implemented against Electrum's
published Regulated Payments Partner API contract. The repository CI tests are
contract/conformance tests, not proof of an actual Electrum sandbox handshake.
The worker remains opt-in and production settlement enforcement is not enabled.

## Supported inbound completion contract

- Route: `POST /providers/electrum/payshap/completion`
- Scheme: `ZA_RPP`
- Message schema: `PaymentStatusReport`
- Completion outcomes: `APPROVED`, `CANCELLED`, `PENDING`, `REJECTED`,
  `PARTIALLY_ACCEPTED`
- Final settlement is eligible only for `status.outcome == APPROVED`.
- UETR is read from `transactionIdentifiers.uetr`.
- The original request linkage is validated from `originalMessageIdentifiers`.
- Amount and currency are read from
  `originalTransactionData.amounts.bankSettlementAmount`.
- Creditor account correlation is based on a SHA-256 fingerprint of the stable
  `creditorAccount.identification` and/or `creditorAccount.proxy` locator.
  Raw account/proxy data is not persisted.
- Each completion is durably inserted into the inbox before acknowledgement.
- Electrum completion acknowledgement is HTTP 202 with an empty body and a
  signed `x-jwt-signature` header. The content-digest claim is omitted for an
  empty body as required by Electrum's HTTP message signing contract.
- Non-approved completion messages are durably retained and marked ignored;
  they never create settlement observations or invoice allocations.

## Provider contract references

This receiver follows the Electrum Regulated Payments Partner API
`PaymentStatusReport` schema and its inbound completion notification flow.
Electrum's partner API specifies an HTTP `202` acknowledgement with no
response content for the completion notification. All HTTP requests and
responses carry the `x-jwt-signature` header; ES256/P-256 is the supported
algorithm, and the content-digest claim is present only when a body exists.
The minimum TLS version is 1.2; mutual TLS is not supported. Partner-side
calls do not use the bank OIDC bearer-token mechanism described for
Electrum-side calls.

Official references:

- [Electrum Regulated Payments Partner API – PaymentStatusReport](https://docs.electrumsoftware.com/openapi/elpapi/elpapi-partner/schema/paymentstatusreport)
- [Electrum security](https://docs.electrumsoftware.com/epc/public/security)
- [Electrum HTTP message signing](https://docs.electrumsoftware.com/epc/public/http-message-signing)
- [Electrum PayShap partner-auth flow](https://docs.electrumsoftware.com/epc/public/payshap-partner-auth)

## Electrum onboarding exchange

Obtain these values directly through Electrum's approved onboarding channel:

1. The exact legal entity / merchant account being onboarded and its sponsor
   bank details.
2. The integration environment and partner API base URL for sandbox.
3. The payment-receive mode: auto-auth or partner-auth. This receiver handles
   final completion notifications. Partner-auth additionally requires the
   separate inbound credit-transfer authorisation request/response operations;
   do not select partner-auth until those operations are implemented and
   certified.
4. Electrum's ES256 public verification key(s) and corresponding `kid` values.
5. WILSY's onboarding-assigned issuer value and accepted WILSY key identifier.
6. WILSY's public ES256 key, exchanged through the approved channel.
7. Electrum's agreed callback URL, authentication/network allow-list
   requirements, response timeout, retry/SAF policy and reconciliation window.
8. The sponsor-bank-issued creditor account and approved PayShap receiving
   identifier(s), including any proxy namespace and account currency.

WILSY generates and retains its private ES256 key material. Generate it
outside the repository on a controlled workstation or approved key-management
host, then store the PKCS#8 private key only in the approved secret manager:

```sh
umask 077
openssl ecparam -name prime256v1 -genkey -noout -out electrum-wilsy-ec-key.pem
openssl pkcs8 -topk8 -inform PEM -in electrum-wilsy-ec-key.pem \
  -outform PEM -nocrypt -out electrum-wilsy-private-key-pkcs8.pem
openssl ec -in electrum-wilsy-private-key-pkcs8.pem -pubout \
  -out electrum-wilsy-public-key.pem
```

Exchange only the public key through Electrum's approved onboarding channel.
Never send a private key through chat, email, issue comments, or source
control. Store it only in the approved secret manager and expose it to the
runtime through the deployment's secret-injection mechanism.

## Runtime configuration

For this integration stage, set `WILSY_ELECTRUM_ENVIRONMENT=sandbox`. The receiver refuses to load transport keys unless this value is exactly `sandbox`; the worker also requires this sandbox gate plus explicit opt-in. Do not set the worker opt-in until Electrum has completed the sandbox handshake and the full end-to-end certification gate is green.

The receiver currently reads:

- `WILSY_ELECTRUM_VERIFICATION_KEYS_JSON`: JSON object mapping Electrum
  `kid` to PEM public keys.
- `WILSY_ELECTRUM_SIGNING_PRIVATE_KEY_PEM`: WILSY PKCS#8 ES256 private key.
- `WILSY_ELECTRUM_SIGNING_KEY_ID`: WILSY key ID registered with Electrum.
- `WILSY_ELECTRUM_SIGNING_ISSUER`: exact issuer value assigned during
  onboarding.
- `WILSY_ELECTRUM_SETTLEMENT_WORKER_ENABLED`: explicit opt-in for the inbox
  worker. Keep false until the sandbox certification gate is complete.

The receiving-account fingerprint must be provisioned in
`electrum_provider_account_bindings` and point to an approved destination
reference. The provider account binding does not assign a tenant. A completion
UETR must resolve to exactly one canonical platform execution truth; tenant,
invoice and destination correlation are then checked against that truth.

## Sandbox certification sequence

1. Confirm sandbox endpoint, TLS 1.2+, callback reachability and any IP
   allow-list requirements with Electrum.
2. Exchange public keys and issuer/key identifiers; verify key rotation using
   at least two concurrently trusted Electrum key IDs.
3. Keep the settlement worker disabled while exercising invalid signature,
   unknown key ID, stale `iat`, altered body, malformed schema, wrong scheme,
   missing original message identifiers and invalid UETR cases.
4. Verify a valid completion is durably inserted and answered with a signed,
   empty HTTP 202 response inside Electrum's agreed response deadline.
5. Verify exact delivery replay returns another signed empty 202 without a
   second inbox record or second allocation. Verify divergent message replay
   and duplicate UETR are rejected and raised for reconciliation.
6. Verify `CANCELLED`, `PENDING`, `REJECTED` and
   `PARTIALLY_ACCEPTED` completions are retained but never credited.
7. In an isolated sandbox tenant and disposable replica set, process one
   approved payment in partial, then final allocations. Verify the invoice
   remains partially paid until the balance reaches zero.
8. Interrupt processing at each transaction boundary; verify rollback and
   Electrum SAF redelivery recover without duplicate allocation, audit or
   outbox events.
9. Run concurrent duplicate deliveries and concurrent inbox workers; verify
   unique UETR, unique allocation and invoice revision guards.
10. Reconcile WILSY's resulting invoice allocation with the sponsor-bank /
    Electrum settlement evidence and daily mark-off output.

## Activation gate

Actual provider activation is blocked until Electrum supplies the onboarding
materials and performs the sandbox callback handshake. Passing repository CI
alone does not satisfy this gate. No production deployment, billing enforcement
or subscription lifecycle authority is enabled by this integration.

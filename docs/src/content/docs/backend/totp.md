---
title: "TOTP and recovery"
description: "Configure native second factors, pending sign-in and protected factor changes."
---

Use native TOTP when password sign-in must also require an authenticator code.
The workflow includes enrollment, browser-bound pending sign-in, single-use
recovery codes and protected factor replacement/removal. Authentication still
establishes identity only: keep membership, RBAC, tenant and ownership checks in
your application.

:::caution[Unreleased library workflow]
This guide describes the new `methods/totp` and `stores/postgres/totp` modules in
Pluto Auth's development workspace. They are **not** included in the published
versions shown by the [authentication reference](../auth/). Coordinated module
tags and an installation recipe are pending; do not assume `go get` of the
published password module installs this workflow. CLI scaffolding and frontend
MFA screens are not implemented by this library change. No deployment or
independent security audit is implied.
:::

## Configure

Before mounting handlers, provide:

- Go **1.25.5+** and a checkout/workspace containing the unreleased modules. Their
  local development replacements must become coordinated version pins before
  publishing or consuming a tagged release.
- PostgreSQL with `schema.sql`, then migrations **002, 003, 004 and 005** applied
  explicitly through application migration tooling. `005_totp.sql` creates the
  native-factor, recovery-digest and pending-challenge tables; it enrolls nobody
  and enables no account policy automatically. Constructors never run DDL.
- A host-managed authenticated-encryption boundary for seeds, real shared
  per-account attempt limits, and trusted-client ingress limits before KDF work.
- HTTPS, exact trusted Origins, verified password-lifecycle delivery, and a
  factor-change notification policy.

Use the **same** `totppostgres.Store` for password verification, factor completion
and all account-backed session issuance/rotation. Never issue those sessions
through the session-only `postgres.New` adapter.

### Wire password and factor services

This construction excerpt assumes a configured PostgreSQL pool implementing
`postgres.TransactionDB`; a `password.Hasher`; a `password.AttemptLimiter` shared
by all application instances; a real `password.Sender`; and an ingress middleware
that limits requests using a trusted client identity. `protector` implements
`totp.Protector`. `changed` handles committed security-change notifications.
Neither limiter nor delivery can be a production no-op.

```go
store, err := totppostgres.New(database)
if err != nil {
	return err
}

sessions := auth.DefaultConfig()
primary, err := password.NewService(
	ctx, store, hasher, limiter, sender, sessions,
	password.DefaultLifecycleConfig(),
)
if err != nil {
	return err
}

factors, err := totp.New(store, protector, limiter, totp.Config{
	Issuer:   "Your application",
	Sessions: sessions,
	Changed:  changed,
})
if err != nil {
	return err
}

handler, err := totphttp.New(factors, totphttp.Config{
	Transport: httpauth.Config{
		TrustedOrigins: []string{"https://app.example.com"},
	},
	Ingress: ingress,
	Primary: primary.BeginSignIn,
})
if err != nil {
	return err
}

mux.Handle("/api/factors/", http.StripPrefix("/api/factors", handler))
```

Imports are `context`/`net/http` as needed by the surrounding application, plus:

- `auth "github.com/plutoframework/pluto-auth"`
- `github.com/plutoframework/pluto-auth/httpauth`
- `github.com/plutoframework/pluto-auth/methods/password`
- `github.com/plutoframework/pluto-auth/methods/totp`
- `github.com/plutoframework/pluto-auth/methods/totp/totphttp`
- `totppostgres "github.com/plutoframework/pluto-auth/stores/postgres/totp"`

The complete constructor is maintained at
`stores/postgres/totp/examples/local/local.go` in the auth development workspace.
Mount the existing password adapter alongside it for enrollment, email
verification and password recovery. Use the factor handler's `Transport()` to
protect application routes, retaining application authorization checks. Existing
password-only sign-in rejects accounts that require a factor; it is not a bypass.

### Protect seeds and notify users

`totp.Protector` is an explicit host key-management boundary. Its authenticated
encryption must bind ciphertext to the subject and seed purpose. The included
`totp.NewAESProtector(activeKeyID, keys)` accepts a map of host-managed key IDs to
32-byte AES keys, uses AES-256-GCM, and retains old keys for decryption. New setup
uses the active key. Load keys from a secret manager, **not** from the credential
database. Keep backups, retain old keys during rotation, and give all instances
compatible keys. This helper does not provision or rotate your keys for you.
Existing seeds are never returned by the service.

Configure `Config.Changed` with signature
`func(context.Context, string, totp.Action)` to notify the owner through an
independently verified channel after a committed enrollment, replacement,
removal or code regeneration. It receives only subject and action, not secrets.
The host owns reliable/idempotent delivery and audit retention. Callback failure
cannot undo the committed change. Do not put raw codes, setup URIs, passwords or
request bodies into logs, analytics or plaintext notification outboxes.

## Sign in

For the mounting prefix above, send:

```http
POST /api/factors/begin
Origin: https://app.example.com
Content-Type: application/json

{"email":"alice@example.com","password":"…","action":"signin"}
```

A factor-required account receives `challenge` and `expires` JSON fields and a
`__Host-pluto_factor` cookie. That cookie is Secure, HttpOnly, SameSite=Strict,
Path=/, with no Domain and a five-minute maximum. **No regular session is issued.**
The challenge is not an authenticated session, bearer token or application
identity. A non-factor account signs in directly and receives the normal secure
session cookie instead, with `{"authenticated":true}` in the response.

Keep the pending challenge only in transient UI state. Submit an authenticator
code from the same browser:

```http
POST /api/factors/finish
Origin: https://app.example.com
Content-Type: application/json

{"challenge":"…","code":"123456","recovery":false}
```

The browser supplies the binding cookie; do not copy it into the request body.
Successful completion clears the pending cookie and sets the regular session
cookie. The JSON response never contains a raw session token. Both routes return
`Cache-Control: no-store`. They require exactly one trusted Origin, bounded JSON
and one unambiguous browser-binding cookie for completion. This design requires a
same-site frontend; do not loosen cookie settings for an unrelated site without
a separate reviewed browser design.

Wrong, expired, replayed or mismatched proofs return generic `401 invalid_proof`.
Factor limits return `429 request_limited`; storage/protection failures return
`503 authentication_unavailable`, without internal error details. Untrusted
Origins return 403. Treat ambiguous network failure after commit as uncertain:
start a new workflow rather than assuming a security change was rolled back.

### Library integration

`password.Service.BeginSignIn` verifies the password without creating a session.
Pass its **server-local** ceremony into `factors.Begin`, with a newly generated
`totp.Browser()` binding and `totp.SignIn`. Complete using
`Finish(ctx, challenge, browser, code, false, "")`. Never reconstruct a ceremony
from browser JSON or trust client-supplied method evidence or subject IDs.
Custom method adapters must verify primary credentials themselves.

Pending records bind purpose, account, browser digest, security version and the
original verification deadline. At most one pending record per account/action
is retained; starting another supersedes the old one. Schedule `Store.Prune` for
expired records and bound public account creation at ingress.

Completion atomically rechecks current account policy/version, consumes the
challenge and factor proof, and creates the session under the same account lock.
Reset, disable and factor changes use that fence too. Stored session evidence
retains the actual primary verification time and factor method/time. Rotation
preserves that evidence, credential version and absolute expiry; it is not fresh
authentication. Keep application and database clocks synchronized.

## Enroll and change factors

Every action starts at `/begin` with fresh primary credentials, less than five
minutes old. The challenge cannot extend their original deadline.

| Action | Existing-factor proof | New-seed confirmation | Committed effect |
| --- | --- | --- | --- |
| `enroll` | None; no factor or required-factor policy may already exist | Required | Install seed, require MFA, return 10 recovery codes |
| `replace` | Current TOTP or one recovery code | Required | Replace seed and recovery codes, require MFA |
| `regenerate` | Current TOTP or one recovery code | None | Replace all recovery codes, retain required MFA |
| `remove` | Current TOTP or one recovery code | None | Explicitly remove seed/codes and disable required MFA |

For enrollment/replacement, `/begin` returns a **new** `otpauth://` URI in `uri`.
Show it as a QR code/setup secret once, without logging, analytics or persistent
browser storage. The seed is encrypted in persistence but remains inactive until
confirmed. Existing seeds are never exposed. The HTTP adapter uses the verified
subject as its display label; library hosts can supply a server-selected label.

Submit the new authenticator's code in `confirmation` at `/finish`. Enrollment
needs that confirmation only. Replacement also needs the current factor's
`code`, or a recovery code with `recovery: true`. For example:

```json
{
  "challenge": "…",
  "code": "123456",
  "recovery": false,
  "confirmation": "654321"
}
```

A management result returns `recovery_codes` only when new codes are generated.
Display them once, then return the user to sign-in. Every committed factor change
advances the security version and atomically revokes affected sessions, password
challenges and pending factor challenges. A session alone or a password-reset
token cannot authorize factor replacement/removal. Already authorized in-flight
application requests are not cancelled.

`LocalStore.SetSecondFactorRequired` is a trusted server policy primitive, **not**
a public factor-management route. Never expose it to let users bypass proof.

## Recover access

Each recovery code has 256 random bits, encoded as canonical unpadded base64url.
Only subject/purpose-separated SHA-256 digests are stored. Instruct users to keep
codes offline or in a password manager: there is no retrieval API. Replacement
and regeneration invalidate every old code. If the response is lost after commit,
authenticate again and regenerate; a consumed challenge cannot redisplay codes.

A recovery code substitutes for the **existing factor only**, never the primary
password/provider proof. Start a fresh `/begin`, then send the chosen code with
`recovery: true` to `/finish`. Consumption commits atomically with the intended
sign-in or security change; parallel reuse fails. Wrong TOTP codes never silently
fall back to recovery.

Password reset retains required-factor policy, the encrypted seed, replay counter
and recovery codes. It revokes sessions and invalidates pending primary proof;
it does not downgrade MFA. Losing both the authenticator and all codes requires
a separately designed host recovery process, not an automatic email/support
bypass. Losing encryption keys likewise requires recovery proof to replace the
factor. Plan that policy and verified notifications before enabling MFA.

## Clock and storage limits

The verifier uses RFC 6238 SHA-1, six digits and 30-second periods, accepting only
the previous/current/next step. The highest accepted counter is stored globally
per factor, including enrollment confirmation, preventing reuse across challenges,
instances and actions. A just-used code cannot immediately sign in again; wait
for a new step or use recovery. Accepting a future step blocks earlier ones.
TOTP and recovery codes are not phishing-resistant authentication.

PostgreSQL is the supplied durable factor adapter; the session memory store is
not a native-factor store. A custom `totp.Store` must implement the entire atomic
contract, not consume a proof separately from session creation. Protect database
backups containing encrypted seeds and recovery digests, and enforce retention
policy. There is no support-recovery console or generated frontend enrollment UI
in this implementation.

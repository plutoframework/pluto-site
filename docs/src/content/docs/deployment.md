---
title: "Deployment & upgrades"
description: "Deployment & upgrades with Pluto."
---

Start from the generated application README and the requirements for each enabled adapter. Pluto provides primitives and scaffolding; deploying an app also requires application-specific delivery, ingress, permissions and operational policies.

## Before deployment

- Apply reviewed migrations explicitly, using a suitably restricted database role. Startup performs no DDL.
- Supply real credential delivery and shared attempt limits when using local credentials. Demo-only providers and loopback fixtures are development tools.
- Configure trusted origins, HTTPS, cookie behavior and trusted proxy ingress for your deployment.
- Provision required PostgreSQL, optional Valkey, worker processes and OTLP infrastructure.
- Keep secrets in your chosen secret provider. Generated fnox/mise files are starting configuration.

## Writes and background work

Keep business writes, audit records and outbox enqueue in one transaction. Run the worker separately and plan retention, retries and reconciliation. Jobs are delivered at least once, so external effects require idempotent handlers. A state-machine decision is only a proposed transition until the transaction commits.

Generic HTTP idempotency capture has a gap between business commit and replay completion. Use the same-transaction completion API when the operation needs atomic business/replay completion. Read [Core's guarantees](../backend/core/) before relying on retries.

## Upgrade deliberately

Pin module versions and commit Go/npm lockfiles. Updating the CLI does not rewrite existing authored code or silently migrate a frontend. Review the CLI reference's schema-specific migration instructions and the library's release notes.

For state scaffolding in an older application:

```sh
go get github.com/plutoframework/pluto-core@v0.4.0
pluto --no-input add state launches --dry-run
```

Run format, contract freshness, tests, fuzz/mutation checks relevant to your change and real database integration before shipping. The [purchasing example](../example/) shows a complete disposable development walkthrough.

## Documentation versions

This site currently publishes one current guide set. Every imported reference page links to an immutable repository revision. Historical behavior is available through source tags; separate versioned docs trees can be added when maintaining multiple supported framework versions becomes necessary.

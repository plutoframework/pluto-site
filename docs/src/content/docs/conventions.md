---
title: "Conventions & testing"
description: "Conventions & testing with Pluto."
---

Pluto favors visible wiring, readable Go and predictable locations. The CLI removes repetitive setup; application code owns the business decisions.

## Follow the request

1. **Paths** declare endpoint identity, method, path, permissions and feature metadata.
2. **Handlers** decode and validate HTTP input, obtain verified request context, call operations and map responses.
3. **Operations** authorize, load tenant-scoped resources, apply business rules and coordinate writes.
4. **Repositories** implement the persistence capabilities consumed by operations.

Use constructor injection and small consumer-owned interfaces. Keep HTTP and concrete database imports out of domain logic. Use application response models rather than exposing sqlc records directly.

## Configuration

`pluto.toml` describes tooling choices and generated contracts. Runtime configuration is loaded separately into a parent config struct with grouped settings. Environment variables use the app's saved uppercase prefix. Preserve explicit false values for flags; a missing override differs from false.

## Business lifecycles

Use [Core state](../backend/state/) when an entity has a meaningful lifecycle. Compile a definition once and inject it. `Next` evaluates a pure decision against a facts snapshot. Authorization and atomic persistence remain in the operation. Every update affecting guard facts must participate in the version/transaction scheme; facts from other rows may require locks or stronger isolation.

## Tests by responsibility

- Unit-test business rules independently of HTTP and the database.
- Test HTTP decoding, verified context extraction and response mapping separately.
- Fuzz untrusted decoders and lifecycle invariants with bounded runs.
- Use mutation checks to confirm that removing a guard or boundary makes tests fail.
- Run database integration tests against disposable services to verify constraints, concurrency, audit and outbox atomicity.

The lifecycle generator includes meaningful unit cases and a fuzz target. Package repositories also include bounded seeded mutation smoke scripts; these are targeted checks rather than a comprehensive mutation engine. Do not count skipped database tests as successful integration coverage.

## Readable source

Generated projects use an 80-column formatter target, expanded Go formatting and a 1,000-line source ceiling. `pluto fmt` applies the configured formatters and whitespace fixes. `pluto vet` checks the architecture and generated contracts along with Go checks. Split responsibilities across files rather than compacting code to meet the ceiling.

## Humans and agents

Use the wizard for discovery. Use deterministic raw commands with `--no-input` for automation. Generators preserve authored files and offer `--dry-run`. Existing generated contracts require intentional migrations when the manifest schema changes.

## Asynchronous feedback

Every action acknowledges immediately with accessible pending feedback, preserves
failed input and resolves to a clear outcome. Use published action primitives;
select optimism explicitly and test delayed responses, definite rejection,
uncertainty, concurrent actions and scope changes. See [responsive actions](../frontend/actions/).

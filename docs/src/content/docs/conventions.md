---
title: "Conventions & testing"
description: "Conventions & testing with Pluto."
---

Pluto favors visible wiring, readable Go and predictable locations. The CLI removes repetitive setup; application code owns the business decisions.

## Place code by responsibility

Read [application architecture](../architecture/) before adding business logic.
It defines presentation, entry adapters, application operations, domain rules,
data and infrastructure adapters, with composition kept explicit. It also
distinguishes the target boundaries from the checks implemented today.

Handlers translate protocols, operations coordinate use cases, domain packages
own business decisions, and adapters implement I/O. Use constructor injection and
small consumer-owned interfaces. Endpoint metadata and wire models are contracts,
not a home for business logic.

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

Go library maintainer commands (`make fmt` and `make vet`) enforce a blank line
before each standalone comment block unless it starts on file line one. This
also applies immediately inside a code block. Consecutive comment lines stay
together and attached to the code below; trailing inline comments and compiler
or linter directives retain their required placement. Generated Go and `testdata`
fixtures are excluded. The CLI repository uses `scripts/fmt.sh` and
`scripts/check.sh` for the same maintainer rule.

The maintainer formatter applies comment spacing after configured Go formatters.
The check compares that combined result because gofumpt otherwise removes blank
lines before comments at the start of a block. The linter runner selects the
configured semantic linters separately; the composed formatter owns leading
whitespace instead of wsl's conflicting block-start rule. Frontend uses its existing ESLint
comment-spacing rule. These maintainer commands do not change application
`pluto fmt` or `pluto vet` behavior.

## Humans and agents

Use the wizard for discovery. Use deterministic raw commands with `--no-input` for automation. Generators preserve authored files and offer `--dry-run`. Existing generated contracts require intentional migrations when the manifest schema changes.

## Asynchronous feedback

Every action acknowledges immediately with accessible pending feedback, preserves
failed input and resolves to a clear outcome. Use published action primitives;
select optimism explicitly and test delayed responses, definite rejection,
uncertainty, concurrent actions and scope changes. See [responsive actions](../frontend/actions/).

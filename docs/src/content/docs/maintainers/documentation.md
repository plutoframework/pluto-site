---
title: "Writing documentation"
description: "Author realistic, executable Pluto guides and examples."
---

Help readers build something with the published API. Use
[OpenCode's docs](https://opencode.ai/docs/) as the editorial reference;
write original Pluto instructions.

## Lead with real usage

- Show the actual primitive and application wiring before testing machinery.
- For integrations, use the real adapter: a model provider, HTTP client, database
  store or delivery implementation. State the required credentials and services.
- Keep identity, permissions, transactions and resource checks in the example.
  Do not bypass them to make the walkthrough shorter.
- Use local input data when it teaches the real algorithm: pagination over rows
  or a state transition needs no external service.
- Label partial snippets as excerpts and link complete, maintained source.
  Say which callbacks and application policies the reader must implement.
- Explain the observable result. Model-generated text varies; do not present
  canned output as evidence of inference or a printed message as delivery.

## Separate testing examples

- Put scripted providers, mock servers, deferred promises and fixture sessions
  under explicitly named testing sections, after the application example.
- Explain what a deterministic example proves and which integration it replaces.
- Keep tests deterministic. Exercise real adapters against controlled transports;
  a documentation build must not require a paid call or production credentials.
- Distinguish compilation, mocked integration checks and live-service validation.
  Report only what actually ran.

A local PostgreSQL instance exercises real persistence. A scripted model does
not exercise inference. Both can be valuable; the documentation must make the
boundary clear.

## Write the guide

- Open with what the feature does and when to use it.
- Put prerequisites before the step that needs them.
- Use short headings: Install, Configure, Usage, Options.
- Show a working command or configuration before edge cases.
- Explain results and generated paths immediately after each example.
- Use tables for flags and defaults; keep limitations actionable.
- Link deeper references instead of repeating implementation details.
- Identify supported versions and unfinished application wiring.
- Keep marketing language and space metaphors out of instructions.
- Follow repository formatting, including expanded code, the 80-column target
  and a blank line above standalone comment blocks except at file line one.

## Validate and publish

- Check commands against the pinned CLI and examples against published packages.
- Compile complete examples; keep copied snippets checked against their source.
- Run `python3 scripts/format-go-docs.py` with golangci-lint 2.15.0 on PATH.
  Use `--write` on owning source guides before refreshing snapshots. Complete
  source examples also pass their repository's gci and wsl checks.
- Run affected repository formatters, linters and documentation checks.
- Keep secrets out of source, logs, screenshots and generated artifacts.
- Edit reference snapshots in their owning package, publish the source revision,
  then run `python3 scripts/sync-docs.py` in the site repository.
- Build the site and run its checks before an authorized deployment.

## Agent readers

Keep concise guidance in [Pluto Skills](https://github.com/plutoframework/pluto-skills).
The `pluto-docs` skill points here; skills must not duplicate the manual.

Every topic is exported as `/docs/<slug>.md` from the same source as Starlight.
[docs/llms.txt](https://plutoframework.github.io/pluto-site/docs/llms.txt) lists the
exports. Maintain one manual and validate Markdown targets with
`python3 scripts/check-docs.py` after assembling the site.

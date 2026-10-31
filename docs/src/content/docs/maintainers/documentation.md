---
title: "Writing documentation"
description: "Author realistic, executable Pluto guides and examples."
---

Help readers build something with the published API. Use
[OpenCode's docs](https://opencode.ai/docs/) as the editorial reference;
write original Pluto instructions.

## Choose the destination before writing

Product documentation lives on the site. A change to public APIs, commands,
configuration, defaults, setup, supported integrations or observable behavior
must be reflected in the affected product pages as part of the same work.
Updating a package README alone does not complete that documentation work.
For an internal change with no reader-visible effect, no new prose is needed.

Inspect existing pages and `scripts/sync-docs.py` before choosing a destination:

| Content | Owning location |
| --- | --- |
| Product guides, workflows, configuration and troubleshooting | Existing topic under `pluto-site/docs/src/content/docs/` |
| Package reference that feeds a site snapshot | The source path listed in `pluto-site/scripts/sync-docs.py`; refresh the site snapshot afterward |
| Package introduction and quick start | Repository `README.md`; link deeper product docs |
| Contributor commands and repository constraints | Existing `CONTRIBUTING.md` or `AGENTS.md` |
| Runnable example | Source in the owning repository's established example directory; explain it in the relevant guide |
| Reusable agent decisions | The relevant skill; link the product manual for detail |
| Work plan, implementation summary, test evidence or handoff | Conversation, PR description or issue; no repository Markdown file by default |

Maintain one authoritative explanation for each topic. Link it from other
entrypoints instead of copying it. Package-owned reference sources are intentional
inputs to generated site pages; do not hand-edit those snapshots. Site-authored
pages are edited directly in the site repository. Markdown exports are generated
from those pages, not separately authored manuals.

## Keep repository Markdown deliberate

- Update an existing section first. Add a page only for a distinct, lasting reader
  task or reference that does not fit an existing page, or when explicitly asked.
- Put new product topics in the site's established topic directory and link them
  from the relevant navigation or guide. A new package-owned reference belongs in
  its existing `docs/` structure and must be connected to the site when intended
  for product readers.
- Keep repository roots to established entrypoints. Do not add feature-named
  summaries, completion reports, validation reports, scratch plans or duplicate
  how-to files just to record that work happened.
- Use code comments or Go API comments for local implementation contracts, tests
  for executable behavior, and established contributor docs for maintainer steps.
  Do not turn implementation details into a new user guide without a reader need.
- Keep task-specific notes in the conversation or PR. Add an ADR, migration guide,
  security report or other durable record only when requested or required by an
  established repository convention; use its designated directory.

## Complete the product documentation

Identify the affected site topics before editing code. Update their owning source
alongside the implementation, including examples, defaults, compatibility limits
and migration steps when they change. Check related setup and troubleshooting
pages rather than adding a disconnected feature announcement.

For synchronized references, update the package source first. After that revision
is published to the source remote, fetch the affected sibling `origin/main` and
run `python3 scripts/sync-docs.py` from `pluto-site`. The sync reads committed
remote revisions, not local edits. Inspect its diff and `docs/sources.json` for
unrelated refreshes. Update site-authored guides directly as needed as well.
Do not push source changes or deploy merely to satisfy this workflow without
existing authorization.

When site access or an authorized source revision is unavailable, complete the
available source edits and report the exact outstanding site pages and refresh
step. Treat that work as incomplete; do not silently substitute extra Markdown
in the package repository. A request to work in one repository does not override
an explicit restriction on editing another.

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
- Refresh package-owned references using the source-revision workflow above.
  Confirm every changed product behavior is covered on the site, not only in
  repository docs, and that new pages are reachable through existing navigation.
- Build the site and run its checks before an authorized deployment.

## Agent readers

Keep concise guidance in [Pluto Skills](https://github.com/plutoframework/pluto-skills).
The `pluto-docs` skill points here; skills must not duplicate the manual.

Every topic is exported as `/docs/<slug>.md` from the same source as Starlight.
[docs/llms.txt](https://plutoframework.github.io/pluto-site/docs/llms.txt) lists the
exports. Maintain one manual and validate Markdown targets with
`python3 scripts/check-docs.py` after assembling the site.

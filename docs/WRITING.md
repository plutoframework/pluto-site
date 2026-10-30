# Writing Pluto documentation

Use OpenCode's documentation (https://opencode.ai/docs/) as the editorial reference.
Write original Pluto instructions; do not copy their prose.

- Open with what the feature does and when to use it.
- Use short, descriptive headings: Install, Configure, Usage, Options.
- Show a small working command or configuration before discussing edge cases.
- Explain the result immediately after the example, including generated paths.
- Put prerequisites before the step that needs them.
- Use tables for flags/defaults and callouts for actionable limitations.
- Keep marketing language and space metaphors out of instructions.
- Link deeper package references rather than repeating implementation details.
- Identify supported versions. Distinguish scaffolding from completed app wiring.
- Check commands against the pinned CLI. Compile complete examples in CI.

Reference snapshots preserve upstream package wording and exact source revisions.
Edit those in the package repository, then refresh with scripts/sync-docs.py.

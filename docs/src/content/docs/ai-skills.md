---
title: "AI skills and Markdown"
description: "Install concise Pluto guidance and fetch documentation without HTML."
---

Give your coding agent task-specific Pluto conventions. Each skill contains short
do/don’t lists and links to the relevant docs. Install only the skills you need.

## Install skills

Requires Node.js 22.20+. Run from your project:

```sh
npx skills add plutoframework/pluto-skills
```

Choose skills and supported agents in the installer. Installation is project-local
by default. Add `-g` for a user-wide install, or select a skill explicitly:

```sh
npx skills add plutoframework/pluto-skills --skill pluto-api -a codex
```

| Skill              | Covers                                                             |
| ------------------ | ------------------------------------------------------------------ |
| `pluto-project`    | Initialization, configuration and upgrades                         |
| `pluto-api`        | Endpoints, operations and domain state                             |
| `pluto-security`   | Authentication, RBAC, tenants and feature flags                    |
| `pluto-data`       | Persistence, pagination, idempotency, jobs and cache               |
| `pluto-frontend`   | React, UI libraries, themes, registries and UI state               |
| `pluto-agents`     | Typed AI runs and tool authorization                               |
| `pluto-maintainer` | Framework changes, experience improvements and security validation |

The maintainer skill has a short entrypoint and focused implementation, experience
and security references. It applies to work on Pluto itself; the other skills
guide application work.

Use `npx skills check` to inspect updates and `npx skills update` to apply them.
See the [public collection](https://github.com/plutoframework/pluto-skills) for
release pins. Existing project instructions and explicit user choices still
apply; installing guidance does not authorize deployment or paid API calls.

## Fetch Markdown docs

Start with the [agent index](https://plutoframework.github.io/pluto-site/docs/llms.txt).
It links to one plain Markdown file per topic. Fetch only what the task needs:

```sh
curl -fsSL https://plutoframework.github.io/pluto-site/docs/backend/state.md
```

Every content page has a `.md` URL alongside its human-readable page. For example,
`/docs/backend/state/` becomes `/docs/backend/state.md`; the introduction is
`/docs/index.md`. Exports use the same source as Starlight, remove frontmatter and
resolve documentation links to their Markdown targets.

These are explicit static URLs, compatible with GitHub Pages. They do not require
HTML parsing, JavaScript or an `Accept` header. Reference snapshots retain their
upstream version and commit; compare those with your installed packages.

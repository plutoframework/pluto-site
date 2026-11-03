---
title: Software factory (experimental)
description: Set up a local Pluto factory that turns scoped GitHub issues into validated pull requests.
sidebar:
  order: 2
---

The factory runs implementation, checks, independent review and QA around a
durable work queue. Use GitHub integration to watch ready-labeled issues and
publish pull requests, or managed integration for local examples.

This is an **unreleased local prototype**. Use matching factory-engine and Pluto
[factory](https://github.com/plutoframework/pluto-factory) and CLI
development checkouts. The published CLI reference describes a different,
released revision and does not establish factory support.

## Install

Required tools are Python 3.12+, uv, Git, Go 1.25.5+, Herdr Core (`hc`), Pi and
fnox. GitHub integration also needs `gh` with access to the target repository.
The adapter reuses that login for HTTPS Git through a command-scoped
credential helper; it does not change global Git configuration or put token
values in command arguments.
Generating an age identity needs `age-keygen`; a 1Password backend needs `op`.

Set these paths to the development checkouts that contain the factory engine
and CLI integration:

```sh
PLUTO_FACTORY_SOURCE=/absolute/path/to/pluto-factory
PLUTO_CLI_SOURCE=/absolute/path/to/pluto-cli
uv tool install --editable "$PLUTO_FACTORY_SOURCE"
mkdir -p "$HOME/.local/bin"
go -C "$PLUTO_CLI_SOURCE" build -o "$HOME/.local/bin/pluto" ./cmd/pluto
pluto factory --help
```

Ensure the uv tool directory and `~/.local/bin` are on `PATH`. For development,
`PLUTO_FACTORY_ENGINE` can instead name the factory virtual environment's
`pluto-factory` executable. It accepts an executable path, not a shell command.

The native command passes arguments and streams to the Python engine. It does
not download or install that engine implicitly.

## Configure

The factory uses separate master, application and factory configuration:

| File | Purpose |
| --- | --- |
| `~/.config/pluto/pluto.toml` | Secret-free master defaults |
| `<repository>/pluto.toml` | Application generator manifest |
| `~/.config/pluto/factories/<name>/factory.toml` | Resolved factory settings |

`XDG_CONFIG_HOME` changes the base configuration directory. A repository's
manifest is never discovered as master defaults.

Example master defaults:

```toml
[factory]
coordinator = "model"
coordinator_model = "openai-codex:gpt-6.1-terra"
auth_mode = "existing"
integration = "github"
github_issue_label = "factory:ready"
github_poll_seconds = 30
github_auto_merge = false
close_source_issues = true

[factory.worker]
provider = "openai"
model = "gpt-6.1-sol"
reasoning = "high"

[factory.reviewer]
provider = "openai"
model = "gpt-6.1-sol"
reasoning = "high"

[factory.qa_model]
provider = "openai"
model = "gpt-6.1-terra"
reasoning = "medium"

[factory.secrets]
provider = "age"
generate_age_key = false
```

Age is the default fnox backend. Master settings may contain provider choices,
public recipients and credential references, never secret values. Factory names
and repository registrations belong to individual setup operations.

Explicit setup flags override `setup --config` fields, which override master
defaults and built-ins. Setup freezes the resolved settings; changing the master
file does not change an existing factory. Inspect defaults with:

```sh
pluto factory defaults show
```

### Secrets and authentication

Each factory gets its own `fnox.toml`. Age stores encrypted values; 1Password
stores references to existing vault items. The engine isolates fnox's global
configuration layer and resolves only the credential selected for its API
connection. There is no providerless plaintext storage fallback.

Choose `--secrets-provider age --generate-age-key` to generate an owner-only
identity, or select an existing private identity with `--age-key-file` and its
public recipient with `--age-recipient`. Keep identity backups separate from
factory-state exports.

For 1Password, choose `--secrets-provider 1password --op-vault <vault>` and
reference an item with `--op-item op://vault/item/field`. This does not create or
change vault items.

API keys can be entered through the wizard or `--api-key-stdin`, or referenced
through an explicitly named environment variable. Secret values do not belong
in the master file, factory TOML, task packets or command arguments.

Native Pi and the Pydantic AI coordinator have separate provider settings. This
Pi version uses `provider = "openai"` for native OAuth access. The coordinator's
`openai-codex:` namespace belongs to Pydantic AI. Setup reuses existing logins by
default; an explicit Codex-login choice can run the native login flow.

Readiness metadata is not proof of inference. Verify worker execution and the
default coordinator's subscription authentication with a live work item before
relying on them. A deterministic fixture run does not establish either.

### Host execution

The prototype runs on the host in explicitly selected cooperative mode. A
repository registry scopes task assignments and factory Git operations; it does
not sandbox an unrestricted worker shell. The default `isolation = "required"`
refuses dispatch because an enforced isolation adapter is not implemented yet.
Select `--isolation cooperative` only for a trusted local prototype.

`--trust-repositories` preauthorizes Pi project guidance for registered
repositories during each run. It does not provide OS isolation.

Container packaging and portable export/import are follow-up work.

## Set up a factory

Create and push the target repository first. For the Snake example, prepare the
repository yourself, then decompose the game into scoped issues with the
assistant. Setup does not create the game or implement the whole project.

Open the guided setup:

```sh
pluto factory setup
```

`init` is an alias. `pluto --interactive factory setup` also opens the guided
flow with supplied arguments prefilled. The wizard previews the plan before
creating files. Piped input and CI do not silently open it. At the first
repository prompt, blank selects the current directory; at the additional
repository prompt, blank ends the list. A human name such as `Snake Game`
becomes a stable factory name such as `snake-game`.

For a pushed local checkout, the equivalent headless shape is:

```sh
pluto factory setup --no-input \
  --name snake --repo game=/absolute/path/to/snake \
  --integration github --github-repo game=OWNER/REPOSITORY \
  --issue-label factory:ready --poll-seconds 30 \
  --check '["npm","test","--","--run"]' \
  --qa '["npm","run","test:e2e"]' \
  --harness pi --coordinator model --isolation cooperative \
  --trust-repositories
```

The check commands are examples: replace them with executable checks supplied
by the actual repository. They are argument arrays, not shell strings. Missing
checks and QA commands are reported as not ready rather than successful.

Repeated `--repo NAME=PATH` entries register multiple writable repositories;
`--read-repo` registers reference repositories. The simple flags share check
commands across repositories. Use a full config for per-repository checks and
flag matrices. Each repository maps independently to a GitHub slug.

Without `--github-repo`, GitHub setup can infer standard GitHub HTTPS or SSH
origins locally. Unresolved writable repositories and mappings for unregistered
names fail before factory files are created. Setup does not query GitHub.

Setup creates the factory TOML, SQLite schema, editable role prompts, QA
guidance/rules, resource directories and fnox configuration. Existing authored
configuration is preserved. Its response distinguishes file creation from
runtime readiness.

```sh
pluto factory doctor --factory snake --verify-auth
```

Doctor reports native Pi no-refresh readiness without printing credentials.
`--verify-auth` additionally runs a captured GitHub authentication check; it does
not print the backend's output or ask GitHub to create anything.

Use `--herdr-space <id>` to associate workers with an existing Herdr app space.
Without that mapping, workers remain available through Core while running
headlessly. Automatic space creation is not implemented.

## Queue work

Create the configured ready label once if the repository does not already have
it:

```sh
gh label create factory:ready --repo OWNER/REPOSITORY \
  --description "Ready for the Pluto factory" --color 0366d6
```

Write an issue with explicit scope and acceptance checkboxes. The adapter treats
issue checkbox items as acceptance criteria:

```markdown
## Scope
Describe one implementable increment and its constraints.

## Acceptance
- [ ] Describe the expected observable behavior.
- [ ] Describe the regression or integration check that proves it.
```

Apply the ready label after the issue is ready for autonomous work:

```sh
gh issue edit ISSUE_NUMBER --repo OWNER/REPOSITORY --add-label factory:ready
```

For a cross-repository issue, an optional declaration can name registered
repository aliases and explicit criteria:

```markdown
<!-- pluto-factory:
{"repositories":["core","cli"],
 "acceptance":["State the combined observable result"]}
-->
```

The declaration cannot add repository authority. Each requested alias must be
registered in the factory. Without a declaration, the source repository is the
default target.

For dependent increments, add issue references to that declaration:

```markdown
<!-- pluto-factory:{"repositories":["game"],"depends_on":["#2","OWNER/REPO#3"]} -->
```

Local references use the source issue repository. Cross-repository references
must name a registered GitHub repository. Missing prerequisites remain waiting;
merged and completed prerequisites unlock the next increment. Self-dependencies
and cycles are rejected. Invalid issues are recorded without starving healthy
intake. Execution remains sequential within a factory.

Direct callers can use `pluto factory submit` or `submit --file request.json`;
GitHub intake uses the same durable queue and duplicate-delivery protection.

## Local dashboard

```sh
pluto factory ui --port 8765
```

Open `http://127.0.0.1:8765` to follow factories and tasks in the browser. The
local dashboard refreshes the queue, dependencies, activity, reports, check
output and PR links. Select a task for its details and copy a task-specific
Herdr command or terminal attach command. The browser does not execute them.

Use **Expand task** to give the selected task the workspace. **Restore
workspace** or Escape brings the queue back, retaining the task, tab and reading
position. The orbit beside **Agent working** appears only for a current worker
with a coordinator observation from the last 15 seconds. Queued, idle, paused
and stale workers stay static; reduced-motion preferences disable animation.
A lost connection stops the indicator while preserving the last displayed data.

The observer binds only to loopback and reads private database snapshots. It
does not dispatch, pause, resume or modify factory work. Stopping the dashboard
leaves factories running. Credentials, assignment/config bundles and worker
reasoning transcripts are excluded; known secret patterns in displayed output
are masked, without claiming comprehensive secret detection.

Use `--root /alternate/factories` or `--home /path/to/factory` to select an
alternate registry or additionally include a custom factory. Watcher status and
task status are separate so blocked and dependency-waiting work stays visible.

## List factories

```sh
pluto factory list
pluto factory list --json
pluto factory list --root /alternate/factories
```

The default view is a compact human-readable table with wrapped details; narrow
terminals use a stacked view. `--json` returns the complete machine-readable
inventory. Both `pluto factory list --json` and `pluto factory --json list`
are supported.

Inventory reports name, location, registered repositories, role models,
coordinator status, current work phase and last recorded activity. It checks the
coordinator lock rather than trusting a saved PID. Paused/deferred work and
per-factory configuration or database errors remain visible. Human output omits
internal work identifiers.

Listing does not initialize or migrate a database or modify factory state. The
standard registry is `$XDG_CONFIG_HOME/pluto/factories`, normally
`~/.config/pluto/factories`. `--root` selects another registry. `--home` or
`PLUTO_FACTORY_HOME` additionally includes an explicitly selected custom home;
the command does not search arbitrary filesystem locations.

## Run and inspect

```sh
pluto factory start --factory snake --watch
pluto factory inspect --factory snake
```

GitHub factories watch by default and remain alive while the queue is empty.
`--no-watch` drains current work; `--once` performs one intake/tick cycle.
Managed examples exit when drained unless watch is explicitly requested.

The factory implements a candidate, runs configured checks, collects independent
review and QA reports, and publishes validated changes to pull requests. Inspect
shows durable progress, evidence and PR references. Automatic merging is off by
default. Explicit `--auto-merge` remains subject to repository checks and review
policy. Issue closure follows completed integration across required repositories,
not merely a worker's coding-complete report.

For automatic merges, `github_required_checks = ["validate"]` in factory
configuration requires that exact CI check to succeed at the validated head.
Missing, pending or non-successful required checks withhold merge requests,
including the interval before GitHub reports a new workflow run. The adapter
does not use an administrator merge bypass.

Recoverable errors trigger bounded autonomous recovery. Notifications report
what happened and what the coordinator is doing without blocking unrelated
work. Missing authority or exhausted recovery options defer only affected work.
Slack delivery is outbound-only in this prototype.

### Show the current worker

```sh
pluto factory open --factory snake
pluto factory open --factory snake --terminal
pluto factory open --factory snake --json
```

The default command peeks the currently active worker in an existing Herdr
window. `--terminal` attaches through the calling terminal for SSH or headless
use. The lookup follows the ledger's current assignment and checks live Core
identity, ownership labels and generation before presenting the session. It
does not reuse an old terminal ID after recovery.

Paused, deferred and historical sessions are not selected. If the current phase
has no active worker, such as checks or integration, the command reports that
phase instead. If the app window is unavailable, it provides a rerunnable
terminal fallback without opening a new window, space or tab.

This visibility command does not pause coordination or change work state.
Default output omits internal IDs; `--json` includes operational metadata.

Pause before taking over a worker:

```sh
pluto factory pause --factory snake
pluto factory resume --factory snake
```

Opening a terminal alone does not establish exclusive human control. Failed
worktrees and useful evidence remain available for recovery.

## Testing examples

For a disposable transport and recovery demonstration:

```sh
pluto factory demo --directory /tmp/pluto-factory-demo
pluto factory demo --directory /tmp/pluto-factory-recovery \
  --scenario crash_once
```

These examples use deterministic fixture workers, real SQLite state, managed
Git worktrees and executable flag-off/flag-on checks. They preserve source
repositories and do not call a model or publish GitHub PRs. Run them in empty
directories. Their success does not prove live model judgment or GitHub access.

## Limits

Managed integration advances only a factory-owned local clone. GitHub mode is a
separate intake and publication adapter; real remote publication and merging
need provider-backed validation. There is no atomic merge across repositories,
so every intermediate repository state must remain compatible and deployable.

This prototype runs one active item per factory. Multiple factories have
separate SQLite databases and coordinator locks. Release/deployment, additional
bug-source adapters, enforced process isolation, container migration and Slack
approvals are not implemented. Prompts and QA rules are configurable, but prompt
text cannot grant tool access or weaken deterministic integration gates.

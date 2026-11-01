---
title: "Pull requests and automated review"
description: "How Pluto reviews changes, requires maintainer approval, and merges routine fixes."
---

Pluto changes enter `main` through pull requests. Formatting, tests and security
checks run alongside an Astra review through GPU Router. A deterministic merge
policy decides whether the change qualifies for automatic approval. GitHub
branch protections remain the final authority for merging.

Developers and coding agents write code, push branches and open PRs using their
normal contributor identities. **Pluto PR Steward is the reviewer.** It
never writes code, pushes branches, opens PRs or creates replacement submissions.
It reviews existing PRs, requests changes when it finds defects, approves passing
changes and merges them when the policy and GitHub protections permit it.
Steward authenticates as `jackbot-advrsty` for review comments, approvals,
change requests and merges. The GitHub App signs the required check results.

## Open a pull request

Run the repository's formatter and checks before opening the PR. Describe the
behavior changed, the tests run and any compatibility or documentation impact.
Keep implementation summaries and test evidence in the PR rather than adding
report files to the repository.

The reviewer runs when a PR is opened, reopened, marked ready or updated. Feedback
is kept on the PR. Push fixes to the same branch; the next review evaluates the
complete current diff and revisits previous findings. A comment alone does not
prove that a finding was fixed.

Draft PRs do not qualify for automatic merging. To retry a failed review, run the
**Pluto PR review** workflow manually, supply the PR number and select
**retry_review**. That option spends review tokens. Leave it off to reevaluate
policy using existing evidence. CI completion and review notifications reuse a
completed review for the same repository, PR, head, base and policy revision.
Failed or interrupted attempts remain blocked until a new revision or an explicit
retry; those notifications do not repeatedly call the model.

## What qualifies for automatic merging

All of the following must hold for the current revision:

- A complete structured Astra review exists for the current head, base and policy
  revision. Missing or partial review output blocks merging.
- The review explicitly reports low risk, no concerns and no unresolved key
  issues. Medium or high risk needs an independent maintainer approval; a
  maintainer approval does not waive reported defects or security findings.
- Every required repository CI workflow and the dependency-security workflow
  has a successful pull-request run for this head commit.
- Sensitive changes have an independent maintainer's approval for this head.
- No maintainer's request for changes remains outstanding.
- GitHub's native requirements pass: code-owner approval where applicable,
  current branch checks, resolved conversations and CodeQL thresholds.

Steward approves eligible changes submitted by other identities, then squash
merges them or queues GitHub's native auto-merge while native checks finish.
New commits invalidate stale approvals and require checks and review again.
Steward has no branch-protection bypass. API failures, model failures,
unknown mergeability and incomplete file inventories do not grant approval.

## Changes requiring a maintainer

Authentication and authorization repositories always require a maintainer.
Across other repositories, the policy also protects authentication, authorization,
cryptography, sessions, credentials, tenant boundaries, database migrations and
SQL, dependency manifests and lockfiles, CI, build tooling and review policy.
Both sides of a rename are checked. Binary files and omitted patches require
manual review rather than being treated as reviewed text.

A human approval must come from a repository administrator or maintainer, belong
to the current head commit and come from someone other than the PR author.
Bots and dismissed or stale approvals do not count. GitHub also enforces native
code-owner approval independently of the model's verdict.

GitHub does not allow authors to approve their own PRs and also requires approval
from someone other than the last pusher. Sensitive changes require an eligible
human maintainer other than the PR author. Steward's own approval never counts as
that human approval, even though its machine account has GitHub's `User` type.
The controller rejects PRs authored by the Steward account without spending model
tokens. Steward does not author or recreate contributor PRs.

## Security checks

Dependency checks run `govulncheck` for tracked Go modules and `npm audit` for
tracked npm lockfiles. High and critical npm vulnerabilities fail the check.
CodeQL uses extended queries; its native merge rule blocks high or critical
security alerts and error-level findings. Secret scanning and push protection
are enabled separately in repository settings.

Passing these checks and AI review is evidence for a merge decision, not an
independent security audit. Runtime authorization, transaction ownership,
concurrency and regression coverage still need substantive review.

## Maintain the automation

The canonical implementation is
[`pluto/scripts/pr_automation`](https://github.com/plutoframework/pluto/tree/main/scripts/pr_automation).
Repository entrypoints are generated from its job template and pin the policy
and reviewer source to full commit SHAs.
Changes to that implementation, the pins and `CODEOWNERS` require maintainer
review. Update the source and tests, exercise a pilot PR, then update the pins.
Do not let a PR choose the policy used to evaluate itself.

The `pluto-pr-steward` App publishes two checks: **Pluto review** records completed
review evidence; **Pluto merge policy** grants or withholds merge eligibility.
Required checks are bound to that App's identity, preventing an ordinary Actions
job from substituting a check with the same name.
The App check-signing token is separate from the `jackbot-advrsty` credential and
is not passed to the model-review subprocess. The reviewer API client rejects PR
creation, commit creation and branch writes.

Credentials live in the **pluto-review** Actions environment, restricted to the
`main` branch. `PLUTO_STEWARD_TOKEN` authenticates the machine account; the App key
is used only to mint repository-scoped check-signing tokens. The privileged
reviewer runs on `pull_request_target` or trusted
`workflow_run` events, checks out only pinned policy and reviewer source, and
never executes PR code. Unprivileged PR tests and review-event notifications do
not receive those credentials.

GPU Router uses base URL `https://gpurouter.io/v1`, gateway model
`openai/gpt-6-astra` and high reasoning effort. There is no weaker fallback.
Each model request has a ten-minute deadline; timed-out calls are not replayed
automatically. The review process has a fifteen-minute limit. A timeout keeps
merging blocked; retry the review workflow after the provider recovers.
`PLUTO_AUTO_MERGE=false` keeps a repository in review-only mode; `true` enables
merging when every gate passes. This setting does not bypass branch rules.

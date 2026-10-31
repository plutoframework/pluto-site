---
title: "Pull requests and automated review"
description: "How Pluto reviews changes, requires maintainer approval, and merges routine fixes."
---

Pluto changes enter `main` through pull requests. Formatting, tests and security
checks run alongside an Astra review through GPU Router. A deterministic merge
policy decides whether the change qualifies for automatic approval. GitHub
branch protections remain the final authority for merging.

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
**Pluto PR review** workflow manually and supply the PR number. The same workflow
reevaluates policy after CI finishes and after a review is submitted or dismissed.

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

The App then approves eligible changes and enables GitHub's native squash
auto-merge. New commits invalidate stale approvals and require checks and review
again. The App has no branch-protection bypass. API failures, model failures,
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

GitHub does not allow authors to approve their own PRs. A sole maintainer should
have an automation identity open a sensitive PR, then review and approve it as
that maintainer. A PR authored by the review App itself cannot receive its own
App approval and needs an independent review.

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
Repository entrypoints pin its reusable workflow and policy to a full commit SHA.
Changes to that implementation, the pins and `CODEOWNERS` require maintainer
review. Update the source and tests, exercise a pilot PR, then update the pins.
Do not let a PR choose the policy used to evaluate itself.

The `pluto-pr-steward` App publishes two checks: **Pluto review** records completed
review evidence; **Pluto merge policy** grants or withholds merge eligibility.
Required checks are bound to that App's identity, preventing an ordinary Actions
job from substituting a check with the same name.

Credentials live in the **pluto-review** Actions environment, restricted to the
`main` branch. The privileged reviewer runs on `pull_request_target` or trusted
`workflow_run` events, checks out only pinned policy and reviewer source, and
never executes PR code. Unprivileged PR tests and review-event notifications do
not receive those credentials.

GPU Router uses base URL `https://gpurouter.io/v1`, gateway model
`openai/gpt-6-astra` and high reasoning effort. There is no weaker fallback.
`PLUTO_AUTO_MERGE=false` keeps a repository in review-only mode; `true` enables
merging when every gate passes. This setting does not bypass branch rules.

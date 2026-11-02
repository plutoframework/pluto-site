---
title: "Pull requests and automated review"
description: >-
  How the independent Pluto PR Steward reviews, approves and merges changes.
---

Pluto changes enter `main` through pull requests. Formatting, tests and security
checks run alongside an independent model review through GPU Router. A
deterministic merge policy decides whether the independent reviewer can approve
and merge. GitHub branch protections remain the final authority for merging.

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
completed review for the same repository, PR, head, base, policy revision and
selected model. Changing the selected model invalidates cached review evidence.
Failed or interrupted attempts remain blocked until a new revision or an explicit
retry; those notifications do not repeatedly call the model.

## Verified review input

Before inference, the controller binds review input to the exact repository, PR,
head and base. It verifies the file inventory and text against immutable Git trees
and blobs, including both sides of renames and verified empty files. Recovered
patches must match those files. Generated files, checksums and lockfiles remain
in the complete inventory; filenames do not grant review exemptions. Binary or
nonregular files, unreadable content and mismatched inputs block verification
instead of being counted as reviewed.

The reviewer plans every chunk before the first model request. Each call has a
96,000-token total cap, including the rendered input and 16,384 reserved output
tokens. A review permits at most five model calls, with no automatic retries or
fallback model. A plan that filters, omits or clips files, or exceeds these
limits, is rejected before inference.

Keep PRs reviewable. If a complete review cannot fit these limits, split large
changes into coherent PRs or ask maintainers to resolve input-verification or
review-configuration problems. Do not retry an unchanged incomplete plan. Checks
publish allowlisted failure reasons rather than raw provider errors or subprocess
logs; resolve the reported cause before requesting a token-spending retry.

A read-only resolver first identifies the current PR using GitHub's built-in
credential, without Steward, App-signing or model-provider credentials.

Review jobs share a queue for the same repository, PR number and head SHA,
without canceling an active review. Different PRs pointing to the same commit
have independent queues. Wait for the current review to finish before requesting
a manual retry. A new head still needs its own review; serialization cannot make
stale evidence valid.

## What qualifies for automatic merging

All of the following must hold for the current revision:

- A complete structured review from the selected approved model exists for the
  current head, base and policy revision. Missing or partial review output blocks
  merging.
- The review covers every changed file and explicitly recommends
  `no_concerns_found`. Unresolved findings or concerns, including security
  concerns, block approval; a positive recommendation alone does not waive them.
- Intrinsic risk is assessed as low, medium or high. Unknown or malformed risk
  blocks approval. A `needs_review` recommendation also blocks approval, even
  when a human has approved the PR.
- Every required repository CI workflow and the dependency-security workflow
  has a successful canonical pull-request run for this head commit. If a workflow
  also has push runs for this head, its latest push run must succeed too. A
  successful PR run does not waive a failing or unfinished push duplicate.
- No human maintainer's request for changes remains outstanding. Steward does
  not dismiss those requests to make a PR eligible.
- GitHub's native requirements pass: code-owner approval where applicable,
  current branch checks, resolved conversations and CodeQL thresholds.

Steward approves eligible changes submitted by other identities, then squash
merges them or queues GitHub's native auto-merge while native checks finish.
New commits invalidate stale approvals and require checks and review again.
Steward has no branch-protection bypass. API failures, model failures,
unknown mergeability and incomplete file inventories do not grant approval.

## Sensitive changes and reviewer independence

The same evidence gates apply to authentication, authorization, cryptography,
sessions, credentials, tenant boundaries, database migrations and SQL, dependency
manifests and lockfiles, CI, build tooling and review policy. These categories do
not impose a separate human-approval requirement. The independent Steward account
can approve and merge them at any assessed intrinsic risk level when the complete
review recommends `no_concerns_found`, no unresolved findings or concerns remain
and all other gates pass.

Complete coverage includes both sides of a rename. Unreadable binary content,
omitted patches and incomplete file inventories remain coverage blockers; they
must not be counted as reviewed text. A human approval cannot substitute for
missing review evidence or waive unknown risk.

GitHub does not allow authors to approve their own PRs and also requires approval
from someone other than the last pusher. Steward must satisfy those independence
requirements and any native code-owner rules. Its independent-account approval
satisfies the policy without a separate human approval.
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

## Verify a merge receipt

After an actual Steward merge, a racing notification can leave a false-red
merge-policy check. Run **Pluto PR review** with the merged PR number and leave
**retry_review** off to audit the existing receipt without calling the model or
attempting another merge.

Repair requires the Steward's approval, signed complete positive review and
successful required checks for the reviewed head. GitHub must confirm that
Steward merged that head into `main`, with the expected base parent and the
reviewed head's exact tree in the squash commit. Missing or mismatched proof does
not qualify; this audit cannot authorize an open PR or bless a bypassed merge.

## Maintain the automation

The canonical implementation is
[`pluto/scripts/pr_automation`](https://github.com/plutoframework/pluto/tree/main/scripts/pr_automation).
Repository entrypoints are generated from its job template and pin the policy
and reviewer source to full commit SHAs.
Changes to that implementation, the pins and `CODEOWNERS` require the same
complete independent review as other changes. Update the source and tests,
exercise a pilot PR, then update the pins. Do not let a PR choose the policy used
to evaluate itself.

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

GPU Router uses base URL `https://gpurouter.io/v1`. For a rollout using the
approved model-selector profile, operators set the protected Actions repository
variable `PLUTO_REVIEW_MODEL` to one of these exact route literals:

- Opus 5.5, the default: `openai/anthropic/claude-opus-5.5`.
- Astra: `openai/openai/gpt-6-astra`.

An empty or unset variable selects Opus 5.5. Unknown values are rejected before
requests. Selection comes only from the protected variable; failures never
silently switch models. Both approved models use high reasoning effort and the
same review limits and gates.

Long review requests use streaming transport with one transport attempt per
call, no automatic retry and no fallback model. Only normal terminal completion
qualifies: interrupted or truncated responses, or responses without finish
information, block approval.

Each model request has a ten-minute deadline; timed-out calls are not replayed
automatically. The review process has a fifteen-minute limit. A timeout keeps
merging blocked; retry the review workflow after the provider recovers.
`PLUTO_AUTO_MERGE=false` keeps a repository in review-only mode; `true` enables
merging when every gate passes. This setting does not bypass branch rules.

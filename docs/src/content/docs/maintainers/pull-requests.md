---
title: "Pull requests and review"
description: >-
  Prepare changes, pass CI and security checks, and obtain maintainer review.
---

Pluto changes enter `main` through pull requests. Maintainers review the current
diff alongside CI and security results. GitHub's branch protections, required
checks and code-owner rules govern merging.

## Prepare the change

Keep each PR focused on a coherent change. Run the repository's formatter and
checks before opening it, and include a regression for a reproduced defect.
Describe the resulting behavior, validation, compatibility and migration needs.
Record test evidence in the PR rather than adding work-summary files.

Follow the repository's contributing instructions. Public behavior changes also
need their owning documentation updated; see the
[documentation guide](../documentation/) for source ownership and snapshot
refreshes. Keep a PR in draft while implementation or validation is incomplete.

## Obtain review

Request a human reviewer with relevant expertise. Review the complete current
diff, including generated files, dependency updates, migrations and CI changes.
Authentication, authorization, tenant boundaries, transactions and concurrency
need substantive review beyond passing tests.

Push fixes to the same branch and explain how they address feedback. Verify
reported defects with code and regression evidence. Resolve discussions when
the concern has been addressed, and retain outstanding requests for changes.
New commits may invalidate prior approvals and require another review.

## Check CI and security results

Every required check must succeed for the current revision before merging.
Inspect failures and repair their cause before rerunning checks. Missing or
skipped validation is not evidence of a pass; describe prerequisites and
remaining coverage explicitly.

Dependency checks use `govulncheck` for tracked Go modules and `npm audit` for
tracked npm lockfiles. High and critical npm vulnerabilities fail the check.
CodeQL and the repository's native security rules also apply. Secret scanning
and push protection are configured separately in repository settings.

## Merge

A maintainer merges after review, required checks, code-owner approval and
conversation-resolution requirements are satisfied. Use GitHub's normal merge
flow and preserve branch protections. Address blocking findings rather than
bypassing checks or dismissing requests for changes to obtain a green status.

Passing CI supports the review decision; it does not replace an independent
security audit or prove runtime authorization and transaction correctness.

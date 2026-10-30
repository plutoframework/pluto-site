---
title: "Responsive actions"
description: "Immediate feedback, confirmed cache updates and explicit optimistic behavior."
---

Every asynchronous action should acknowledge the interaction immediately. Do not
wait for the API before showing progress. Keep feedback local to the affected
control or row and preserve unrelated interaction.

## Choose feedback

- **Pending confirmation** is the default. Keep the record visible, show progress,
  prevent conflicting submits and change the result after server confirmation.
- **Optimistic projection** is explicit. Project a predictable change over current
  scoped data, then reconcile with server truth. Use it when failure is recoverable.
- Keep financial decisions and other consequential actions in confirmation mode
  unless the feature has a documented reason to use optimism.

## Use shared primitives

Install `@plutoframework/frontend` **0.2.1**. Use `/actions` for a dependency-free
controller, `/react` `useActions` for React ownership or `/query`
`useActionMutation` for optional TanStack Query integration. The state entrypoint
remains dependency-free; Query and React remain optional peers.

Read the [API and examples](../state/#responsive-actions) before implementing a
feature. Transports and cache updates remain in feature adapters. Pass explicit
actor/session/tenant scope, including resource identity when callbacks capture it.
Apply authoritative response data in `confirm` before background reconciliation;
a refresh failure must not be presented as a failed business write.

New CLI forms use these helpers and include held-response tests. They refuse a
connected callback without an explicit scope. Existing authored components are
not silently migrated by updating the CLI.

## Handle failure honestly

A definite rejection removes that action's optimistic projection and preserves
input for correction. Do not restore a whole-list snapshot: it could erase
another completed change. Pending projections run over current canonical data.

Timeouts, disconnects and ambiguous server errors may happen after commit. The
default classification is uncertain; conflicting retries stay locked until the
host establishes the outcome through authoritative reconciliation. Resolve it
explicitly after checking. Resource keys prevent duplicates within one controller;
backend idempotency keys remain separate, stable business intents.

## Verify the interaction

- Hold the response open; assert immediate accessible progress and duplicate protection.
- Reject the request; verify preserved input and no false success.
- Lose the response; verify uncertainty and no blind retry.
- Complete concurrent actions out of order; preserve independent changes.
- Switch actor/tenant or unmount; fence stale confirmations.
- Fail background refresh after a confirmed write; retain the successful outcome.

These primitives do not provide durable recovery, offline queues, cross-component
locking, exactly-once effects or faster database execution. They make the frontend
responsive while the server remains authoritative.

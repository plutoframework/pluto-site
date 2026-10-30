---
title: "Worked examples"
description: "Application integrations and deterministic Pluto testing examples."
---

Start with actual application wiring, then use controlled tests to explore
failure paths. Complete source and prerequisites are linked below.

## Application integrations

| Task                                                              | Source and setup                                                                                                          |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Build and run an API with authenticated business operations       | [Purchasing application](../example/)                                                                                     |
| Summarize supplied text with real model inference                 | [OpenAI summary command](https://github.com/plutoframework/pluto-agent/tree/main/examples/summary)                        |
| Enroll, verify and sign in with PostgreSQL-backed credentials     | [Local credential integration](../backend/credentials/)                                                                   |
| Connect responsive UI feedback to actual submit/approval requests | [Purchasing mutations](https://github.com/plutoframework/pluto-example/blob/main/web/src/features/purchases/mutations.ts) |
| Commit business data and audit delivery through an outbox         | [Application worker](https://github.com/plutoframework/pluto-example/blob/main/cmd/worker/main.go)                        |
| Follow two pages while preserving visibility                      | [Core pagination](https://github.com/plutoframework/pluto-core/tree/main/examples/pagination)                             |
| Combine assignment, permission and resource policy                | [RBAC purchasing](https://github.com/plutoframework/pluto-rbac/tree/main/examples/purchasing)                             |

The model example needs provider credentials and may incur charges; its output
varies. The full application needs PostgreSQL, migrations, verified accounts and
explicit memberships. Local Mailpit delivery is for development. Pagination and
RBAC use local data while executing the actual library algorithms.

## Deterministic testing examples

| Boundary                                                            | Test walkthrough                                                                                             |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Protected endpoint with fixture sessions and grants                 | [CLI HTTP harness](https://github.com/plutoframework/cli/blob/main/docs/FIRST-ENDPOINT.md)                   |
| Session middleware and revocation                                   | [In-process Auth test](https://github.com/plutoframework/pluto-auth/tree/main/examples/protected-http)       |
| Transaction visibility and job settlement without external delivery | [Jobs/PostgreSQL test](https://github.com/plutoframework/pluto-jobs/blob/main/docs/TRANSACTIONAL-EXAMPLE.md) |
| Tool authorization with zero external calls on denial               | [Scripted purchase review](https://github.com/plutoframework/pluto-agent/tree/main/examples/purchase-review) |
| Concurrent confirmation, rejection and uncertain outcomes           | [Controlled action promises](https://github.com/plutoframework/pluto-frontend/tree/main/examples/actions)    |

These isolate boundaries. Fixture issuance is not a login flow, scripted output
is not inference, and a synthetic delivery handler does not send a notification.
Keep those fixtures in testing code. See the [authoring guide](../maintainers/documentation/)
for the documentation standard.

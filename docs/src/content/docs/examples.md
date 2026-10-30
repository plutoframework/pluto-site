---
title: "Worked examples"
description: "Complete, runnable examples of Pluto's application boundaries."
---

Start with one task. Each example has complete source and an executable path;
README snippets link back to the implementation and its tests.

| Task                                                                | Example                                                                                                       |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Generate a protected endpoint and receive a real HTTP response      | [CLI walkthrough](https://github.com/plutoframework/cli/blob/main/docs/FIRST-ENDPOINT.md)                     |
| Follow two pages while preserving tenant visibility                 | [Core pagination](https://github.com/plutoframework/pluto-core/tree/main/examples/pagination)                 |
| Protect an HTTP handler and revoke its session                      | [Auth walkthrough](https://github.com/plutoframework/pluto-auth/tree/main/examples/protected-http)            |
| Combine trusted assignment, permission and resource policy          | [RBAC purchasing](https://github.com/plutoframework/pluto-rbac/tree/main/examples/purchasing)                 |
| Commit a business write and outbox job, then process it             | [Jobs/PostgreSQL guide](https://github.com/plutoframework/pluto-jobs/blob/main/docs/TRANSACTIONAL-EXAMPLE.md) |
| Run typed tools and prove denied runs make no external calls        | [Agent purchase review](https://github.com/plutoframework/pluto-agent/tree/main/examples/purchase-review)     |
| Project a removal, recover from rejection and reconcile uncertainty | [Frontend actions](https://github.com/plutoframework/pluto-frontend/tree/main/examples/actions)               |

Most examples use synthetic in-process fixtures. The Jobs example explicitly
starts a disposable PostgreSQL container. The agent example uses a scripted model
and loopback vendor service; no model key or paid call is required.

Fixture session issuance and static memberships demonstrate trusted wiring, not
a production login mechanism. Keep real credential verification, resource
checks, migrations and operational policy at their documented application boundaries.

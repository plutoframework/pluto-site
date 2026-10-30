---
title: "Introduction"
description: "Welcome aboard with Pluto."
---

Pluto gives Go APIs a clear home: explicit routes, small HTTP handlers, testable operations, and shared primitives. Add a React frontend when your application needs one.

This field guide covers **CLI v0.12.1** and **Core v0.4.0**. Package reference pages identify their own source revision. Pluto is an evolving framework preview; read each integration's operational requirements before deploying.

## Get started

1. [Create an application](getting-started/), add an endpoint and run its tests.
2. Learn the [code conventions](conventions/) before adding business logic.
3. Use the [CLI reference](cli/reference/) for flags and wizard behavior.
4. Explore [the purchasing example](example/) for a complete application with authentication, tenants, approvals, audit history and a React UI.

## Build on shared primitives

- [Authentication](backend/auth/) and [RBAC](backend/rbac/) establish verified identity and permissions.
- [Core](backend/core/) provides pagination, idempotency and explicit data caching.
- [Feature flags](backend/features/) control exposure; [state machines](backend/state/) describe business transitions.
- [Jobs](backend/jobs/) deliver work after commit; [telemetry](backend/telemetry/) connects traces, metrics and logs.
- [Agents](backend/agents/) call tools through application-controlled authority.

## Add a frontend

Start with [React profiles](frontend/profiles/), then configure [themes](frontend/themes/) and [custom component registries](frontend/registries/). API contracts remain the boundary between the frontend and business operations.

## Configure your application

Read [configuration](configuration/) for saved project choices, environment variables and feature overrides.

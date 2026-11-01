---
title: "Application architecture"
description: "Place application code, define dependencies, and enforce Pluto's architectural boundaries."
---

Use this model to decide where code belongs before choosing a primitive or
adding a lint rule. Pluto applications have six responsibility layers and an
explicit composition root. Features such as purchasing span several layers;
authentication, auditing and telemetry have responsibilities at several
boundaries.

This is the target architecture contract for framework development and application
design. Existing generators and applications implement parts of it. The
[enforcement status](#enforcement-status) distinguishes current checks from work
still needed; this guide does not introduce new CLI commands or migrate code.

For the existing package inventory, concrete gaps and phased adoption criteria,
see [architecture mapping and migration](../maintainers/architecture-migration/).

## The layers

| Layer | Owns | Must delegate |
| --- | --- | --- |
| Presentation | Screens, forms, user interaction, accessibility, display formatting, client query and action state | Business authority and durable changes to server operations through the API |
| Entry adapters | HTTP, job and tool input decoding, protocol validation, verified caller context, operation invocation, response/error mapping | Business decisions to operations; persistence and outbound effects through operation-owned interfaces |
| Application operations | A use case: enforce access, load scoped facts, invoke domain decisions, coordinate persistence and effects | Business rules to domain code; concrete I/O to data or infrastructure adapters through ports |
| Domain rules | Business concepts, value validation, normalization, calculations, resource policies, lifecycle definitions and guards | I/O and orchestration to operations |
| Data | Databases, caches, object stores, queries, data mapping, transactions, concurrency checks and durable records such as audit/outbox entries | Business decisions and access requirements to operations and domain rules |
| Infrastructure adapters | Identity-provider, payment, email, model-provider and other external-service integrations; external delivery mechanisms | Business decisions to operations/domain rules; persistence to data capabilities |

Layers describe responsibilities and dependency rules, not separate services,
processes, repositories or Go modules. A small app can implement them in a single
server. Features organize code within layers; they do not create permission to
bypass a boundary.

The data layer is a first-class boundary. A remote object store belongs to data
even when its client uses HTTP. A payment provider belongs to infrastructure even
when it retains records. Classify the capability by responsibility, not protocol
or vendor. Data and infrastructure are separate implementation boundaries used
through ports; neither is a mandatory step after the other in a request pipeline.

The composition root loads validated configuration, constructs concrete adapters,
injects dependencies, registers entry points and owns startup/shutdown. It can
reference every server layer for wiring. It must not execute request-specific
business rules or become a service locator.

## Dependency rules

Runtime calls and source dependencies are different. An operation calls a
repository at runtime, but imports a small interface rather than PostgreSQL.
The PostgreSQL adapter satisfies that interface. This keeps the operation usable
from HTTP, a worker or an agent tool without importing those transports.

The following table describes allowed production dependencies between roles.
It is a target for transitive checking, including helper packages.

| Source role | Allowed dependencies | Forbidden dependencies |
| --- | --- | --- |
| Presentation | Feature UI logic, frontend primitives, API contracts; the designated client boundary owns HTTP calls | Server packages, database clients, authoritative permission or lifecycle implementations |
| Entry adapters | Operation contracts, wire contracts, protocol libraries, trusted identity/context adapters | Storage implementations, business calculations, direct business mutations |
| Application operations | Domain rules, consumer-owned ports, policy/feature evaluators, appropriate framework primitives | HTTP handlers, concrete database/cache/provider clients, presentation, composition |
| Domain rules | Other explicit domain concepts and pure primitives such as Core state or compiled policy evaluation | Operations, transports, storage, provider clients, environment reads, ambient clock/randomness or mutable global state |
| Data | Consumer-owned ports, domain data contracts, approved database/cache/object-store primitives and clients | Presentation, entry handlers, operation execution, composition, direct external business effects |
| Infrastructure adapters | Consumer-owned ports, domain data contracts, approved framework adapters and service clients; narrow data ports when needed | Presentation, entry handlers, operation execution, concrete data implementations, composition, decisions about which business actions are permitted |
| Composition | Configuration and concrete constructors from the server layers | Request-time business decisions and hidden global lookup |

Ports are interfaces owned by their consuming application package. They describe
the capability needed, not an entire database or vendor SDK. Contract-only
packages may hold shared interfaces and data types when needed to avoid cycles;
they must not become an unclassified home for logic.

An infrastructure adapter needing credential persistence consumes a narrow data
port, wired by composition. It does not construct a database client. Data code
can coordinate database, cache and object-store capabilities within its own
boundary, but must state their consistency guarantees. A database transaction
does not roll back an object upload or a cache write. Persisting outbox intent
belongs to data; sending the corresponding email belongs to infrastructure.

Do not solve a forbidden import by moving it into `utils`, a callback, or another
helper. Classify every production package by responsibility. Tests can compose
multiple layers to exercise a complete path without changing production rules.

## Where code lives

Use the following package roles when extending the existing structure. Paths are
a placement guide, not a claim that every current scaffold generates them.

| Responsibility | Existing or target application location |
| --- | --- |
| Feature UI and interaction logic | `web/src/features/<feature>/`; components, forms, queries, mutations and flows retain their distinct roles |
| Reusable presentation | `web/src/shared/ui/`; receives props and callbacks |
| HTTP client and generated wire types | `web/src/api/`; feature queries/mutations are its consumers |
| HTTP entry adapters | `internal/handlers/<feature>/` |
| Worker entry adapters | `internal/background/<feature>/`; decode a job and invoke its use case |
| Agent tool entry adapters | Feature-specific tool bindings; invoke the same authorized application use cases |
| Application operations and their ports | `internal/operations/<feature>/` |
| Domain rules | `internal/domain/<feature>/`; named files for models, validation, policies, calculations and lifecycles |
| Data implementations | `internal/storage/<adapter>/` for persistence and object stores, and `internal/caching` for cache adapters; sqlc output stays behind the data boundary |
| Infrastructure integrations | Dedicated adapter packages such as `internal/auth` for identity integrations; add a named package for each external service |
| Composition and configuration | `cmd/`, `internal/app/`, `internal/config/` |
| Endpoint and wire contracts | `internal/paths/` and application API/model packages; no use-case execution |

The example currently has some flat operation/domain packages and provisional
HTTP helpers in `internal/pluto`. Classify their contents by responsibility before
splitting them; a directory rename alone does not establish a boundary.

Endpoint metadata is a declaration consumed by registration and generation, not
an executable layer. Request/response types describe the wire format. Domain
types describe business concepts. Database records describe persistence. Map
between these contracts at the corresponding adapter; do not expose sqlc records
as public API models.

## Business logic and generated entry points

Generated entry adapters own protocol mechanics. Authored operations coordinate
work. Authored domain packages own business decisions, even when a rule is only
three lines long. There is no size-based exception.

An operation may branch to propagate an error, handle absence, or act on a typed
domain result. It must delegate decisions such as an approval threshold,
discount calculation, self-approval prohibition or permitted lifecycle transition.
This distinction is about responsibility, not the presence of an `if` statement.

The target is to keep generated entry adapters closed to authored business logic,
with explicit extension points in operations and domain packages. A generator may
create an initial authored domain file; its permanent role is domain code, not
an entry adapter. Existing CLI handler and operation stubs are authored files and
remain protected from overwrite. Changing their ownership requires a deliberate
generator migration.

Domain rules take explicit facts and return values, decisions or domain errors.
An operation supplies verified identity, loaded records and any required current
time or random value. Domain code does not fetch additional facts through a
captured repository or hidden network call.

## Lifecycle ownership

The target lifecycle contract requires all of the following:

1. Declare the entity fields that represent lifecycle state.
2. Assign each lifecycle one owning domain package.
3. Reject state assignments outside approved initial construction, transition
   and persistence-rehydration paths.
4. Require transition writes to carry the evaluated change, entity identity and
   expected version.
5. Enforce stale-write rejection atomically in the database.

Prefer private fields and controlled constructors/mutation methods so the compiler
enforces ownership wherever possible. Go package privacy alone cannot prevent
arbitrary assignments inside the owning package; type-aware checks must cover
those paths and restrict access to rehydration entry points. Private fields also
do not prove that a zero value is valid. Mutation and persistence boundaries must
reject invalid values and prevent replay of a decision against another entity or
version. These contracts extend the current Core decision API; they are not
guarantees already supplied by `Next`.

## Authorized operation boundaries

Every entry path must invoke the required authorization boundary for its use
case. Merely finding an `Authorize` call somewhere in a function is insufficient.
The target is a required operation wrapper coupled to a restricted write
interface, so callers cannot skip the gate and invoke the underlying mutation.
Bind authorization to the current actor, tenant, resource and action, and define
when mutable membership or policy facts must be revalidated. A flag or a stale
authorization result cannot substitute for current permission.

This is a contract for future typed boundaries and runtime enforcement, not a new
published wrapper API. Tests must attempt denied direct operation calls as well
as HTTP calls, including attempts to reuse authority for another resource.

## Network and authentication boundaries

Network code belongs at two edges. Incoming HTTP is an entry adapter; outbound
HTTP to an identity provider, payment service or model provider is an
infrastructure adapter. Database, cache and object-store protocols belong to data
adapters. Domain code must not know these protocols. Server
timeouts, TLS termination and ingress limits belong to deployment/transport
configuration, wired through composition where application-owned.

Authentication is a capability spanning these boundaries, not a single step
that makes all later calls trusted:

- Entry adapters establish caller context through trusted authentication
  integrations. Client-supplied roles and tenant IDs are not proof of authority.
- Identity infrastructure verifies credentials, sessions or provider responses.
- Operations require the appropriate identity, current tenant membership,
  permissions, authentication evidence and feature availability for the use case.
- Domain resource policies decide relationships such as ownership or whether
  an approver may decide their own request, using verified facts.
- Storage preserves tenant scope and concurrency constraints on every relevant
  read and write.

HTTP route permission checks are an early gate. Direct operation calls, jobs and
agent tools still need an authorized operation boundary. Background work must
declare its authority and revalidation semantics; a persisted actor ID alone
does not confer permission. Credential lifecycle endpoints can use the published
Auth adapters rather than recreating authentication algorithms in application
domain code.

## Follow a purchase approval

1. Presentation captures the user's intent and shows pending feedback. It does
   not grant approval authority.
2. The entry adapter decodes the request and supplies verified caller context to
   the approval operation.
3. The operation enforces access and loads the purchase through a scoped port.
4. The domain lifecycle evaluates the event and guard facts, returning a decision.
5. The operation asks its write port to persist the change with the expected
   version and required audit/delivery intent.
6. The storage adapter atomically checks the version and commits the mutation,
   audit and declared outbox work. A stale decision fails rather than overwrites.
7. The entry adapter maps the committed result or error to the wire contract.
   A worker later delivers outbox work through its own operation and adapter.

The application calls domain, data and infrastructure capabilities at different
points; domain code does not call down into storage. A successful state decision is not
proof of authorization or a successful commit. Rules involving multiple records
need an appropriate transaction, locking or constraint strategy for those facts.
See [state machines](../backend/state/) and [jobs](../backend/jobs/).

## Assign shared concerns

Each concern has an owner for intent and an owner for mechanism.

| Concern | Application/domain responsibility | Adapter responsibility |
| --- | --- | --- |
| Validation | Domain invariants and normalization | Protocol shape, decoding and limits; database constraints provide a backstop |
| Authorization | Operation access requirements and domain resource policies | Verified identity and scoped data access |
| Feature flags | Gate the use case independently of permission | Load explicit configuration; expose only intended client capabilities |
| Lifecycle/concurrency | Decide allowed transitions from facts | Atomically reject stale writes and preserve relevant constraints |
| Audit/outbox | Declare what business event and delivery the mutation requires | Persist them with the mutation in the same transaction |
| Idempotency | Define the logical action and required replay semantics | Claim, fingerprint and persist completion with the required atomicity |
| Pagination | Decide collection visibility and allowed filters | Apply visibility before bounded queries and cursor boundaries |
| Cache | Choose non-authoritative data and required access checks | Scope keys, bound freshness, load and invalidate without granting authority |
| External effects | Declare the intended action and failure semantics | Execute delivery with bounded retries and deduplication where required |
| Telemetry | Name meaningful operations without exposing sensitive facts | Instrument transport, storage and providers; keep diagnostics separate from business audit |

Library names do not define application layers. Core supplies mechanisms used in
several roles; Auth, RBAC, Jobs, Agent and Frontend retain their specialist
responsibilities. Application-specific rules remain in the application's domain.

Extract a shared mechanism only after demonstrating it across distinct business
cases. Prove that its inputs, guarantees and failure behavior generalize before
promoting it into the appropriate Pluto module. This does not authorize a second
implementation of a mechanism Pluto already provides.

## The example uses Pluto exclusively

The example originally prototyped the desired application before the framework
was derived from it. Going forward, it is the working proof of concept for the
current Pluto contract, not an independent implementation.

The example application must use Pluto's supported mechanisms, generators and
canonical enforcement system. It must not introduce an example-only framework,
alternative primitive or independent architecture rule set. Pluto must enforce
the same boundaries on the example that it enforces on consumer applications.

The example still owns its business rules, schemas, typed queries, explicit
wiring and application behavior tests at Pluto's authored extension points.
Using Pluto exclusively includes supported libraries and adapters selected through
Pluto; it does not require replacing vendor drivers with homemade code.

When a framework capability or check is missing, implement it in the owning Pluto
module or generator and then consume it in the example. Provisional example-local
framework helpers and architecture checks are migration debt. Consolidate checks
in Pluto and make the example invoke them; do not keep parallel copies or grant
the example an exemption. Keep application-specific business assertions in the
example, and use it as a real consumer proving that the shared rules work.

Preserve the existing example as a failing baseline during framework repair.
Fix libraries, generators, analyzers and trusted check execution first, then run
them against that unchanged baseline. Require clear failures for the known drift
before migrating the example. If a known violation passes, fix the upstream
enforcement; do not clean up the example to hide the missed detection. A schema
error alone is not evidence that unrelated architectural violations were caught.
After migration, require both a passing current example and regression evidence
that the old invalid paths are rejected.

## Enforcement status

Published CLI contract checks validate managed generated content, file limits and
selected transitive import boundaries: operations cannot reach HTTP or storage
implementations, handlers cannot reach storage, and paths cannot reach handlers
or operations. The example also has an application-local architecture test.
These checks do not prove that a handler or operation contains no business rules,
and they do not yet enforce every role in this guide.

The unpublished implementation adds a read-only architecture inspection command,
frozen-baseline evidence runner, bound lifecycle decisions and permission gates.
See the [candidate enforcement workflow](../maintainers/architecture-migration/#candidate-enforcement-workflow)
for usage and limits. These additions are building blocks; they do not yet make
the complete contract mandatory or authorize migration of the frozen example.

Use this contract to design the next checks:

| Boundary | Intended enforcement |
| --- | --- |
| Generated entry adapters | Generator ownership plus checks across the entire adapter package |
| Layer dependencies | Canonical package classification and transitive import checks |
| Domain purity | Restricted dependencies and type-aware checks for forbidden effects; explicit input facts |
| Lifecycle mutation | Controlled construction and mutation APIs plus checks on declared lifecycle fields |
| Required operation gates | Typed operation boundaries and runtime checks shared across entry paths |
| Transaction and tenant guarantees | Constrained repository contracts, database enforcement and integration tests |

Static checks must report a stable rule ID, exact file and line, owning
responsibility and supported repair. For example, this proposed diagnostic
describes a forbidden assignment and the required path; the rule is not yet
implemented:

```text
PLUTO-STATE-001 purchases/approve.go:42
Purchase.Status is owned by the purchase lifecycle.
Direct assignment is forbidden here.
Evaluate the lifecycle and persist through its transition writer.
```

Heuristics such as nested-branch detection can suggest an
extraction; they cannot prove that a state machine is the right business model.
Required CI checks must run the same contracts as local tooling. Skills teach
placement and repair decisions; tooling must enforce their outcomes. The contract
is a small, explicit set of places where business decisions can be authored and
a checked set of ways those decisions can affect the world.

Translate this architecture into checks one boundary at a time, preserving
authored code and documenting migration requirements. Check behavior as well as
structure: denied direct calls, cross-tenant access, stale writes, rollback and
repeated delivery. See [conventions and testing](../conventions/).

## Trace errors to their source

Every architectural correction must explain both how the invalid state became
possible and why it escaped detection. Trace the path through instructions,
library APIs, generated extension points, consumer migrations and actual check
execution. Fix the owning framework/tooling boundary and prove recurrence fails;
repairing only the example is incomplete.

Distinguish a missing rule from a bypassed rule, and a newly adopted constraint
from an existing requirement. Record evidence and unknowns rather than infer
agent intent from code. Use the [causal review and closure criteria](../maintainers/architecture-migration/#causal-review)
for each finding. Local tooling, trusted required CI and library/runtime contracts
must work together; skills teach the supported path but cannot enforce it alone.

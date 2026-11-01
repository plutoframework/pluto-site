---
title: "Architecture mapping and migration"
description: "Map existing Pluto packages to the six application layers and sequence enforceable boundary changes."
---

Use this map to migrate existing packages and the purchasing example to the
[application architecture contract](../../architecture/). It separates correct
placement, mixed responsibilities and missing enforcement. A package spanning
roles is not automatically a defect; a dependency that prevents a required
boundary from being enforced is a reason to split it.

This is a source-based baseline from October 31, 2026, not a release or security
certification. The map and gaps describe the baseline; the candidate capabilities
below are unpublished and do not close the complete migration. The six layers
are presentation, entry adapters, application
operations, domain rules, data and infrastructure adapters. Composition and
development tooling sit outside the runtime layers.

## Candidate enforcement workflow

The unpublished CLI adds a read-only inspection command that can examine an old
manifest without migrating it or executing application-owned scripts:

```sh
pluto architecture check --directory ../pluto-example --format json
```

The report includes package roles, diagnostics with locations and repairs, and
explicitly unassessed boundaries. Exit 1 indicates findings; exit 0 means only
the implemented checks passed. Neither exit 0 nor the presence of a local check
command proves required CI execution or complete architectural compliance.

The first checks classify conventional Go package paths and trace local imports,
including helper packages. They report obsolete manifests, incomplete source
inventory, unknown roles, unresolved imports and missing recognized local check
invocations. Normal CLI contracts also apply dependency, managed-operation and
source-derived lifecycle checks. External dependency internals, frontend
dependencies and complete business-rule/write analysis remain unassessed.
Configuration and
access-policy packages are supporting roles; their classification is not a
purity guarantee. Build variants are inspected together without type checking.

Fresh worker scaffolds place worker construction in `internal/app` and keep
handler dependency contracts in `internal/background`. Existing authored files
require an explicit migration. The generator must pass its own boundary checks
before an existing consumer is changed.

Schema 10 declares operations independently of their HTTP, worker and tool
entries. Each entry references one operation rather than authoring a separate
business callback. Managed gates, adapters, registration and dependency wiring
are checked against those declarations. Private implementation methods provide
a compiler boundary; canonical checks reject replacement adapters and the
captures or interface-embedding paths that Go alone permits.

A published-dependency scaffold is a compatibility draft until its required
protection contracts are supported. A membership lookup over caller-supplied
subject strings does not establish authenticated identity. Canonical checks must
reject that unsupported protection contract, even when the draft compiles.
The explicit local candidate profile adopts the unpublished opaque identity,
resource-policy and constrained-write APIs together. It is not a release claim
or permission to silently replace published dependencies.

The candidate contract separates authenticated identity from tenant membership.
Auth issues a callback-lifetime opaque identity; the configured manager checks
its exact issuer and live session. RBAC's identity gate verifies current tenant
membership, permission and resource policy and supplies the execution scope.
Restricted data ports recheck that scope on use, including cache hits and replay.
Original cancellation and session revocation are checked again after policy I/O.

### Adopt the supported local candidate

Use a fresh application for positive conformance. Candidate initialization is
noninteractive, requires multi tenancy and uses explicit absolute source paths:

```sh
pluto --no-input init /absolute/path/records --module example.com/records \
  --multi-tenant --boundary-profile candidate \
  --candidate-auth-source /absolute/path/pluto-auth \
  --candidate-rbac-source /absolute/path/pluto-rbac \
  --candidate-core-source /absolute/path/pluto-core \
  --candidate-jobs-source /absolute/path/pluto-jobs
cd /absolute/path/records
pluto --no-input add blueprint --file record-contracts.toml
go mod tidy
pluto fmt
pluto architecture check --directory . --format json
pluto vet
```

The blueprint declares resources, independent operations, matching behavior
contracts, roles, effects, HTTP endpoints, jobs and agent tools together.
Generation validates the complete contract before writing. Conflicting names,
authority, resource bindings, replay guarantees or retry budgets fail before a
partial application is created. Role declarations are a catalog, not actor
assignments; current memberships come from the explicit tenant/actor SQL table.

This profile implements scoped records with controlled construction, explicit
normalization, owner/tenant visibility, lifecycle guards (`none`, `owner`,
`not_owner`), atomic writes and bounded delivery. It owns production Go source,
including domain rules and operation workflows derived from metadata. Authored
hooks and additional production files require a supported framework extension.
Canonical checks also protect compiler directives, rehydration and construction
entry points, native/unsafe/reflection escapes, and managed migrations. The
canonical OpenAPI schema reader retains its required reflection under exact
managed integrity checks.

The current candidate accepts externally issued PostgreSQL sessions. Local
credential/OIDC ingress, single tenancy and route-only feature flags are rejected
until they have complete managed contracts. HTTP resource selection is explicit
(`body`, `path:name`, `query:name`, or `collection`). Write tools require a host
approved opaque intent and operation replay; model arguments and model completion
alone cannot authorize or report a committed write. Workers authenticate their
configured service credential for each delivery.

Apply generated migrations explicitly. Configure worker credentials using
`<PREFIX>JOB_<GROUP>_<ACTION>_CREDENTIAL` and effect destinations using
`<PREFIX>EFFECT_<GROUP>_<ACTION>_URL`, with group/action names in uppercase.
Destinations are deployment configuration. The fixed effect adapter verifies
persisted work, reauthorizes, bounds HTTP delivery and supplies the stable delivery
ID as the downstream idempotency key. The remote service must honor that key;
local checks do not prove external exactly-once delivery.

The CLI's candidate integration profile generates applications through these
commands, checks canonical source ownership, compiles all packages and runs real
PostgreSQL/race tests across three guard/visibility profiles. Its runtime consumer
executes one write through HTTP, a queued worker and a host-approved tool, and
checks denied authority, rollback and delivery behavior. Required named SQL and
runtime cases must run; a skipped or missing case is not a pass. The frozen
example remains a separate negative consumer and is never rewritten by these
checks.

The source-derived lifecycle rules identify state types used by Core machines:

| Rule | Rejected shape | Required repair |
| --- | --- | --- |
| `ARCH301` | Public mutable lifecycle-state fields in domain entities | Private state with controlled construction, mutation and rehydration |
| `ARCH302` | A resolved raw `Machine.Next` call or method reference outside domain code | A domain-owned evaluator whose result is required by the write port |
| `ARCH303` | Exported data entry points accepting raw lifecycle entities, including recognized containers and local wrappers | A constrained transition input and atomic scope/entity/state/version comparison; model initial creation separately |

This is a local source inventory, not complete Go type or assignment-flow
analysis. External factories, generic wrappers, reflection and unsafe code remain
unassessed. Private fields alone do not check every mutation inside their owning
package. A structural pass does not prove a database transaction is correct.

The candidate library contracts support the generated application boundary:

- Core `Machine.Evaluate` returns an opaque decision bound to scope, entity,
  source state and version. A writer uses its owning machine to reject zero,
  foreign or mismatched decisions. Guard-relevant facts come from authoritative
  persistence, never a display cache; versions cover every such fact.
- Auth `Manager.WithIdentity` supplies a private callback-lifetime identity.
  `Manager.UseIdentity` rejects another issuer's identity and revalidates the
  session. Authentication does not itself select or authorize a tenant.
- RBAC's optional identity module binds that identity to live membership and a
  required resource policy. Its opaque execution scope cannot be constructed
  from caller-owned subject, role or tenant strings. Data access uses the same
  gate again; revocation is not made atomic with a database transaction.
- Jobs `Definition[T]` binds a payload to one kind, strict decoding and validation.
  Prepared effects are transactionally enqueued; managed dispatch admits the
  target operation and retries only within the declared bound.

Core's nested shipment PostgreSQL consumer demonstrates the composed data
contract. Private normalized inputs and narrow ports separate domain decisions
from SQL and cache mechanics. Mutation, actor audit, typed outbox enqueue and
idempotency completion commit together. Replay binds actor, tenant, operation,
resource and input; queries apply visibility before pagination, exports are
capped, and cached display reads still authorize. Lifecycle evaluation reloads
SQL even when the display cache contains a matching-version record.

Run `scripts/postgres-check.sh` from Core for disposable database evidence.
Candidate integration requires the explicit local dependency profile and
`PLUTO_CORE_CANDIDATE_DATA=1`. Required mode rejects missing databases, absent
required cases and skipped cases. SQL mutations must fail the intended semantic
assertion; a build failure or unavailable database does not count as a kill.

The umbrella composes these libraries in a temporary consumer without changing
the example or published dependency pins:

```sh
python3 scripts/check-operation-conformance.py \
  --core ../pluto-core --rbac ../pluto-rbac \
  --auth ../pluto-auth --jobs ../pluto-jobs
```

It runs named SQL/race cases for issuer and scope rejection, guarded writes,
concurrency, replay, rollback, poisoned cache, bounded collections and typed
retry exhaustion. It also checks that every required case ran rather than
accepting a green command containing skipped tests. This proves the exercised
consumer and adapters; arbitrary application SQL still needs its own proof.


The umbrella repository owns the frozen-baseline runner. Supply an explicitly
built candidate CLI; do not invoke checks from the baseline repository:

```sh
python3 scripts/check-architecture-baseline.py \
  --cli /absolute/path/to/pluto \
  --baseline ../pluto-example \
  --report /tmp/pluto-architecture-evidence.json
```

The runner pins the example revision and fingerprints tracked contents before
and after inspection. It requires specific schema, dependency, invocation,
operation-gate, lifecycle/write, normalization, cache, collection, replay and
effect diagnostics with valid locations. A crash,
malformed report or unrelated error
does not satisfy the ledger. Success means the expected negative cases were
observed; the example remains noncompliant. `--require-complete` rejects reports
with unassessed boundaries. It remains stricter than the supported candidate
contract: a source scanner cannot prove arbitrary Go business semantics or
hosted merge-policy enforcement.
Ignored build outputs are outside the baseline proof, as documented in the
umbrella contributor guide.

The original phase plan below describes the migration baseline. The supported
local candidate now has generated adoption and composed runtime evidence; this
does not make the frozen example compliant or authorize its migration. Broader
business patterns, hosted required-check policy and published dependency adoption
remain separate work. Package reference snapshots must be refreshed from
authorized published source revisions before these APIs are presented as released.

## Framework package map

Paths in this table are relative to the named repository. Classify exported
capabilities as well as packages: importing a module with a pure policy function
does not make every function in that module appropriate for domain code.

| Repository and package | Layer or supporting role | Fit and required treatment |
| --- | --- | --- |
| `pluto-frontend`: `state`, `react`, `actions`, `query` entrypoints | Presentation | Good placement. Keep client state, effects and query integration separate from server authority. Standardize application consumption of write primitives. |
| `pluto-core/state` | Domain rules primitive | Good decision boundary. Does not control entity construction, state assignment, authorization or persistence; those contracts still need enforcement. |
| `pluto-core/features` | Application policy support and declarations | Immutable evaluation can be reused at operation gates and entry points. Feature availability never grants permission. |
| `pluto-core/pagination` | Shared collection contract and pure helpers | Operations/data use bounded requests and page results; entry adapters parse wire inputs. Domain entities need not own cursor encoding. |
| `pluto-core/idempotency` | Application/data contract | Claims and replay semantics support operation execution and durable storage. Do not move HTTP response capture into domain rules. |
| `pluto-core/httpidem` | Entry adapters | Correct home for HTTP replay capture. Its generic completion path is not atomic business completion. |
| `pluto-core/cache`, `cache/memory`, `idempotency/memory`, `stores/postgres`, `stores/valkey` | Data primitives and adapters | Keep cache loading and concrete persistence here. Scope/access requirements come from operations; memory implementations do not imply durability. |
| `pluto-core/telemetry` | Cross-cutting adapters and composition | One import package currently contains HTTP, pgx, cache, jobs and exporter wiring. Provide narrow observation contracts and separate adapter entrypoints where import boundaries require them. |
| `pluto-auth` root | Authentication operations, contracts and pure evidence/ceremony rules | Session manager orchestration and pure rules share a package. Preserve ownership in Auth; restrict which capabilities pure domain code may call rather than declaring the whole root pure. |
| `pluto-auth/httpauth`, `methods/*/*http` | Entry adapters | HTTP/session/cookie/protocol handling belongs here; it does not establish application membership or resource permission. |
| `pluto-auth/methods/password`, `methods/totp` | Authentication operations plus cryptographic/rule helpers | Keep algorithms and services in Auth. Pure helpers and effectful services need distinguishable boundaries if exposed to domain packages. TOTP source presence is not a release claim. |
| `pluto-auth/methods/oidc` | Infrastructure protocol client plus authentication operation | The package combines `Client` and `Service`; the service takes a concrete client. Separate protocol implementation from orchestration before treating the service as a transport-independent application dependency. |
| `pluto-auth/stores/memory`, `stores/postgres`, `stores/postgres/oidc`, `stores/postgres/totp` | Data | Correct storage boundary. Keep atomic credential/session/factor invariants in these implementations and their integration tests. |
| `pluto-rbac` compiled policy/catalog | Domain-compatible policy primitive | Pure permission evaluation fits domain/application rules. Application-specific ownership policies remain in the application. |
| `pluto-rbac.Authorizer`, `RoleResolver` | Application authorization support and data port | Role resolution may perform I/O. Do not approve all RBAC calls as pure merely because the package is stdlib-only. |
| `pluto-jobs` request/store contracts and worker | Application/data contracts; entry dispatch runtime | Worker dispatch and retry mechanics are framework runtime, not domain rules. Business job handlers must delegate to operations. |
| `pluto-jobs/stores/postgres` | Data | Durable claims, fencing and transactional enqueue fit here. No external delivery inside a database transaction. |
| `pluto-agent` root | Application execution runtime and tool-entry contracts | Typed runs and dispatch checks fit here. Application tool handlers still call authorized operations; a run is not a durable transaction. |
| `pluto-agent/providers/openai` | Infrastructure adapters | Concrete model-service HTTP belongs here and is injected at composition. |
| `pluto-agent/providers/scripted` | Testing/development infrastructure adapter | Keep deterministic demo setup outside production operation implementations. |
| `pluto-agent/integrations/plutorbac`, `integrations/otel` | Application authorization bridge; observability adapter | Preserve narrow optional integrations instead of expanding the root dependency surface. |
| `pluto-cli`: `internal/project`, `internal/frontend`, templates | Development tooling | Own generation, manifest migration and canonical application checks. Generated output has a layer; the generator itself is not a runtime layer. |
| `pluto` umbrella repository; `pluto-site` | Ecosystem tooling and documentation | Own shared contributor policy and the manual; neither is an application runtime layer. |

Repositories may legitimately span several layers. Do not rename repositories
or create one module per layer simply to match the table. Split import packages
when concrete dependencies or callable effects defeat a boundary. Shared runtime
mechanisms stay with their specialist owner, not automatically in Core.

No object-store package was found in this inventory. Reserve its place in data;
do not invent an adapter before there is a concrete consumer and contract.

## Example application map

Paths below are relative to `pluto-example`. Browser query caching remains
presentation state; it is not the server data layer or an authority for records.

| Existing code | Target role | Fit or migration |
| --- | --- | --- |
| `web/src/features/*/{pages,components,forms,flows}`, `shared/ui` | Presentation | Mostly aligned. Keep reusable parsing outside component bodies where appropriate; server validation remains authoritative. |
| `web/src/features/*/{queries,mutations,cache,provider}`, `web/src/api` | Presentation orchestration and its client boundary | Keep network access in the designated client. Purchase writes use Pluto action primitives; role changes use a different mutation path. |
| `web/src/app`, `web/src/main.tsx` | Frontend composition and shell | Provider/router construction is composition; shell markup is presentation. File roles distinguish them. |
| `internal/handlers/*` | Entry adapters | Most HTTP handlers already decode, invoke operations and map results. Feature-capability handling directly invokes evaluation rather than an explicit application operation. |
| `internal/pluto` | Entry adapters and transport mechanics | Provisional app-local decoding, registration, errors, middleware, pagination and replay glue. Reconcile with CLI-owned templates/shared mechanisms; do not retain an independent framework. |
| `internal/operations` | Application operations and consumer ports | Mixes orchestration with ownership/visibility rules, entity construction, mutation, cache mechanics and review configuration. Split responsibilities, not merely files. |
| `internal/domain` | Domain rules and models | Lifecycle definitions and validation fit. Public state/principal fields permit unchecked construction; `pagination.go` contains cursor-format mechanics rather than business policy. |
| `internal/features` | Application feature contracts/evaluation | Wraps Core appropriately, but must follow canonical declarations/gates and keep composition out of evaluators. |
| `internal/storage/{postgres,memory}`, sqlc output, `db` | Data | SQL, migrations, mapping and transaction execution fit. PostgreSQL job code imports the background-handler package to obtain job contracts. |
| `internal/caching` | Currently composition for data adapters | `New` selects disabled/memory/Valkey backends from configuration. Classify this as composition, not a data operation solely because of the directory name. |
| `internal/operations/organization.go` cache loader/key/TTL logic | Data decorator plus application operation | Move the cache implementation behind `OrganizationReader`; retain current access checks before every read, including hits. |
| `internal/auth/demo.go` | Entry context extraction, membership operation and development fixtures | Separate HTTP session extraction from scoped membership resolution and fixture data. The same membership operation must be usable outside HTTP. |
| `internal/auth/local.go`, `ingress.go` | Authentication composition and entry adapters | Move construction to composition and leave protocol limits/errors at the entry boundary. |
| `internal/auth/development_smtp.go` | Infrastructure adapter | Loopback-only SMTP delivery belongs outside the mixed auth package. Reusable development delivery should come from a Pluto-owned supported adapter/template. |
| `internal/background/audit.go` | Job contracts, entry handler and composition | Separate contracts from dispatch and worker construction; make the handler invoke an audit-delivery operation. The current archive sink is local data storage, not an external SIEM. |
| `internal/operations/review.go` | Application review operation, tool entry, output rules and demo composition | Keep the run in operations; separate tool bindings, pure output validation and scripted-provider setup by responsibility. |
| `internal/app`, `cmd/api`, `cmd/worker`, `internal/config` | Composition and configuration | Mostly aligned; move inline request handlers out of route composition. Preserve explicit lifecycle ownership. |
| `internal/api`, `internal/paths`, generated frontend API types | Wire/declaration contracts | Not a seventh executable layer. Mapping is an adapter responsibility; generated metadata needs a canonical manifest source. |
| `internal/development`, `cmd/dev-fixtures`, `cmd/openapi` | Development/build tooling and composition | Keep fixture creation explicit and outside production policy. OpenAPI generation consumes canonical contracts. |
| `internal/architecture`, `web/scripts/architecture.mjs` | Development enforcement | Replace independently maintained backend rules and secure ownership/versioning of frontend checks through Pluto. Keep application behavior tests. |

## Concrete gaps

This section records the original audit baseline. The candidate workflow above
describes the subsequent enforcement and generated adoption; these historical
findings do not describe the current candidate checker. They are gaps against
the target contract, not claims that every application path is incorrect or
exploitable.

### G1. The example is not yet a canonical CLI consumer

The example manifest uses schema 1, puts local credential settings under
`development`, and has no endpoint declarations. At the audit baseline, CLI code
used schema 8 (with limited schema 7 acceptance), expected credential capability
metadata, and derived managed contracts from endpoint declarations. The current
candidate uses schema 10 and independent operations. The example's CI runs its
own check script and backend architecture test. Simply adding `pluto vet` will
not migrate those contracts.

Evidence: [example manifest][example-manifest], [CLI manifest][cli-manifest],
[example checks][example-checks], [architecture test][example-architecture].

### G2. The checker does not cover the complete layer contract

CLI import checks recognize operations, handlers and paths as roots; they do not
independently classify every domain, data, infrastructure and composition
package. Traversal follows local imports, not the complete external dependency
graph. An external wrapper can therefore conceal dependencies that a local
wrapper would expose. The example's backend checker has a different rule set.

Frontend architecture code is generated from a CLI template, but frontend
contract validation checks the profile and catalog, not that checker file or
the package scripts invoking it. The example copy currently differs from the
template in formatting; that alone is not evidence of different rule behavior.
The issue is enforceable ownership and coverage, not just duplication on disk.

Evidence: [CLI checks][cli-checks], [frontend contracts][frontend-contracts],
[frontend checker template][frontend-checker].

### G3. Data imports an entry-handler package

`internal/storage/postgres/jobs.go` imports `internal/background` for the audit
job kind and payload. That package also defines the handler and constructs the
worker. Put the job contract in a contract-only package consumed by both data and
entry code. Keep enqueueing in the existing transaction.

Evidence: [data job adapter][example-jobs], [background handler][example-background].

### G4. Operations contain policy and domain mutation

Purchase visibility is expressed in `Get`, `List` and `ListPage`; membership
self-change policy is implemented inside `ChangeRole`. Purchase creation and
transition operations assemble mutable entity fields themselves. Move these
decisions to owned domain constructors, resource policies and transitions.
The broad `Repository` interface also combines purchase, membership and audit
capabilities; split it by actual consumers rather than introduce a generic store.

Evidence: [purchase operations][example-purchases],
[pagination operations][example-pagination],
[membership operations][example-administration], [repository port][example-repository].

### G5. Operation and lifecycle authority remain conventions

`Principal.Verified` checks nonempty public fields; it does not establish their
provenance. HTTP wiring supplies verified context today, but constructing that
struct is not itself authentication. `Purchase.Status` is public and
`SavePurchase` accepts an ordinary entity plus a version, rather than requiring
an evaluated transition. Existing version/audit/outbox enforcement is valuable
and must survive the change; it does not prevent all decision-path bypasses.

Evidence: [domain models][example-models], [transaction adapter][example-transactions].

### G6. Cache mechanics and composition sit in operation code

`OrganizationService` constructs a Core loader, composes cache keys, chooses a
TTL and loads cached data while also enforcing access. A data decorator behind
the reader port gives operations one scoped read path. Keep current permission
checks and tenant validation on cache hits; moving code must not weaken them.

Evidence: [organization operation][example-organization].

### G7. Some import packages combine incompatible roles

Telemetry combines HTTP middleware, PostgreSQL tracing and runtime/exporter
configuration. OIDC combines sign-in orchestration and its concrete HTTP client.
Auth root and RBAC also expose both pure decisions and orchestration through
ports. They must not be blanket-allowlisted as pure. Introduce narrow contracts,
split packages where needed, or constrain calls to verified pure capabilities.
Do not force broad package splits where a role already has a sufficient boundary.

Evidence: [telemetry adapters][core-telemetry], [OIDC service][auth-oidc],
[RBAC authorizer][rbac-authorizer].

### G8. Tool and worker entry paths mix responsibilities

Review operation code constructs tool policy/handlers, validates domain-shaped
output and provides a scripted provider. The audit job file combines contracts,
dispatch, delivery coordination and worker construction. Separate their entry,
operation, domain, data/infrastructure and composition roles while preserving
per-dispatch access checks and repeat-delivery behavior.

Evidence: [review operation][example-review], [background handler][example-background].

### G9. Presentation write behavior is not uniform

Purchases use `useActionMutation`; memberships use `useMutation` plus query
invalidation. Both can compile and satisfy the import rules while expressing
different handling of pending, uncertain and confirmed writes. Declare which
endpoint actions require the Pluto write primitive and check those consumers.
Do not classify all POST requests as durable business mutations or put auth
writes into business replay storage.

Evidence: [purchase mutations][purchase-mutations], [membership mutations][membership-mutations].

### G10. Data guarantees need required real-database evidence

The example has tests for tenant isolation, concurrent lifecycle decisions and
atomic audit/outbox writes. PostgreSQL tests skip without a dedicated database
URL; the inspected main CI workflow does not provision one. Generic HTTP replay
also remains separate from atomic business completion. Require integration
execution for these guarantees and declare replay semantics per operation.
No passing import checker can prove SQL isolation or commit atomicity.

Evidence: [integration setup][example-integration], [example CI][example-ci],
[Core transaction guidance][core-transactions].

## Phased enforcement plan

The example was intentionally built first to prototype the desired application
experience; the framework was derived from it. The project owner's account
establishes that design sequence. The independent prototype was a starting point,
not evidence of a failed attempt to follow a framework that already existed.
Drift accumulated as the ecosystem evolved. Going forward, the example is the
working proof of what Pluto supports and enforces.

Read the [causal review](#causal-review) before implementing a gap's fix. The
required order is: preserve the evidence, fix the upstream ecosystem, prove that
it rejects the existing drift, and only then migrate the example. Phases 0–3
must not edit the example's source, manifest, checks or dependency pins to make
the assessment easier. These phases may read it and run isolated tests against
it. New compliant consumers belong in framework-owned test fixtures.

The order represents dependencies, not calendar estimates. Candidate tooling
can assess the baseline before release; validate real release pins before
consumer adoption is complete. Publishing follows normal authorization.

### Phase 0: Preserve the baseline and define expected failures

**Owner:** CLI architecture tooling and the architecture guide.

- Pin the example revision and record relevant working-tree differences so that
  the test subject is reproducible. Keep this baseline available after migration.
- Define canonical roles, allowed dependencies, generated/authored ownership and
  external capabilities. Record expected findings for G1–G10, the responsible
  upstream owner, evidence and the kind of enforcement needed.
- Distinguish static violations, missing required contracts, runtime failures and
  absent required execution evidence. A placement finding is not proof of a
  behavioral defect, and a passing behavioral test does not waive placement.
- Review instructions, skills and templates for conflicting or obsolete guidance.
  Prepare the framework-owned corrections; leave baseline example guidance intact
  until migration. Record which constraints are newly adopted.

**Exit:** a reproducible baseline and an explicit expected-failure ledger exist.
Each gap names how the framework will detect it and how that detection will be
verified. An inventory alone is not proof of enforcement.

### Phase 1: Build canonical checks that can inspect the unchanged example

**Owner:** CLI analysis/generation and trusted ecosystem CI tooling.

- Consolidate backend checks into a CLI-owned engine, with frontend checks under
  equally explicit version/content ownership. Cover all declared roles and
  transitive dependencies, including helpers, external wrappers and re-exports.
- Run the checker independently of the example's editable scripts. Supply the
  target path and any required role mapping from the trusted harness; do not
  require installing new checks inside the target before it can be assessed.
- Report the old manifest as a compatibility error, but continue independent
  source checks where safe. If a check cannot run, report its precise blocker
  and mark it unassessed. One schema error must not masquerade as detection of
  the remaining architecture gaps. Legacy inspection must not silently migrate
  the application or weaken normal generation/validation contracts.
- Require diagnostics with stable IDs, exact locations, violated boundaries and
  supported repairs. Detect unknown roles, modified checker wiring and missing
  required contracts rather than silently skipping them.
- Build a trusted required-CI path. Removing an application script or workflow
  must not produce an accepted success. Validate protected merge/check settings
  rather than infer them from repository files.
- Provision the existing disposable PostgreSQL suite in the external harness;
  make missing prerequisites and skipped required cases fail its integration gate.
  Do not modify baseline application code to provide that assertion.

**Exit:** framework tooling emits actionable failures against the unchanged
baseline for implemented rules, with explicit coverage/blockers for the rest.
Unit tests and compliant generated fixtures verify that valid code passes. Do not
mark G1–G10 closed or begin example cleanup at this partial-coverage milestone.

### Phase 2: Fix upstream APIs, generators and enforcement coverage

**Owner:** Core, Auth, RBAC, Jobs, Agent, Frontend and CLI in their existing roles.

- Separate generated job contracts from handlers and worker construction. Provide
  canonical transport mechanics and declared operation/adapter extension points.
  Close generated entry packages to business decisions, including adjacent files.
- Expose narrow telemetry and OIDC contracts where their concrete dependencies
  prevent separation. Distinguish pure Auth/RBAC capabilities from effectful
  orchestration; do not blanket-allowlist whole modules as pure.
- Provide supported data decorators for caching, consumer-sized operation ports,
  domain constructor/policy locations and explicit composition paths. Preserve
  typed application SQL and migrations rather than add a generic database layer.
- Require operation gates for HTTP, worker and tool calls. Restrict execution-scope
  construction and mutation access; define resource binding, freshness and
  background authority. A stored actor ID is not permission.
- Provide controlled lifecycle initialization, transition and rehydration paths.
  Bind writes to evaluated changes, tenant/entity and expected version; reject
  invalid zero values and decision reuse. Keep Core state a pure decision engine.
- Establish typed commit contracts for mutation, audit, outbox and atomic replay
  where declared. Exercise PostgreSQL rollback, tenant isolation, concurrent
  decisions and multi-record constraints in framework conformance tests.
- Require the supported frontend action path for declared business mutations and
  explicit effect/delivery contracts. Keep authentication writes separate from
  business replay and preserve at-least-once delivery semantics.
- Fix generator instructions, skills and reference examples at their owning
  source. Validate new mechanisms across distinct business fixtures; do not
  require a state machine for a policy that is not a lifecycle.
- Add migration diagnostics for old consumer APIs and missing declarations. New
  library types alone cannot constrain unchanged consumers pinned to old APIs.
  Framework tooling must detect that unsupported consumer contract explicitly.

**Exit:** each expected gap has an upstream correction, an enforcement path and
positive/negative consumer fixtures. Re-run the unchanged example as coverage
expands. No example source change counts as an upstream fix.

### Phase 3: Prove rejection of the unchanged example

**Owner:** framework conformance harness and the owners of each expected finding.

- Run the completed canonical checks against the preserved baseline. Match actual
  findings to the G1–G10 ledger, including prerequisite and execution-evidence
  failures. Record rule IDs, locations, tool versions and outcomes.
- A known violation accepted by the checker is a framework test failure. Repair
  the analyzer, API contract, generator or test harness and rerun; do not move
  code, suppress the expectation or special-case the example to pass this gate.
- Resolve unassessed checks before declaring coverage complete. Compilation
  failures, tool crashes and unrelated schema errors do not count as successful
  detection of a different expected violation. Withdraw a finding only when new
  evidence disproves it, documenting that correction explicitly.
- Exercise practical bypasses in isolated fixtures: helper imports, re-exports,
  altered invocation, adjacent files, forged values, reused decisions and legacy
  write hooks. Require the supported path to pass in a fresh generated consumer.

**Exit:** the baseline application fails the applicable canonical gates for the
expected reasons. The framework's regression suite passes because it asserts
those specific failures and confirms compliant consumers pass. Every gap has
accounted-for evidence; there are no silent passes or unassessed guarantees.
This is the mandatory checkpoint before changing the example.

### Phase 4: Migrate the example through supported Pluto paths

**Owner:** example application, consuming the corrected framework and tooling.

- Migrate the manifest and managed contracts explicitly, preserving routes,
  permissions, flags, schemas and authored intent. Do not merely bump the schema.
- Adopt canonical checks and supported transport mechanisms; remove independent
  framework/checker implementations only after their replacement is available.
- Separate job contracts, auth/worker/tool entry points and composition; move cache
  mechanics to data and business decisions into their domain owners.
- Adopt restricted operation/lifecycle/write contracts and the consistent
  frontend mutation/effect paths. Preserve existing authorization, tenant,
  concurrency, audit, outbox and replay semantics through behavior tests.
- Resolve each diagnostic with the supported repair. If the repair is impossible
  with Pluto's APIs, return to the upstream owner; do not invent an example-only
  workaround or weaken the diagnostic.

**Exit:** the migrated example and fresh generated consumers pass the same
applicable rules, including required database/effect tests, using real release
pins without local replacements. Authored code survives regeneration. All G1–G10
are closed; old baseline regressions still produce their expected failures.

### Phase 5: Keep the proof of concept current

**Owner:** each framework change and its affected consumers.

- Require changes to generators, APIs and rules to enumerate affected consumers,
  update migrations and exercise the example plus clean generated fixtures.
- Retain the old baseline or minimal equivalent negative fixtures as regression
  evidence; do not turn expected historical failure into a waived current failure.
- Verify canonical-check ownership and trusted CI execution on every applicable
  change. Keep skills linked to current rules and supported diagnostic repairs.
- Track observed recurrences and reopen upstream causes when a known class passes
  unexpectedly. The working example demonstrates the current framework contract;
  it must not become a separate implementation again.

**Exit:** ongoing required gates catch recurrence and consumer drift. A correct
example and a framework that rejects the old incorrect paths remain separate,
required pieces of evidence.

## Completion criteria

The migration is complete only when all gaps above are closed and:

- The unchanged pre-migration baseline was rejected for the expected reasons
  before example cleanup, and that negative evidence remains reproducible.
- A fresh generated app and the example pass identical applicable Pluto rules.
- The example contains business intent and supported integration wiring, without
  its own framework primitives or independently maintained enforcement logic.
- Required checks are pinned and invoked in CI; rule deletion/suppression is not
  an accepted repair. Compiler, static, runtime and database checks each cover
  the guarantees they can actually establish.
- The release-pin consumer checks pass without local workspace replacements.
- Skills link the canonical architecture and diagnostic repairs; documentation
  reports implemented guarantees and migration limits accurately.
- Every gap has an evidence-backed causal record, an upstream owning fix and
  an executable recurrence test. The original failure and its nearest practical
  bypass must fail through the actual required consumer check, not only a checker
  unit test. Unresolved causes remain explicitly open.

This plan does not defer CI until the end: each phase adds its own required
negative fixtures and consumer checks. Operational tests that skip are not
evidence of a database or delivery guarantee.

## Causal review

For every finding, ask two separate questions: what allowed the state to be
introduced, and what allowed it to survive? Follow both paths through the public
API, generator, instructions, consumer migration, check implementation and actual
CI invocation. A fix to the example alone closes neither path by default.

Call a violation of an established invariant an error. A requirement introduced
by the six-layer contract creates migration debt in older code; do not claim the
author ignored a rule that did not exist. Both require prevention once the new
contract is adopted. The root cause must describe a technical or process
condition, not end at "the agent wrote it incorrectly."

### Evidence and limits

The review inspected local commit history, introduction diffs, generator output
templates, instructions and current check wiring. The project owner confirms
that the example came first as the desired-product prototype, from which Pluto
was derived. The original prototype's instructions explicitly placed business
policies in operations. Its schema 1 and local architecture test were present at
introduction; the initial CLI described schema 2 and app-local provisional
primitives. Independent prototyping was intentional. The missing enforced
transition to a canonical framework consumer allowed that separation and later
drift to persist.

There is no evidence in the inspected changes that an agent deliberately disabled
a failing rule to introduce these cases. Git authorship does not establish whether
an agent wrote code, what instructions it saw, or which commands actually ran.
Historical CI run logs and live repository protection settings were not inspected.
Distinguish a potential bypass in current tooling from evidence that it was used.

The existing backend/frontend architecture checks passed during the mapping
exercise. That establishes that the present rules accept the present tree, not
that every historical change passed CI or satisfied the new layer contract.

### Introduction and escape paths

| Gap | Evidence of how it arose | What allowed it to survive | Upstream correction and owner |
| --- | --- | --- | --- |
| G1: independent example | [Initial prototype][history-prototype] introduced schema 1 and a local checker; [initial CLI guidance][history-cli-guidance] described schema 2 and different generated ownership. Subsequent example integrations retained schema 1. | Example checks validate their own architecture/OpenAPI, not compatibility with the current CLI manifest and managed output. There is no canonical consumer requirement in that check path. | CLI owns explicit migration and one check engine; example CI must consume it. New framework capabilities must identify and migrate affected consumers. |
| G2: incomplete checks | [Initial CLI checker][history-cli-checker] deliberately implements local import reachability for selected roots. Frontend profile checks were introduced with narrow generated-contract coverage. | Passing the selected checks says nothing about unclassified packages, external wrappers or integrity of the checker invocation. No rule covers those classes. | CLI owns exhaustive role classification, dependency resolution, checker integrity and negative fixtures; trusted CI owns required execution. |
| G3: data imports handlers | [Jobs integration][history-jobs] introduced job declarations and handlers in one package and imported it from PostgreSQL. Current CLI job templates also co-locate payload construction and handlers. | There is no data-to-entry import prohibition in the example checker. Co-location makes the forbidden dependency the convenient way to reuse a payload. The template has the same design shape; this is not proof the example was generated from it. | CLI/Jobs separate contract and handler generation; CLI rejects the data-to-entry edge. Example consumes the shared correction without changing enqueue atomicity. |
| G4: policies in operations | [Original instructions][history-example-guidance] explicitly say business policies live in operations. This explains placement permitted by the earlier model. | Neither the guidance nor import checks require pure domain decisions; moving a policy between methods still passes. | Architecture/CLI owners update guidance and generators, expose named policy/constructor paths, and add enforceable boundaries. Treat the domain-only placement rule as a migration, not proven historical disobedience. |
| G5: mutable authority/state | Public principal/entity fields existed in the prototype. [State adoption][history-state-adoption] replaced branch decisions with `Next` but retained state assignment and the existing repository write signature. Core intentionally supplies a pure decision API. | Tests cover chosen operation behavior and concurrent commits, but public API shape still permits another caller to construct an entity and attempt a write without that decision. Structural checks do not close the mutation path. | Auth/RBAC/application gates establish execution authority; Core/CLI supply controlled lifecycle paths; data ports require bound decisions. Preserve the pure state machine rather than make it own databases. |
| G6: cache in operations | [Cache integration][history-cache] introduced the loader, key and TTL in the organization operation alongside access checks and tests. Guidance requires safe scoped caching but does not prescribe a separate data decorator. | Generic Core cache imports are permitted; no rule distinguishes operation intent from cache mechanics. Existing behavioral tests can pass with either placement. | CLI generates/injects a scoped data decorator; data owns mechanics and operations retain authorization. Test both prohibited placement and unchanged hit/miss/failure behavior. |
| G7: mixed library packages | [Telemetry introduction][history-telemetry] bundled adapters; [OIDC introduction][history-oidc] bundled service and protocol client. The current APIs intentionally expose these together. | The older package boundary model allows that coupling; no enforced pure/effectful capability classification exists for consumers. | Owning libraries expose narrower contracts or packages before CLI restricts consumers. Do not demand an impossible import boundary or blame the example for dependencies imposed by public APIs. |
| G8: mixed tool/worker roles | [Review integration][history-review] placed run setup, tool handlers, validation and demo provider in one operation file; jobs integration combined contracts, handler and worker construction. | Older operation/handler extension points permit the combined implementation, and tests exercise behavior without requiring role separation. | Agent/Jobs/CLI provide separate supported extension points and classify them; required operation gates cover each entry path. |
| G9: partial action adoption | Membership mutations date to the initial frontend. [Action migration][history-actions] updated purchase flows and tests; membership mutation history shows no corresponding action migration. | No inventory or rule requires all declared business mutations to adopt the primitive. Import checks accept both approaches. This is evidence of partial migration, not deliberate bypass. | Frontend/CLI derive affected consumers from declared mutation contracts, migrate all applicable paths and reject unsupported write paths. |
| G10: optional integration evidence | The prototype's database helper skips when its URL is missing. [CI introduction][history-ci] invokes ordinary tests/race checks without provisioning that database. | A successful general test command can include skipped integration tests; the inspected workflow has no required execution assertion for those guarantees. This does not show that database behavior is failing. | CI/tooling provides an isolated database and a strict integration mode; missing prerequisites or skipped required tests must fail. Data owners retain failure-window and concurrency assertions. |

### Recurrence tests required to close the causes

These are acceptance requirements for closing each historical cause. The
candidate workflow above describes current evidence; this table alone is not a
claim that every consumer, profile or hosted check has been verified.

| Gaps | Reintroduce the original failure | Exercise the nearby bypass |
| --- | --- | --- |
| G1–G2 | Run the required gate on an obsolete manifest and altered managed checker | Remove the checker invocation, rename a package, or route a forbidden import through a dependency; an absent check must not count as success |
| G3 | Import the job handler package from storage to reach a payload type | Re-export the handler dependency through a helper; contract-only packages must stay contract-only |
| G4, G6–G8 | Generate a consumer and insert a decision/effect into an adapter or pure domain boundary | Put the same behavior in a callback/helper or adjacent file; approved extension points must not reopen the forbidden path |
| G5 | Attempt direct lifecycle assignment and a write without the evaluated change | Construct invalid zero values, reuse a decision for a different tenant/entity/version, or call an operation without verified authority |
| G9 | Add a new declared business mutation using the legacy write path | Hide that path behind a custom hook; also verify uncertain outcomes, scope changes and refresh failures |
| G10 | Run the required integration job without a database or with skipped required cases | Inject audit/outbox/completion failure and concurrent changes; require the actual PostgreSQL assertions, not an in-memory substitute |

For semantic rules, first design the restricted API or generated code shape that
makes the rule checkable. An analyzer cannot generally infer arbitrary business
meaning or prove all callbacks pure. Record the exact supported enforcement
scope and remaining uncertainty; do not replace a missing guarantee with a
heuristic that happens to reject one example.

### Required causal record

For each correction, keep these fields in its issue/PR or maintained gap record:

1. **Invariant and applicability:** what must hold, where, and whether the rule
   existed when the offending code was introduced.
2. **Observation and provenance:** exact code, introducing/altering revision,
   relevant template/instructions/API, and reproducible current behavior.
3. **Introduction cause:** what made the invalid path possible or the default.
4. **Escape cause:** which check was missing, insufficient, skipped, disabled or
   never invoked; distinguish evidence from an untested hypothesis.
5. **Owning correction:** library API, generator, analyzer, migration, guidance
   and/or trusted CI change, with consumer changes as part of adoption.
6. **Counterfactual proof:** show the old path is accepted or possible before
   the correction and rejected afterward; exercise the nearest plausible bypass
   and confirm the supported path still works in a generated consumer and example.
7. **Closure evidence:** actual required-check execution, compatibility/release
   status, unresolved uncertainty and accountable owner. Do not close at code move,
   a new prompt instruction, or a passing unit test alone.

Repository-local checks cannot prevent a caller from choosing not to run them.
For changes entering the maintained codebase, trusted required CI and protected
merge policy must enforce execution independently of editable application scripts.
Validate that setup rather than infer it from a workflow filename. If a rule was
actually disabled, fix both the disabling route and any API/generator affordance
that made bypass attractive; do not stop at telling the agent to obey the rule.

## Source baseline

The map covers local source at the following revisions, not a claim that each
revision is published as a package:

| Repository | Revision |
| --- | --- |
| `pluto` | `12721eb9e82d3731c78a6fc3d9c70947a61f4002` |
| `pluto-core` | `8965909404ca417a2135bfb611a1733bb3b25331` |
| `pluto-auth` | `4fbe198ea51ccbc9cd85909aee7376075358f9fa` |
| `pluto-rbac` | `79d47bc258e8fd5a0df6e77e2a652c8900e9ef3a` |
| `pluto-jobs` | `5bd1fcb4d1959bb088bbdf12e64065d897ccb28a` |
| `pluto-agent` | `befa179e4361bcfb1973e2cfc8981a6ca95975aa` |
| `pluto-frontend` | `d29a5b50856e06028e02c1ee9cde29791b1220c0` |
| `pluto-cli` | `eb5fdc070a7880dc4fc4074197818fde9ab534cb` |
| `pluto-example` | `a54f525318900a8f09983ed202f7c436ea2d494f` |

[example-manifest]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/pluto.toml
[cli-manifest]: https://github.com/plutoframework/cli/blob/eb5fdc070a7880dc4fc4074197818fde9ab534cb/internal/project/manifest.go
[example-checks]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/scripts/check.sh
[example-architecture]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/architecture/architecture_test.go
[cli-checks]: https://github.com/plutoframework/cli/blob/eb5fdc070a7880dc4fc4074197818fde9ab534cb/internal/project/check.go
[frontend-contracts]: https://github.com/plutoframework/cli/blob/eb5fdc070a7880dc4fc4074197818fde9ab534cb/internal/frontend/profiles.go
[frontend-checker]: https://github.com/plutoframework/cli/blob/eb5fdc070a7880dc4fc4074197818fde9ab534cb/internal/frontend/templates/scripts/architecture.mjs.tmpl
[example-jobs]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/storage/postgres/jobs.go
[example-background]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/background/audit.go
[example-purchases]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/operations/purchases.go
[example-pagination]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/operations/pagination.go
[example-administration]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/operations/administration.go
[example-repository]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/operations/repository.go
[example-models]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/domain/model.go
[example-transactions]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/storage/postgres/transactions.go
[example-organization]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/operations/organization.go
[core-telemetry]: https://github.com/plutoframework/pluto-core/blob/8965909404ca417a2135bfb611a1733bb3b25331/telemetry/adapters.go
[auth-oidc]: https://github.com/plutoframework/pluto-auth/blob/4fbe198ea51ccbc9cd85909aee7376075358f9fa/methods/oidc/service.go
[rbac-authorizer]: https://github.com/plutoframework/pluto-rbac/blob/79d47bc258e8fd5a0df6e77e2a652c8900e9ef3a/authorizer.go
[example-review]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/operations/review.go
[purchase-mutations]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/web/src/features/purchases/mutations.ts
[membership-mutations]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/web/src/features/memberships/mutations.ts
[example-integration]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/internal/storage/postgres/integration_test.go
[example-ci]: https://github.com/plutoframework/pluto-example/blob/a54f525318900a8f09983ed202f7c436ea2d494f/.github/workflows/ci.yml
[core-transactions]: https://github.com/plutoframework/pluto-core/blob/8965909404ca417a2135bfb611a1733bb3b25331/docs/transactions.md
[history-prototype]: https://github.com/plutoframework/pluto-example/commit/f39e355124ebb0d92bafe1c2980f4045b0ea369b
[history-example-guidance]: https://github.com/plutoframework/pluto-example/blob/f39e355124ebb0d92bafe1c2980f4045b0ea369b/AGENTS.md
[history-cli-guidance]: https://github.com/plutoframework/cli/blob/df7cd9420c5762a4df69b68cd1562b1c2eccb2da/internal/project/templates/AGENTS.md.tmpl
[history-cli-checker]: https://github.com/plutoframework/cli/blob/df7cd9420c5762a4df69b68cd1562b1c2eccb2da/internal/project/check.go
[history-jobs]: https://github.com/plutoframework/pluto-example/commit/267d6c555290b7a5a166785837aee4439dd4a469
[history-state-adoption]: https://github.com/plutoframework/pluto-example/commit/9482517e969facc20ee68c59224965df3726f3c3
[history-cache]: https://github.com/plutoframework/pluto-example/commit/01c94af741a126f04b26ef436fa083ef49c084a1
[history-telemetry]: https://github.com/plutoframework/pluto-core/commit/f9cea193d9619810966a20d3022ba7b75732a0bb
[history-oidc]: https://github.com/plutoframework/pluto-auth/commit/d1b2554fb1d69605682284bda99fe1b9c489f54a
[history-review]: https://github.com/plutoframework/pluto-example/commit/f93401967ba01d54f45a12c11d61e12c51384a7b
[history-actions]: https://github.com/plutoframework/pluto-example/commit/4f52859420a95adeeecac5914b754e8b0cbd0199
[history-ci]: https://github.com/plutoframework/pluto-example/commit/b41ba3097f9cb11cfc2d2c5617833a8d78f37887

---
title: "Authored roles"
description: "Write business code in the rules, logic and adapter roles of the candidate profile, with an audit-log worked example."
---

The candidate boundary profile is unpublished and its generated `internal/scope`
package is app-local and provisional, not a published Pluto API. In this profile
authored code lives only in three declared roles per group. Pluto generates
everything around them and rejects every other file or import.

| Role | Directory | May import |
| --- | --- | --- |
| rules | `internal/rules/<group>` | pure standard library and other rules |
| logic | `internal/logic/<group>` | rules, the group's models and ports, `internal/scope`, `internal/domain`, pagination, state |
| adapter | `internal/adapters/<group>` | the group's rules, models, ports and sqlc package, `internal/scope`, pgx `pgtype`, pagination |

"Pure" excludes `os`, `net`, `reflect`, `unsafe`, `log`, `database/sql` and other
packages that reach the OS, network or filesystem. Third-party modules need an
`[[authored.dependencies]]` entry with a reason. Roles have no `init`, no
package-level variables (blank `var _ T` assertions excepted) and no goroutines.
Violations are `ARCH610` (imports) and `ARCH611` (shape).

## What is generated and what is authored

Generated and managed: the HTTP endpoint and OpenAPI, the operation gate and
workflow (`*_gate_gen.go`, `*_workflow_gen.go`), `contract_gen.go` in each logic
package, `internal/scope`, the sqlc config and a `queriesOf` helper, adapter
composition, model structs, and the membership resolver. Authored and created
once, never overwritten: the logic body `internal/logic/<group>/<action>.go`, a
rules package, and an adapter stub.

The gate checks identity, permission and the tenant-bound resource, then calls
the workflow, which calls your body with a `scope.Execution` and the declared
ports. An `Execution` has no constructor and is valid only inside that call.
`e.SubjectID()` is the only legitimate actor; `e.Tenant()` is the verified
tenant. An adapter reaches the database only through `scope.DB.Read` and
`Write`, which recheck the gate and open a transaction with the tenant bound.
Sqlc tenant arguments use a `Tenant` type authored code cannot construct.

Scope capabilities are enforced by owner: only generated code calls
`scope.Bind`, `scope.NewDB` and `scope.Queries`. An adapter that touches the
sqlc `DBTX` interface or `WithTx`, or calls `scope.Queries` itself, fails with
`ARCH611` or `ARCH603`. Use `queriesOf(tx)`.

## Worked example: a tenant audit log

Goal: append and list audit events, and verify content hashes, per tenant.

### Metadata

Declare roles, tables, queries, a port, models, operations and memberships in
a blueprint, applied with `pluto add blueprint --file audit.toml`:

```toml
[[roles]]
id = "recorder"
name = "Recorder"
description = "Reads and appends audit events."
permissions = ["audit.read", "audit.write"]

[[tables]]
group = "access"
name = "users"
tenant_column = "org_id"
row_security = true

[[tables]]
group = "audit"
name = "audit_events"
tenant_column = "org_id"
append_only = true
row_security = true

[[queries]]
group = "audit"
files = ["db/queries/audit/*.sql"]
tables = ["audit_events"]

[[ports]]
id = "audit.Events"
adapter = "audit.EventStore"
methods = [
  "Append(scope.Execution, models.NewEvent) error",
  "Query(scope.Execution, models.ListRequest) (pagination.Page[models.Entry], error)",
  "Scan(scope.Execution, int64, int64) ([]models.Entry, error)",
]

[[models]]
id = "audit.Entry"
fields = ["seq:int64", "type:string", "payload:json", "hash:hex", "created_at:time"]

[[models]]
id = "audit.NewEvent"
fields = ["type:string", "payload:json"]

[[operations]]
group = "audit"
action = "Append"
permission = "audit.write"
write = true
idempotency = "exempt"
replay_reason = "Append events are not replay-sensitive; callers dedupe upstream."
body = "authored"
resource = "audit.events"
resource_policy = "tenant"
ports = ["audit.Events"]
input = "audit.NewEvent"

[[operations]]
group = "audit"
action = "List"
permission = "audit.read"
collection = true
idempotency = "none"
body = "authored"
resource = "audit.events"
resource_policy = "tenant"
ports = ["audit.Events"]
response = "page"
item = "audit.Entry"
query = [
  { name = "type", type = "string", max = 64 },
  { name = "from", type = "time" },
  { name = "to", type = "time", after = "from" },
]

[memberships]
table = "access.users"
tenant_column = "org_id"
subject_column = "id"
role_column = "role"
```

An authored body requires `resource` and `resource_policy = "tenant"`. Model
field types are `int64`, `string`, `json`, `hex`, `time` and `bool`. Query
parameters are bounded: strings need `max` (at most 4096) and a `to` can require
that it follows `from`. A `Verify` operation (`response = "object"`) follows the
same shape. Endpoints are declared as usual with `[[endpoints]]`.

### Layout

```text
db/migrations/010_users.sql            authored table schema
db/migrations/011_audit_events.sql     authored table schema
db/queries/audit/events.sql            authored sqlc queries
internal/rules/audit/                  authored, pure
internal/logic/audit/append.go         authored body (created once)
internal/logic/audit/contract_gen.go   generated shape contract
internal/adapters/audit/event_store.go authored adapter
internal/operations/audit/*_gen.go     generated gate and workflow
internal/scope/                        generated capabilities
```

### Rules and logic

Rules hold decisions as pure functions; the logic body orchestrates them:

```go
package audit

// Append records one event for the verified tenant. The actor is the
// verified subject; the request cannot name one.
func Append(
	ctx context.Context,
	e scope.Execution,
	p AppendPorts,
	in models.AppendRequest,
) error {
	if !rules.ValidType(in.Type) || !rules.ValidPayload(in.Payload) {
		return fmt.Errorf("%w: event", domain.ErrInvalidInput)
	}

	return p.Events.Append(ctx, e, in)
}
```

`rules.EventHash(type, payload)` is the same pure SHA-256 helper used by
`Append`'s adapter and by `Verify`.

### Adapter

```go
type EventStore struct{ db scope.DB }

func (s *EventStore) Append(
	ctx context.Context,
	e scope.Execution,
	in models.NewEvent,
) error {
	return s.db.Write(ctx, e, func(ctx context.Context, tx scope.Tx) error {
		_, err := queriesOf(tx).AppendEvent(ctx, queries.AppendEventParams{
			OrgID:   tx.Tenant(),
			ActorID: e.SubjectID(),
			Type:    in.Type,
			Payload: []byte(in.Payload),
			Hash:    rules.EventHash(in.Type, in.Payload),
		})

		return err
	})
}
```

The matching query binds the tenant: `INSERT INTO audit_events (org_id, ...)
VALUES (@org_id, ...)`, and every read filters `WHERE org_id = @org_id`.

### Row-level security and append-only

`ARCH612` analyzes authored queries and migrations with sqlc's own parsed
catalog. For each declared table it requires every query to bind the tenant
column and every migration set to enable `FORCE ROW LEVEL SECURITY` with a policy
on the per-transaction tenant setting (`app.tenant_id`). `append_only = true`
also requires no-update and no-delete triggers. Stray query files outside a
declared set and drift in generated sqlc output fail the check.

When you add `[[tables]]` through a blueprint, Pluto proposes a new migration
with the policy and triggers for any declared table whose migrations do not yet
satisfy the check, at the next free number. Review and commit it like any other
migration. Applied migrations are never edited, and a table no migration creates
yet is an error.

### Memberships binding

`[memberships]` binds role resolution to your own table, here
`users(org_id, id, role)`. The tenant column must equal the declared table's
tenant column, and the table must be declared with forced row-level security.
Pluto generates a resolver that selects the role by subject and tenant inside a
transaction with `app.tenant_id` set, so RLS applies to the lookup. Roles in
`[[roles]]` remain a catalog: nothing assigns an actor a role until a row exists
in your table.

### Tests

The generated `scopetest` harness mints Executions for `_test.go` files only; a
production import of it is an `ARCH610` finding. Test rules as plain functions,
logic with fake ports, and adapters against a real database inside `scope.DB`.

## Verifying

```sh
pluto fmt
pluto openapi
pluto architecture check --directory . --format json
pluto vet
go test ./...
```

`pluto architecture check` and `pluto vet` run `ARCH610`–`ARCH613`: role imports
and shape, authored SQL, and migration numbering. See
[architecture mapping and migration](../maintainers/architecture-migration/) for
candidate pins and `pluto migrate`.

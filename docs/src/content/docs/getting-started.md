---
title: "Your first application"
description: "Your first application with Pluto."
---

This walkthrough targets CLI **v0.14.0**. Install Go **1.25.5+** and Git. Docker is needed when you run the generated PostgreSQL stack. Format/check commands require golangci-lint **2.15.0**, available through the generated mise setup.

## Install Pluto

```sh
go install github.com/plutoframework/cli/cmd/pluto@v0.14.0
pluto version
```

Make sure your Go installation's binary directory is on PATH. Run `pluto` in a terminal for the guided wizard. For scripts and agents, use explicit arguments with `--no-input`.

## Initialize a project

```sh
pluto --no-input init mission-control \
  --name mission-control \
  --module example.com/mission-control \
  --env-prefix MISSION_CONTROL_
cd mission-control
```

Initialization saves project choices in `pluto.toml`. Docker, mise and fnox scaffolding are included by default. Use `--no-docker --no-mise --no-fnox` to omit those presets independently. Git hooks are opt-in with `--hook`; existing hooks are protected.

Inspect generated environment templates and tool configuration before loading them. Keep real credentials out of Git. The fnox scaffold still needs your secret-provider setup.

## Add a route

```sh
pluto --no-input add endpoint launches List \
  --method GET --path /api/launches \
  --name 'List launches' \
  --description 'List launches visible to the verified caller.' \
  --permission launches:read
```

`GET List` generates a paginated collection by default. The command adds route metadata, HTTP adapters, models, operation code and tests, then regenerates OpenAPI.

**Generated operations intentionally return not implemented.** Implement the application operation and its tests. Supply your authentication, membership and role grants; declaring a permission does not grant it to anyone. Read the [CLI reference](../cli/reference/) for the generated dependency boundaries.

## Add a lifecycle

```sh
pluto --no-input add state launches
```

Edit `internal/domain/launches/lifecycle.go` for your actual domain. It starts with a draft/submitted lifecycle and ownership guard. Inject its compiled machine into an operation, prepare facts from verified identity and loaded records, and persist successful decisions with an expected-version check, audit and outbox transaction.

## Check the application

```sh
pluto fmt
pluto vet
go test ./...
go run ./cmd/openapi
```

Migrations are explicit. Inspect and apply the generated database migrations before starting the API; startup does not create database schema. See the generated README and [deployment guide](../deployment/) for prerequisites.

## Add a frontend

```sh
pluto --no-input frontend init --ui heroui-v3
```

The profile is saved in `pluto.toml`. Native and shadcn profiles are also available. `--auth` requires a backend already initialized with `--local-credentials`. Use `--dry-run` to preview or `--no-install` to write files without running npm. See [frontend profiles](../frontend/profiles/).

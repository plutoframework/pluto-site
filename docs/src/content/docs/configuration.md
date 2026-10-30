---
title: Configuration
description: Configure project choices and runtime settings in Pluto.
---

Pluto saves generator choices in `pluto.toml`. Runtime settings come from your application's config package and environment.

## Project settings

Set the application name, module and environment prefix when initializing:

```sh
pluto init mission-control \
  --name mission-control \
  --module example.com/mission-control \
  --env-prefix MISSION_CONTROL_
```

The generated manifest records these choices so later commands can reuse them.

| Section        | Purpose                                                   |
| -------------- | --------------------------------------------------------- |
| `project`      | Application name, Go module and environment prefix        |
| `capabilities` | Tenancy, optional cache backend and local credentials     |
| `development`  | Docker, mise and fnox scaffold choices                    |
| `endpoints`    | Route metadata, permission, feature and collection intent |
| `jobs`         | Background handler definitions                            |
| `agents`       | Generated agent definitions                               |
| `frontend`     | UI profile, theme and component registry settings         |

Prefer CLI commands for adding generated features. Editing a manifest alone does not migrate authored files. Unsupported schemas and changed generated contracts are rejected before generation.

## Environment variables

Use your saved prefix for application variables. For example, the `launches-export` feature key in a project with the `MISSION_CONTROL_` prefix maps to:

```sh
export MISSION_CONTROL_FEATURE_LAUNCHES_EXPORT=true
```

Use the generated `.env.example` as the source of supported runtime names. Load and validate settings once at startup, then inject them into the application.

Keep credentials in your chosen secret provider. Commit templates and nonsecret project choices; exclude real secret values from version control.

## Feature overrides

New scaffolded feature flags default to false. A present environment override wins over the default, including an explicit false. Malformed boolean values fail startup. Core also supports ordered override maps, with the rightmost present value winning.

See [feature flags](../backend/features/) for declaration, visibility and precedence details. Feature visibility in the UI does not grant API permissions.

## Frontend settings

Choose the component profile when initializing the frontend:

```sh
pluto frontend init --ui heroui-v3
```

Pluto saves that choice for subsequent component commands. Configure [theme tokens](../frontend/themes/) and [local component registries](../frontend/registries/) in the manifest. These are build-time frontend settings, so changes require the documented generation/build step.

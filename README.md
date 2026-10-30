<p align="center">
  <img src="https://raw.githubusercontent.com/plutoframework/pluto/main/assets/readme/banner.svg" alt="Pluto — a small framework, wide open possibilities" width="100%" />
</p>

# Pluto Site

The public home and field guide for the Pluto ecosystem. Warm paper, ink-blue
space illustrations and practical, task-first documentation.

[Website](https://plutoframework.github.io/pluto-site/) · [Documentation](https://plutoframework.github.io/pluto-site/docs/index/) · [CLI demo](https://github.com/plutoframework/pluto/blob/main/docs/DEMO.md) · [First issues](https://github.com/plutoframework/pluto/blob/main/CONTRIBUTING.md#starter-tasks)

## What lives here

- A static product page with original orbital illustrations and self-hosted fonts.
- Starlight guides and versioned snapshots of package references.
- One plain Markdown export per topic, discoverable through `llms.txt`.
- GitHub Pages deployment with link, build and published-CLI smoke checks.

## Work locally

### 1. Install docs tooling

```sh
git clone https://github.com/plutoframework/pluto-site.git
cd pluto-site
mise exec node@24.22.1 -- npm --prefix docs ci
```

### 2. Preview documentation

```sh
mise exec node@24.22.1 -- npm --prefix docs run dev
```

Use the local URL printed by Astro. For the product page and assembled Pages
subpath preview, follow [the maintenance guide](docs/MAINTAINING.md).

### 3. Check a change

```sh
mise exec node@24.22.1 -- npm --prefix docs run build
python3 scripts/check.py
python3 scripts/build-site.py
python3 scripts/check-docs.py
```

Reference snapshots come from committed sibling `origin/main` revisions; CI uses the reviewed,
checked-in content. Refresh only the intended sources and inspect the diff.

## Write for people and agents

Follow [WRITING.md](docs/WRITING.md). Lead with the task and a working example;
keep prerequisites, versions and limitations explicit. Link the canonical topic
instead of copying manuals into skills or README files.

## Contribute

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and a [good first issue](https://github.com/plutoframework/pluto/blob/main/CONTRIBUTING.md#starter-tasks).
Self-hosted font licenses remain in [assets/fonts](assets/fonts).

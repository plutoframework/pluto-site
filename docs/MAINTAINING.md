# Pluto site

The public, static product site for the Pluto Go API framework and CLI, including its separate React frontend scaffold.

- Website: <https://plutoframework.github.io/pluto-site/>
- Repository: <https://github.com/plutoframework/pluto-site>
- Product sources: <https://github.com/plutoframework>

## Run locally

The landing page can be previewed without a build:

```sh
cd pluto-site
python3 -m http.server 4173 --bind 127.0.0.1 --directory ..
```

Open <http://127.0.0.1:4173/pluto-site/>. Serving from the parent directory
reproduces the GitHub Pages project subpath. All local assets use relative URLs.

## Check and capture

```sh
python3 scripts/check.py
npm ci
npm run capture
```

The capture command is optional developer tooling. It requires Google Chrome
and the local server above. It uses Playwright only for browser QA; no JavaScript
package ships to visitors. `SITE_ORIGIN` can override the server origin, while
retaining `/pluto-site/` as the path. `npx prettier --check index.html styles.css
responsive.css script.js scripts/capture.mjs` checks source formatting.

`capture` checks local asset responses, font loading, console errors, overflow at
320/390/768/1024/1440px, code tabs and keyboard navigation, mobile menu and Escape,
quickstart navigation, a guide disclosure, clipboard success and rejection,
manual copy selection, skip navigation, visible keyboard focus and reduced motion.
It refreshes `evidence/` and the original social preview image `assets/social.png`.
Evidence is deliberately excluded from the public Pages artifact.

## Design and content

A mission-atlas art direction: warm paper, ink blue, signal orange, fine grid
rules and original code-native planetary/orbit illustrations. Self-hosted
Bricolage Grotesque, Manrope and IBM Plex Mono fonts are distributed under their
SIL Open Font Licenses in `assets/fonts/`. No remote font request, tracking,
analytics, form submission or backend is included.

The page includes accessible code tabs, an installation command with clipboard
feedback and manual fallback, a small quickstart guide, mobile navigation and
links to real public source repositories. Semantic sections, focus styles,
reduced-motion support and native disclosure elements are included.

CLI syntax and excerpts were checked against the local CLI README, Cobra
commands and endpoint templates. Examples are marked as excerpts where code
is omitted. The CLI is a changing preview: generated operations intentionally
remain unimplemented, authentication and role grants require application wiring,
and migrations remain explicit. The site makes no benchmark, adoption,
independent audit or production-readiness claims. Frontend copy is verified against CLI v0.7.0 (9cd36a1), its README, docs/THEMES.md and docs/COMPONENT-REGISTRIES.md. It covers native/HeroUI v3/shadcn profiles, typed bindings, the build-time theme pipeline and local registries. Auth screens require an already enabled local-credential backend. Registry packs are local; existing frontend source is never implicitly migrated.

## Deployment

GitHub Pages is configured with `build_type=workflow`. Push to `main`, or run:

```sh
gh workflow run pages.yml --repo plutoframework/pluto-site
gh run list --repo plutoframework/pluto-site --workflow pages.yml --limit 5
```

`.github/workflows/pages.yml` checks the static site, assembles `_site/`, uploads
the Pages artifact and deploys it. The workflow builds Starlight with pinned Node dependencies, compiles the documented
CLI workflow, checks links and combines the landing page and documentation in `_site/`. Deployment has
`pages:write` and `id-token:write`; the build has read-only repository access.
A dedicated concurrency group prevents competing deployments. No custom domain
is configured.

## Validation evidence

Browser captures and the machine-readable check report are in `evidence/`:

- [Desktop hero](../evidence/desktop.png)
- [Full desktop page](../evidence/desktop-full.png)
- [Mobile hero](../evidence/mobile.png)
- [Full mobile page](../evidence/mobile-full.png)
- [Frontend desktop](../evidence/frontend-desktop.png)
- [Frontend mobile](../evidence/frontend-mobile.png)
- [Desktop code demo](../evidence/code-demo.png)
- [Mobile code demo](../evidence/mobile-code.png)
- [Mobile guide](../evidence/mobile-guide.png)
- [Browser check report](../evidence/browser-check.json)

The T3 native preview opened the local page, but snapshot inspection timed out
twice with `Preview automation snapshot timed out after 15000ms.` Local Chrome
was used for visual inspection and captures after those failures. The browser
checks verify site behavior, not the Go product's implementation. No backend,
Go package test suite or assistive-technology certification is implied.

## Documentation

The docs live at https://plutoframework.github.io/pluto-site/docs/ and use
Astro Starlight. Node 24.22.1 is pinned in CI; dependencies are frozen in
`docs/package-lock.json`. No server is required for the published output.

```sh
mise exec node@24.22.1 -- npm --prefix docs ci
mise exec node@24.22.1 -- npm --prefix docs run build
python3 scripts/build-site.py
python3 scripts/check-docs.py
python3 scripts/docs-smoke.py
```

Serve `_site/` under `/pluto-site/` to reproduce the Pages base path. For authoring,
`npm --prefix docs run dev` starts Astro's docs-only development server.

Guides are authored Markdown in `docs/src/content/docs`. Reference pages are
snapshots from committed package revisions recorded in `docs/sources.json`.
Run `python3 scripts/sync-docs.py` with the sibling repositories checked out to
refresh them, review the diff, and rebuild. CI needs only this repository and
never reads local environment or fnox files. See `docs/WRITING.md` for the
OpenCode-inspired editorial conventions. Search is indexed locally at build time.

The docs link checker verifies all local HTML targets/assets across the assembled
site. The smoke check installs the public CLI v0.11.0 and compiles the documented
endpoint + lifecycle workflow in a disposable project. These checks run on Pages
builds. The site currently has one guide set with explicit reference revisions;
it does not advertise historical version switching.

## Published reference sources

Fetch the intended sibling repositories before `python3 scripts/sync-docs.py`.
The script reads their committed `origin/main` revisions, not local working trees.
Long package references live in `docs/REFERENCE.md`; GitHub READMEs are the short
entrypoints. Review snapshot revisions and source links before committing.

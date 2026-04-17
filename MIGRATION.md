# jupyter-cadquery marimo migration plan

## Goal

Convert this repository from a JupyterLab or Jupyter Server extension package into a marimo-first CAD workflow package.

The final state should satisfy all of the following:

- the runtime path is marimo-specific
- the supported notebook UX aims for parity with the current Jupyter user experience except for JupyterLab sidecar or docked-panel behavior, which marimo does not provide natively
- the Python package does not require JupyterLab, Jupyter Server, IPython shell APIs, or ipywidgets at runtime
- measurement and backend communication no longer depend on Jupyter extension endpoints
- notebook examples are marimo notebooks (or marimo scripts) as the primary supported format
- the README explains marimo setup and execution
- packaging metadata and repository docs no longer advertise Jupyter runtime support
- the package does not support Jupyter as a runtime after migration

## Conceptual map

This repository sits above rendering and tessellation libraries and below the notebook host runtime:

1. `ocp_tessellate` and related geometry tooling provide CAD conversion and tessellation.
2. `cad-viewer-widget` (after its own marimo migration) provides the viewer bridge and rendering surface.
3. `jupyter-cadquery` orchestrates high-level show APIs, backend measurement flow, and user notebook UX.
4. Jupyter or marimo is the host runtime.

In the current codebase, layer 3 is tightly coupled to Jupyter runtime assumptions:

- Python entrypoints expose Jupyter server extension hooks (`_jupyter_server_extension_points`, `_load_jupyter_server_extension`)
- backend HTTP handlers derive from `jupyter_server` extension classes (`ExtensionApp`, `JupyterHandler`)
- comms rely on Jupyter process state (`_xsrf`, `JUPYTER_PORT`, `JUPYTER_CADQUERY_API_KEY`)
- auto-display wiring targets IPython shell hooks (`_ipython_display_`)
- replay functionality uses `IPython.display` and `ipywidgets`

In marimo, the target model is:

- `show(...)`, `show_object(...)`, and viewer configuration remain stable for callers
- backend interaction is host-agnostic (direct/in-process or explicit transport abstraction)
- examples run via marimo without Jupyter extension registration
- interactive CAD workflows remain available in marimo for inline rendering, measurement, picking, animation, replay, and build123d usage, unless a capability is proven impossible in marimo itself
- sidecar-specific placement semantics (`anchor`, docked panels, split panes, shell-managed viewer regions) are not preserved as behavioral goals

## Feature parity target

The migration should preserve the current notebook experience as closely as marimo allows.

Required parity targets:

1. Inline object rendering via `show(...)` and `show_object(...)` for CadQuery, build123d, and supported OCP objects.
2. Viewer configuration parity for the existing supported config surface, including camera, clipping, appearance, tree behavior, and renderer settings.
3. Measurement and object-picking workflows that are usable from marimo without Jupyter server endpoints.
4. Auto-display behavior for CadQuery and build123d objects, using a marimo-safe display mechanism rather than IPython shell hooks.
5. Replay support for CadQuery where the workflow remains practical in marimo.
6. Animation workflows that currently exist for CadQuery and build123d assemblies, including track registration and playback where supported by the viewer layer.
7. Representative build123d workflows, not just import success: `BuildPart`, `BuildSketch`, `BuildLine`, `ShapeList`, joints, and local-sketch rendering paths should still work if they worked before migration.

Explicitly unsupported parity target:

1. JupyterLab sidecar and docked-window UX, including `anchor` semantics tied to the Jupyter shell layout.

If a feature cannot be supported in marimo, the burden of proof is on the migration work:

1. show that marimo lacks the host capability or that the lower-level viewer stack cannot support it without a separate redesign
2. document the degraded behavior explicitly in README and examples
3. remove or narrow the API deliberately rather than silently keeping a misleading surface

## Future interoperability guardrails

This migration must preserve compatibility seams with adjacent packages, especially `cad-viewer-widget` and `ocp_vscode`.

Keep these seams stable while removing Jupyter runtime dependencies:

1. Preserve a framework-neutral `show(...)` contract and parameter behavior.
2. Preserve payload schema expectations used by `cad-viewer-widget` and `ocp_vscode`.
3. Isolate measurement/backend communication behind a transport-agnostic interface.
4. Keep CAD conversion, tessellation, and replay data semantics independent from notebook host specifics.
5. Avoid embedding marimo UX decisions into low-level protocol internals.
6. Preserve build123d-specific rendering and interaction semantics that do not depend on Jupyter shell APIs.
7. Do not keep Jupyter as a supported runtime path or fallback mode.

Explicit non-goals:

- Do not redesign `ocp_tessellate` payload structures in this migration.
- Do not add temporary compatibility shims intended for later removal.
- Do not preserve Jupyter runtime compatibility.
- Do not emulate JupyterLab sidecars if the result is only a misleading inline fallback.

## Scope rules

Each milestone below is intentionally sized to about one commit.

- Do not combine multiple milestones into one large refactor.
- No compatibility shims. Remove old Jupyter paths directly.
- A milestone may be non-functional if the breakage is narrow and intentional.
- Minimize rework by touching each subsystem once whenever possible.
- Delay broad docs refresh until the final cleanup milestone.

## Touch-once strategy

To avoid churn, execute subsystem cutovers in this order:

1. Public Python runtime cutover
2. Backend transport cutover
3. Packaging and metadata cutover
4. Notebook and validation cutover
5. Final docs and repository purge

Within each cutover:

- remove Jupyter-specific behavior immediately
- avoid dual-runtime branches
- keep tests local and narrow to touched files
- preserve public API behavior required by existing callers

## Quality gates for every milestone

Every milestone should clear these gates before moving on:

1. Milestone-specific testing step passes.
2. Commit message states any intentionally broken subsystem.
3. No compatibility wrappers are added.
4. Files outside the subsystem are untouched unless required wiring/import updates are needed.
5. No new Jupyter references are introduced.
6. Public API contracts are preserved or explicitly versioned.
7. No feature that marimo can support is silently dropped without an explicit decision and documentation update.

## Milestones

### Milestone 1: Python runtime API cutover (remove host-specific bootstrap)

Purpose:

- remove Jupyter bootstrap and shell-coupled initialization from core runtime imports
- keep user-facing API (`show`, `show_object`, config helpers) stable

Touched files:

- `jupyter_cadquery/__init__.py`
- `jupyter_cadquery/show.py`
- `jupyter_cadquery/tools.py`
- `jupyter_cadquery/replay.py`

Work:

- remove Jupyter server extension registration functions from `__init__.py`
- remove runtime assumptions tied to IPython shell detection and Jupyter-only environment flags
- replace `_ipython_display_` auto-hook behavior with marimo-safe display registration strategy
- remove or refactor replay paths requiring `IPython.display` or `ipywidgets`
- preserve or deliberately replace auto-display behavior for both CadQuery and build123d objects
- keep replay as a supported feature unless marimo constraints are proven and documented
- preserve public imports and callable surfaces where practical

Testing step:

1. `python -m py_compile jupyter_cadquery/*.py`
2. `rg -n "_jupyter_server_extension_points|_load_jupyter_server_extension|get_ipython|IPython.display|ipywidgets" jupyter_cadquery`
3. confirm no required runtime path depends on those symbols

Completion check:

- top-level Python runtime imports are host-agnostic
- public show-level API remains callable and stable
- CadQuery and build123d objects still have a practical marimo display path without manual Jupyter hooks
- replay is either working in marimo or explicitly removed with corresponding docs and example updates

### Milestone 2: backend measurement transport cutover (remove jupyter_server extension layer)

Purpose:

- remove `jupyter_server` extension app and request handlers
- preserve measurement/backend capability behind a transport-agnostic seam

Touched files:

- `jupyter_cadquery/app.py`
- `jupyter_cadquery/comms.py`
- `jupyter_cadquery/__init__.py` (import wiring only)
- `jupyter-config/jupyter_server_config.d/jupyter_cadquery.json` (remove in this milestone)

Work:

- replace `ExtensionApp`/handler-based backend flow with marimo-compatible transport strategy
- remove `_xsrf` and Jupyter-port/API-key coupling where possible
- keep message shape and command semantics stable for frontend interactions
- ensure `send_backend` and `send_measure_request` use new backend seam without Jupyter server extension dependency
- preserve measurement and picking workflows used by the viewer, not just raw message transport

Testing step:

1. `python -m py_compile jupyter_cadquery/*.py`
2. `rg -n "jupyter_server|ExtensionApp|JupyterHandler|_xsrf|JUPYTER_PORT|JUPYTER_CADQUERY_API_KEY" jupyter_cadquery jupyter-config`
3. run a minimal `show(...)` path, one measurement request path, and one object-picking path in a local dev environment

Completion check:

- backend communication no longer requires Jupyter extension registration
- measurement path remains available through a host-agnostic transport seam
- measurement and picking are usable from marimo notebook workflows

### Milestone 3: packaging and metadata cutover (drop jupyter install hooks)

Purpose:

- remove Jupyter build/install metadata and dependencies from packaging
- align package metadata with marimo runtime and retained libraries

Touched files:

- `pyproject.toml`
- `MANIFEST.in`
- `requirements.txt`
- `runtime.txt`
- `jupyter-config/` (delete any remaining config artifacts)

Work:

- remove Jupyter-focused build hooks, classifiers, keywords, and runtime deps
- remove bundled Jupyter server config data from wheel metadata
- keep required CAD, tessellation, and viewer dependencies
- ensure package install works without JupyterLab/Jupyter Server
- ensure packaging metadata clearly describes marimo-first support and does not imply Jupyter compatibility

Testing step:

1. create fresh virtual environment
2. `python -m pip install -U pip`
3. `python -m pip install -e .`
4. `python -c "import jupyter_cadquery; print('import ok')"`
5. `rg -n "jupyter|jupyterlab|jupyter_server|ipython|ipywidgets|labextension|nbextension" pyproject.toml MANIFEST.in requirements.txt jupyter-config`

Completion check:

- package metadata no longer defines Jupyter extension wiring
- editable install and import succeed without Jupyter runtime packages
- install metadata does not imply Jupyter support or fallback support

### Milestone 4: notebook and notebook validation cutover (marimo-first examples)

Purpose:

- replace or archive Jupyter notebooks as primary examples
- establish marimo notebook/script smoke testing

Touched files:

- `examples/` (convert selected `.ipynb` examples to marimo `.py` notebooks)
- `notebooks/` (convert existing notebook assets to marimo format or archive)
- `validate_nb.py`
- `Makefile` (notebook validation targets)

Work:

- create marimo examples covering CadQuery render, build123d render, viewer config update, measurement or pick workflow, and one animation or replay workflow if those features remain supported
- preserve representative examples for CadQuery/build123d usage, including at least one example that exercises build123d-specific behavior rather than generic shape rendering only
- update notebook validation helper to validate marimo artifacts, not only classic notebook JSON
- keep one fast smoke-test path for CI/local verification
- explicitly rewrite or remove sidecar-oriented examples so they do not imply Jupyter shell behavior still exists

Testing step:

1. `marimo edit examples/1-cadquery.py`
2. `marimo run examples/1-cadquery.py`
3. `marimo run examples/5-build123d.py`
4. verify CadQuery and build123d objects render and that at least one non-render interaction path works
5. run updated validation command from `Makefile`

Completion check:

- marimo artifacts are the primary supported notebook workflow
- notebook validation no longer assumes `.ipynb` only
- example coverage demonstrates retained CadQuery and build123d workflows, not just basic import or rendering
- examples and docs no longer suggest sidecar parity where marimo cannot provide it

### Milestone 5: final docs pass and repository purge

Purpose:

- align all docs and release instructions with marimo-only runtime
- remove stale Jupyter wording and unsupported setup steps

Touched files:

- `README.md`
- `RELEASE.md`
- `CHANGELOG.md` (if needed for migration note)
- `doc/*.md`
- `docker/Dockerfile` and `docker/run.sh` (if runtime commands reference Jupyter)

Work:

- replace Jupyter installation and verification instructions with marimo flow
- document explicit quickstart commands for marimo edit/run
- remove Jupyter extension validation commands from docs
- ensure screenshots/examples still match supported runtime behavior
- add a clear parity statement: marimo is the only supported host, sidecar behavior is intentionally not retained, and all other retained features are documented as supported or unsupported
- document any intentionally removed feature with the reason it is unsupported in marimo

Testing step:

1. follow README from a clean shell
2. run documented install commands
3. run `marimo edit` and `marimo run` on one migrated example
4. verify no missing commands or stale references

Completion check:

- new contributors can run the package through marimo using only README instructions
- docs make the non-support of Jupyter explicit
- docs distinguish between retained parity features and the intentional sidecar exception

## Recommended testing matrix

Use this matrix during migration:

1. Python syntax check for touched files: `python -m py_compile jupyter_cadquery/*.py`
2. Import smoke test in clean venv: `python -c "import jupyter_cadquery"`
3. Search purge check: `rg -n "jupyter|jupyterlab|jupyter_server|IPython.display|ipywidgets|labextension|nbextension" .`
4. marimo notebook startup check: `marimo run examples/1-cadquery.py`
5. build123d notebook startup check: `marimo run examples/5-build123d.py`
6. one measurement-path smoke test using the new transport seam
7. one picking-path smoke test using the new transport seam
8. one replay or animation smoke test if those features remain supported

## Completion verification

Migration is complete only when all are true:

1. `python -m pip install -e .` succeeds in a fresh virtualenv without pulling JupyterLab as a required runtime dependency.
2. `import jupyter_cadquery` works without Jupyter server extension registration.
3. marimo examples run successfully via `marimo run`.
4. measurement/backend flow functions through the non-Jupyter transport seam.
5. README includes complete marimo setup and run steps.
6. `rg -n "jupyter|jupyterlab|jupyter_server|IPython.display|ipywidgets|labextension|nbextension" .` returns no supported-runtime references.
7. no required runtime code path depends on Jupyter extension APIs, shell hooks, or server config wiring.
8. `show(...)` and payload contracts remain stable for consumers and adjacent packages.
9. build123d workflows remain usable in marimo, including at least one build123d-specific example and one build123d-specific rendering option.
10. replay, animation, measurement, and picking are either working in marimo or explicitly removed with documentation and example updates that explain why.
11. sidecar-specific Jupyter shell behavior is either removed from the API surface or documented as intentionally unsupported; it is not presented as retained parity.
12. Jupyter is not supported as a runtime, is not tested as a runtime, and is not advertised as a runtime.

## Suggested commit order

Use this order to minimize rework:

1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5

This order removes host coupling first, then backend transport, then packaging, then user-facing artifacts and docs.

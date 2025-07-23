# Universal LLM Safeguard — Master To-Do List

## Codebase

- [ ] Refactor to dynamic filter registry, robust error handling, add hooks, swap to logger.
- [ ] Refactor all pipelines to use orchestrator; flag and deprecate legacy/test pipelines.
- [ ] Implement output (post-response) filtering in all adapters (FastAPI, Flask, Django).
- [ ] Always log model load failures; add fallback if model can't load; clarify classifier thresholds in docs.
- [ ] Add regex error handling in keyword filter; document config fragility (regex compile errors).
- [ ] Switch all print debugging to logger utility.
- [ ] Add log rotation or archiving to logger; add error handling for log writes.
- [ ] Support more granular anonymization in logging.
- [ ] Upgrade FilterResult to match full manifest output (flags, reasons, override, etc.) in middleware/adapters.
- [ ] Plan for async support in middleware and filters.
- [ ] Plan for context/user/session support in middleware.
- [ ] Add test coverage for edge cases: model failures, config errors, override abuse.
- [ ] Add test coverage summary to contributor docs.
- [ ] Remove unused/legacy dependencies from `pyproject.toml`.
- [ ] Mark optional adapters and extras in `pyproject.toml`.
- [ ] Exclude build, venv, test, and dist dirs from package/repo.
- [ ] Warn if override phrases are too short/simple (config and docs).
- [ ] Validate all keys used by orchestrator/filters are present in config.
- [ ] Ensure all test/example code in docs is runnable and up-to-date.
- [ ] Flag all legacy/test modules and pipelines as non-canonical in docs and code comments.

## Documentation & Manifest/Trinity

- [ ] README: update install/examples to match codebase, add Known Issues, reference Trinity docs and explain role, ensure all modules referenced are live.
- [ ] Update all .md/.txt docs for drift: remove references to dead code, old structure, or unimplemented features.
- [ ] Ensure all docs (manifesto, plan, blueprints, specs) are honest about capabilities, gaps, and roadmap.
- [ ] All Trinity docs (manifesto, plan, seed) must explicitly reference and match codebase, pipeline, config, and output fields.
- [ ] Add/clarify test coverage and manual test steps to Integration/Testing doc.
- [ ] Sync File Tree and Module Blueprint doc with live repo structure.
- [ ] Add "Known Issues" section to Safeguard_OS.md and README.
- [ ] Add phase/step alignment table to Phase Plan doc.
- [ ] Remove or finish all "TODO", placeholder, or stubbed sections before release.
- [ ] All modules/functions/config described in docs must exist in codebase with matching API/output.
- [ ] All instructions, examples, and configs in docs must have been run and verified.
- [ ] All docs must state which Trinity files/version/commit they are aligned to.

## General & Cross-Cutting

- [ ] Overclaiming privacy, audit, or safety beyond what the codebase actually delivers is a release blocker.
- [ ] Document all known limitations and MVP/future boundaries in both code and docs.
- [ ] Every phase in Phase Plan must be kept in sync with live repo status.
- [ ] All docs must use clear, transparent, non-ambiguous language (no misleading or vague text).
- [ ] Regenerate `filelist.txt` and status/audit docs before each release.
- [ ] Remove any empty stubs or placeholder files.

---

> All tasks above are sourced directly from line-by-line code and docs audit.
> Mark off or delegate each item before public release or major version bump.

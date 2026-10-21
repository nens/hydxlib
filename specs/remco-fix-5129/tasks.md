---
feature: remco-fix-5129
status: planned
created: 2026-10-21
chunk_size: medium
total_tasks: 8
estimated_lines: 480
---

# GWSW Import Feedback Tasks

## Overview

Implement the confirmed GWSW HydX importer improvements for Rana HCC: target-schematisation friction lookup, HydX visualization mappings, lateral discharge import, provenance tags, and preserved-GWSW-class support where the input format provides that information. Every behavior change includes regression coverage. Production GeoPackages remain outside Git.

## Task List

### Foundation

#### Task 1: Define target material friction lookup
- **Estimate:** ~60 lines
- **Files:** `hydxlib/exporter.py`, `hydxlib/tests/test_exporter.py`, `hydxlib/tests/conftest.py`
- **Description:** Read the target Rana `material` table during export and create a lookup containing material ID, friction type, and friction coefficient. Define fallback defaults for missing configuration and log fallback use. Apply resolved friction values before constructing `Pipe` objects.
- **Depends on:** None
- **Acceptance:** Target material values override defaults; configured values populate both friction fields; missing configuration uses a documented fallback.
- **Evidence:** Focused exporter tests pass for customized, configured, and fallback cases.

#### Task 2: Verify lateral schema and endpoint semantics
- **Estimate:** ~50 lines
- **Files:** `hydxlib/threedi.py`, `hydxlib/exporter.py`, `hydxlib/tests/test_threedi.py`, `hydxlib/tests/test_exporter.py`
- **Description:** Confirm how static `DEB_TYP=LAT` records map to Rana `Lateral1D`, including no-timeseries behavior and resolution of a `Debiet.UNI_IDE` matching a connection. Use the installed schema and current CSV fixture only.
- **Depends on:** None
- **Acceptance:** Tests document that every HydX `DEB_TYP=LAT` record becomes a Rana `Lateral1D`, including static records without a timeseries, and document the downstream endpoint convention for connection references without fabricating an unsupported timeseries.
- **Evidence:** Focused schema/conversion tests pass.

### Core Implementation

#### Task 3: Add OPL and ITR visualizations [P]
- **Estimate:** ~55 lines
- **Parallel:** Can run with Task 4 after Task 1.
- **Files:** `hydxlib/threedi.py`, `hydxlib/tests/test_threedi.py`
- **Description:** Map `OPL -> 9` for Goot/slot or trench drain and `ITR -> 8` for infiltration drain. Preserve profile validation, sewerage mapping, material mapping, and ordinary `GSL` behavior.
- **Depends on:** Task 1
- **Acceptance:** `OPL` and `ITR` receive the requested visualization values; ordinary `GSL` remains unchanged; profile validation remains active.
- **Evidence:** Unit tests pass for `OPL`, `ITR`, ordinary `GSL`, and profile validation.

#### Task 4: Implement LAT lateral conversion [P]
- **Estimate:** ~75 lines
- **Parallel:** Can run with Task 3 after Task 2.
- **Files:** `hydxlib/threedi.py`, `hydxlib/exporter.py`, `hydxlib/tests/test_threedi.py`, `hydxlib/tests/test_exporter.py`
- **Description:** Add an internal `laterals` collection, branch discharge handling on `DEB_TYP`, convert `LAT` records to `Lateral1D`, preserve non-lateral behavior, resolve node/connection identifiers, skip unresolved records with errors, and add export counts.
- **Depends on:** Task 2
- **Acceptance:** The three supplied `LAT` records become Rana `Lateral1D` objects; non-`LAT` records remain impervious surfaces; unresolved identifiers are logged and skipped.
- **Evidence:** Importer and exporter tests pass against the supplied CSV fixture and temporary schema.

#### Task 5: Add importer provenance tags
- **Estimate:** ~60 lines
- **Files:** `hydxlib/threedi.py`, `hydxlib/exporter.py`, `hydxlib/tests/test_threedi.py`, `hydxlib/tests/test_exporter.py`
- **Description:** Add one stable provenance tag, such as `gwsw-hydx-import`, to nodes, pipes, pumps, weirs, orifices, outlets, surfaces, dry-weather flows, and laterals using the Rana schema’s tag representation.
- **Depends on:** Task 4
- **Acceptance:** Every exported object type receives the importer tag without replacing unrelated existing tags.
- **Evidence:** Exporter tests inspect constructed or persisted model objects for the tag.

#### Task 6: Preserve and map GWSW classes
- **Estimate:** ~80 lines
- **Files:** `hydxlib/hydx.py`, `hydxlib/threedi.py`, `hydxlib/tests/test_hydx.py`, `hydxlib/tests/test_threedi.py`
- **Description:** After confirming the actual new export header, add optional preserved-class support and map `Trottoirkolk -> node visualization 4`, `Kolkaansluitleiding -> pipe other`, and `Overstortleiding -> pipe visualization 4`. Do not infer classes from identifiers, geometry, names, or generic HydX codes.
- **Depends on:** Task 3
- **Acceptance:** Explicit class metadata produces requested mappings; ordinary `GSL` remains ordinary; current fixtures without metadata remain backward compatible; incomplete records follow current validation behavior.
- **Evidence:** Unit tests cover all classes, absent metadata, ordinary `GSL`, and incomplete records.

### Integration and Verification

#### Task 7: Run end-to-end feedback regression suite
- **Estimate:** ~60 lines
- **Files:** `hydxlib/tests/test_importer.py`, `hydxlib/tests/test_exporter.py`, `hydxlib/tests/test_threedi.py`
- **Description:** Exercise the complete import/export path with the supplied CSV directory or a copied test fixture. Assert object counts, lateral presence, visualization values, target-material friction values, and importer tags without adding real GeoPackages.
- **Depends on:** Tasks 1, 3, 4, 5, and 6
- **Acceptance:** End-to-end output contains supported expected objects and values; invalid records do not crash the run; production files remain untracked.
- **Evidence:** `pytest hydxlib --cov` passes and `git status --short` shows no production GeoPackage added.

#### Task 8: Document settled conversion behavior
- **Estimate:** ~40 lines
- **Files:** `.minispec/knowledge/architecture.md`, `.minispec/knowledge/conventions.md`, `.minispec/knowledge/glossary.md`, `.minispec/knowledge/decisions/gwsw-import-feedback-design.md`
- **Description:** Record final friction lookup, visualization mappings, lateral semantics, tag format, and unresolved HydX class limitations. Keep documentation aligned with tested behavior.
- **Depends on:** Task 7
- **Acceptance:** Documentation distinguishes HydX-defined behavior from Rana-specific behavior and documents fallback behavior without claiming unsupported mappings.
- **Evidence:** Documentation review confirms all feedback points and referenced commands are accurate.

#### Task 9: Fix geometry serialization and CRS validation
- **Estimate:** ~70 lines
- **Files:** `hydxlib/exporter.py`, `hydxlib/tests/test_exporter.py`, `hydxlib/tests/conftest.py`
- **Description:** Replace or correct the manual EWKT geometry serialization that currently produces GeoAlchemy SQLite parse warnings. Validate the source and target CRS/units so local or millimetre-like HydX coordinates are not silently written as EPSG:28992 metre coordinates. Use a small synthetic geometry test rather than production GeoPackages.
- **Depends on:** Task 7
- **Acceptance:** Exported point and line geometries are valid for the target schema, SRIDs are preserved, known coordinate-unit mismatches are detected or handled explicitly, and the exporter tests no longer emit the current geometry parse warnings.
- **Evidence:** Focused geometry tests pass, including coordinate bounds/CRS assertions, and the exporter test suite completes without GeoAlchemy WKT warnings.

## Dependencies and Parallelization

- Tasks 1 and 2 are independent foundation work.
- Tasks 3 and 4 can proceed in parallel after their foundations.
- Task 5 depends on Task 4.
- Task 6 depends on Task 3 and confirmation of the actual class field.
- Task 7 waits for implementation tasks.
- Task 8 is last.
- Task 9 follows Task 7 and may run alongside Task 8 if documentation does not depend on its final implementation details.

## Notes

- The setup script initially ran on protected `master`; this branch-specific plan is now stored under `specs/remco-fix-5129/`.
- `Margraten.gpkg`, `hmm.gpkg`, and `remco test gwsw import.gpkg` are existing untracked files and must not be committed.
- Manning values must be read from the target Rana `material` table on every run. Built-in values are fallback defaults only.
- HydX does not define Rana visualization numbers or Manning coefficients.
- `Trottoirkolk`, `Kolkaansluitleiding`, and `Overstortleiding` cannot be safely distinguished from current CSVs unless class information is preserved.

## Progress

- [x] Task 1: Define target material friction lookup
- [ ] Task 2: Verify lateral schema and endpoint semantics
- [ ] Task 3: Add OPL and ITR visualizations
- [ ] Task 4: Implement LAT lateral conversion
- [ ] Task 5: Add importer provenance tags
- [ ] Task 6: Preserve and map GWSW classes
- [ ] Task 7: Run end-to-end feedback regression suite
- [ ] Task 8: Document settled conversion behavior
- [ ] Task 9: Fix geometry serialization and CRS validation

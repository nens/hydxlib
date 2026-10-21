# GWSW Import Feedback Design

**Status:** Planned

## Context

The GWSW HydX importer converts HydX CSV files into a Rana HCC schematisation using the Rana/3Di schema. The HydX standard defines exchange fields and codes, while Rana-specific visualization, friction, and provenance behavior is defined by this importer and the target schematisation.

The current example CSV files are in `~/src/rdc/data/5129/gwsw_files/`. `Margraten.gpkg` is production data and must not be committed to Git or used as a checked-in fixture.

The target Rana GeoPackage contains the authoritative material configuration:

- `material.id`
- `material.description`
- `material.friction_type`
- `material.friction_coefficient`

New pipe rows receive the resulting values in:

- `pipe.material_id`
- `pipe.friction_type`
- `pipe.friction_value`

## HydX Facts

- Node type is `Knooppunt.csv:KNP_TYP`.
- Connection type is `Verbinding.csv:VRB_TYP`.
- `Goot` is an open line and is represented by `VRB_TYP=OPL`.
- `Infiltratieriool` is represented by `VRB_TYP=ITR`.
- `Overstortleiding` is a closed gravity line and can be represented by `VRB_TYP=GSL`, but the distinction from an ordinary gravity line is lost in the current export.
- `DEB_TYP=LAT` means lateral discharge from another sewer system.
- `AFV_OPP` is a separate contributing-area value and is not itself the lateral discharge.
- HydX defines material codes but does not define Manning coefficients or Rana visualization values.

## Feedback Requirements

### 1. Trottoirkolk node visualization

A GWSW node with class URI ending in `Trottoirkolk` must be represented with Rana connection-node visualization `4`.

The current HydX CSV export does not contain this class. Do not infer it from identifier, geometry, name, or `KNP_TYP`. Implement the mapping only when a future input preserves the GWSW class information. Inputs without that information must retain current behavior.

Required tests:

- Preserved class `Trottoirkolk` maps to visualization `4`.
- Current input without a class field remains backward compatible.

### 2. Goot pipe visualization

An open HydX connection (`VRB_TYP=OPL`) must be represented with Rana pipe visualization `9` for a slot or trench drain.

Required behavior:

- Continue creating a pipe.
- Preserve open-profile validation.
- Set visualization to `9`.
- Continue assigning material and friction.

Required tests:

- `OPL` produces a pipe with visualization `9`.
- Existing open-profile validation remains active.

### 3. Infiltratieriool pipe visualization

An HydX connection with `VRB_TYP=ITR` must be represented with Rana pipe visualization `8` for an infiltration drain.

Required behavior:

- Continue creating a connected pipe.
- Set visualization to `8`.
- Preserve current profile and sewerage mappings.

Required tests:

- `ITR` produces a pipe with visualization `8`.

### 4. Kolkaansluitleiding handling

A GWSW `Kolkaansluitleiding` should be represented as a pipe with the Rana “other” visualization, meaning no special visualization. Poor or incomplete records may be excluded by existing validation behavior.

The current HydX ontology does not define a dedicated `VRB_TYP` for `Kolkaansluitleiding`. Do not guess its class from an unrelated HydX code. Implement this mapping only when the input preserves the GWSW class.

Required behavior:

- Valid class-preserved records become pipes.
- Visualization uses the Rana schema’s explicit “other” value.
- Missing endpoints, profiles, or levels retain current error logging and skip behavior.
- Import must not crash on incomplete data.

Required tests:

- A valid class-preserved `Kolkaansluitleiding` becomes an un-specialized pipe.
- An incomplete record follows existing validation behavior.

### 5. Overstortleiding pipe visualization

A GWSW `Overstortleiding` must be represented with Rana pipe visualization `4` for a spillway.

The current HydX export can reduce this class to `VRB_TYP=GSL`, which is also used for ordinary gravity pipes. Do not map every `GSL` to visualization `4`. Use visualization `4` only when the original class is preserved.

Required tests:

- A class-preserved `Overstortleiding` maps to visualization `4`.
- An ordinary `GSL` remains an ordinary pipe.

### 6. Lateral discharge records

The final three records in the supplied `Debiet.csv` are:

```text
knp30;LatDeb1;LAT;;;
lei12;LatDeb2;LAT;;;
knp31;;LAT;;12
```

The current importer treats all discharge records as impervious surfaces, so these lateral records are missing from the Rana schematisation.

Required behavior:

- Add a `laterals` collection to the internal Rana representation.
- Branch on `DebietType`.
- Every resolvable `LAT` record becomes a Rana `Lateral1D` object.
- Non-`LAT` records retain the current impervious-surface behavior.
- Resolve a lateral identifier against connection nodes first, then connections according to the agreed Rana endpoint convention.
- Log and skip unresolved identifiers without aborting the import.
- Do not fabricate a time series when the HydX record has none.
- Preserve `AFV_OPP` when it represents a lateral contributing area.
- Export laterals after connection nodes exist.
- Include lateral counts in export results.

The known erroneous connection from the GWSW server is not to receive a hard-coded exception. Only records present in the HydX input should be processed; missing or invalid references follow existing validation behavior.

The current fixture contains a `LAT` discharge for `lei4`, but no matching `lei4` connection is imported. It is logged and skipped rather than handled with a production-specific exception. The installed Rana `Lateral1D` schema has no contributing-area column, so `AFV_OPP` is retained during HydX parsing but is not persisted for 1D laterals.

Required tests:

- All three `LAT` fixture records become Rana `Lateral1D` objects; only genuinely unresolved references may be skipped with an explicit tested error.
- Non-lateral discharge behavior is unchanged.
- Unresolved lateral identifiers are logged and skipped.

Open implementation detail: verify how a static `LAT` record without a time series is represented in the Rana model and how a connection identifier resolves to a lateral node.

### 7. Material-based Manning friction

Every exported pipe must receive a friction type and friction value.

The target Rana GeoPackage is authoritative and must be read on every run. Values must not be taken solely from hard-coded defaults.

Required behavior:

- Read the target `material` table before assigning friction.
- Resolve HydX profile material (`PRO_MAT`) to the target Rana material.
- Use `material.friction_type` for the pipe friction type.
- Use `material.friction_coefficient` for the pipe friction value.
- Write the resolved values to `pipe.friction_type` and `pipe.friction_value`.
- Use explicit built-in material defaults only when the target material is absent or has no usable friction configuration.
- Log each fallback material and pipe code.
- Preserve the existing material ID mapping.

The target material configuration should be loaded after the output database is available. Prefer a small change that assigns friction immediately before constructing `Pipe` objects, or pass the loaded configuration into conversion explicitly. Avoid opening a production database more than necessary.

Required tests:

- A customized target material value overrides the built-in default.
- A configured material sets both friction type and value.
- An unknown or unconfigured material uses the documented fallback and logs it.
- No production GeoPackage is required; use the existing temporary `ThreediDatabase` fixture and insert a minimal sanitized material table.

### 8. Import provenance tags

Add a provenance tag to objects created by this importer. This is a Rana-specific provenance marker, not a replacement for GWSW semantic class information.

Required behavior:

- Apply one stable importer tag, such as `gwsw-hydx-import`.
- Apply it to connection nodes, pipes, pumps, weirs, orifices, outlets, surfaces, dry-weather flows, and laterals.
- Use the Rana schema’s supported tag representation.

Required tests:

- Each exported object type receives the importer tag.
- Existing tags are not unintentionally overwritten if the schema supports multiple tags.

### 9. Production data protection

Do not commit `Margraten.gpkg`, the other real GeoPackages, or any extracted production data.

Use:

- synthetic HydX objects for visualization mappings,
- the existing CSV fixtures for lateral regression tests,
- temporary databases from `hydxlib/tests/conftest.py` for material and exporter tests.

## Implementation Order

1. Add target-material friction lookup and regression tests.
2. Add `OPL` and `ITR` visualization mappings and regression tests.
3. Add `LAT` lateral conversion and exporter support.
4. Add provenance tags.
5. Add preserved-GWSW-class support and mappings for `Trottoirkolk`, `Kolkaansluitleiding`, and `Overstortleiding` when the input field is confirmed.
6. Update architecture, conventions, and glossary documentation with the settled implementation decisions.

## Explicit Non-Goals

- Do not infer lost GWSW classes from identifiers, geometry, names, or ordinary HydX codes.
- Do not map all `GSL` connections to spillway visualization.
- Do not hard-code production-specific connection exceptions.
- Do not check in `Margraten.gpkg` or any other production schematisation.
- Do not treat HydX material codes as authoritative Manning values when the target Rana material table provides a configured value.

#!/usr/bin/env python3
"""
Step 9.3: lock exact H0/H1/H2 runtime options.

The output is a canonical JSON options artifact plus a top-level SHA256 file.
Per-regime option hashes are embedded so submission/retrieval/manuscript records
can point to the exact options used.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from common import (
    default_runtime_options,
    get_runtime_options_hashes,
    load_paths,
    load_scope,
    parser_with_project,
    resolve_project_path,
    sha256_obj,
    utc_now,
    validate_runtime_options_structure,
    write_safe_json,
    write_text,
)


def main() -> int:
    parser = parser_with_project("Step 9.3 lock exact H0/H1/H2 runtime options.")
    parser.add_argument("--template", default=None, help="Optional runtime options template JSON. Default: package config/runtime_options_template.json.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))

    if args.template:
        from common import read_json
        runtime_options: Dict[str, Any] = read_json(Path(args.template))
    else:
        runtime_options = default_runtime_options()

    runtime_options["created_utc"] = utc_now()
    runtime_options["operator_identifier"] = args.operator
    runtime_options["selected_backend"] = scope["selected_backend"]
    runtime_options["pair_count_expected"] = scope["pair_count_expected"]
    runtime_options["circuit_count_expected"] = scope["circuit_count_expected"]
    runtime_options["rma_excluded"] = True
    runtime_options["wave2_excluded"] = True

    failure_reasons = validate_runtime_options_structure(runtime_options, scope)
    hashes = get_runtime_options_hashes(runtime_options)
    runtime_options.update(hashes)
    runtime_options["options_explicit_and_hashed"] = not failure_reasons
    runtime_options["failure_reasons"] = failure_reasons
    runtime_options["token_value_absent_from_artifact"] = True

    out_path = resolve_project_path(project_root, paths["outputs"]["runtime_options"])
    write_safe_json(out_path, runtime_options)

    sha_path = resolve_project_path(project_root, paths["outputs"]["runtime_options_sha256"])
    write_text(sha_path, hashes["runtime_options_all_sha256"] + "\n")

    print(f"[step9.3] options_explicit_and_hashed={not failure_reasons} -> {out_path}")
    print(f"[step9.3] sha256={hashes['runtime_options_all_sha256']} -> {sha_path}")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

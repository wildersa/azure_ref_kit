#!/usr/bin/env python3
import os
import yaml
import sys
import argparse
from typing import List, Dict, Any

def log_error(message: str):
    print(f"ERROR: {message}", file=sys.stderr)

def log_info(message: str):
    print(f"INFO: {message}")

def validate_solution(solution_path: str) -> bool:
    valid = True
    solution_yaml_path = os.path.join(solution_path, "solution.yaml")
    readme_path = os.path.join(solution_path, "README.md")

    if not os.path.exists(solution_yaml_path):
        log_error(f"Missing solution.yaml in {solution_path}")
        valid = False

    if not os.path.exists(readme_path):
        log_error(f"Missing README.md in {solution_path}")
        valid = False

    if not valid:
        return False

    try:
        with open(solution_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        log_error(f"Failed to parse solution.yaml in {solution_path}: {e}")
        return False

    status = config.get("status")
    # For now, allow 'active' and 'stable' as they are used in the repo, but log a warning if we want to transition.
    # The contract says scaffold, partial, executable.
    allowed_statuses = ["scaffold", "partial", "executable", "active", "stable"]
    if status not in allowed_statuses:
        log_error(f"Invalid status '{status}' in {solution_yaml_path}. Must be one of {allowed_statuses}.")
        valid = False

    # Check building blocks
    building_blocks = config.get("building_blocks", [])
    for block in building_blocks:
        if isinstance(block, str):
            # Support simple string path for backward compatibility or simple cases
            block_path = block
        elif isinstance(block, dict):
            block_path = block.get("path")
            if not block_path:
                log_error(f"Building block missing 'path' in {solution_yaml_path}")
                valid = False
                continue
        else:
            log_error(f"Invalid building block format in {solution_yaml_path}")
            valid = False
            continue

        if not os.path.exists(block_path):
            log_error(f"Declared building block path does not exist: {block_path} (referenced in {solution_yaml_path})")
            valid = False

    # Status-based requirements
    if status in ["partial", "executable"]:
        runtime_map_path = os.path.join(solution_path, "runtime-map.md")
        if not os.path.exists(runtime_map_path):
            log_error(f"Missing runtime-map.md in {solution_path} (required for status '{status}')")
            valid = False

    # Check package-map.yaml whenever it is present
    package_map_path = os.path.join(solution_path, "deploy", "package-map.yaml")
    if os.path.exists(package_map_path):
        try:
            with open(package_map_path, 'r') as f:
                pkg_config = yaml.safe_load(f)

            if not pkg_config or not isinstance(pkg_config, dict) or "artifacts" not in pkg_config:
                log_error(f"Malformed deploy/package-map.yaml in {solution_path}: Missing 'artifacts' root.")
                valid = False
            else:
                artifacts = pkg_config.get("artifacts", [])
                for art in artifacts:
                    sources = art.get("sources", [])
                    for src in sources:
                        if not os.path.exists(src):
                            log_error(f"Source path in package-map.yaml does not exist: {src} (referenced in {package_map_path})")
                            valid = False
        except Exception as e:
            log_error(f"Failed to parse deploy/package-map.yaml in {solution_path}: {e}")
            valid = False
    elif status == "executable":
        log_error(f"Missing deploy/package-map.yaml in {solution_path} (required for status 'executable')")
        valid = False

    if status == "executable":
        infra_path = os.path.join(solution_path, "infra", "terraform")
        if not os.path.exists(infra_path):
            log_error(f"Missing infra/terraform/ in {solution_path} (required for status 'executable')")
            valid = False

        tests_path = os.path.join(solution_path, "tests")
        if not os.path.exists(tests_path):
            log_error(f"Missing tests/ in {solution_path} (required for status 'executable')")
            valid = False

    return valid

def main():
    parser = argparse.ArgumentParser(description="Validate solution composition contract.")
    parser.add_argument("--path", type=str, help="Path to a specific solution directory.")
    parser.add_argument("--all", action="store_true", help="Validate all solutions in the solutions/ directory.")

    args = parser.parse_args()

    if not args.path and not args.all:
        parser.print_help()
        sys.exit(1)

    success = True
    if args.all:
        solutions_dir = "solutions"
        if not os.path.exists(solutions_dir):
            log_error(f"Directory {solutions_dir} not found.")
            sys.exit(1)

        for item in os.listdir(solutions_dir):
            item_path = os.path.join(solutions_dir, item)
            if os.path.isdir(item_path):
                log_info(f"Validating solution: {item_path}")
                if not validate_solution(item_path):
                    success = False
    elif args.path:
        log_info(f"Validating solution: {args.path}")
        if not validate_solution(args.path):
            success = False

    if not success:
        log_error("Validation failed.")
        sys.exit(1)

    log_info("Validation successful.")

if __name__ == "__main__":
    main()

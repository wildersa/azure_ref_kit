import os
import pytest
import yaml
import shutil
from scripts.check_solution_composition import validate_solution

@pytest.fixture
def temp_solution(tmp_path):
    def _create_solution(name, status, building_blocks=None, files=None):
        sol_dir = tmp_path / name
        sol_dir.mkdir()

        config = {
            "name": name,
            "status": status,
            "building_blocks": building_blocks or []
        }

        with open(sol_dir / "solution.yaml", "w") as f:
            yaml.dump(config, f)

        if files:
            for file_path in files:
                full_path = sol_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                if file_path.endswith(".yaml"):
                    with open(full_path, "w") as f:
                        yaml.dump({"artifacts": []}, f)
                else:
                    full_path.touch()

        return str(sol_dir)
    return _create_solution

def test_validate_scaffold_minimal(temp_solution):
    path = temp_solution("scaffold-sol", "scaffold")
    assert validate_solution(path) is True

def test_validate_scaffold_missing_yaml(tmp_path):
    sol_dir = tmp_path / "missing-yaml"
    sol_dir.mkdir()
    assert validate_solution(str(sol_dir)) is False

def test_validate_partial_missing_runtime_map(temp_solution):
    path = temp_solution("partial-sol", "partial")
    # partial requires runtime-map.md
    assert validate_solution(path) is False

def test_validate_partial_with_runtime_map(temp_solution):
    path = temp_solution("partial-sol", "partial", files=["runtime-map.md"])
    assert validate_solution(path) is True

def test_validate_executable_requirements(temp_solution):
    path = temp_solution("exec-sol", "executable", files=["runtime-map.md"])
    # executable requires deploy/package-map.yaml, infra/terraform, tests/
    assert validate_solution(path) is False

def test_validate_executable_full(temp_solution):
    path = temp_solution("exec-sol", "executable", files=[
        "runtime-map.md",
        "deploy/package-map.yaml",
        "infra/terraform/main.tf",
        "tests/test_sol.py"
    ])
    assert validate_solution(path) is True

def test_validate_building_block_path_exists(temp_solution, tmp_path):
    bb_path = tmp_path / "building-blocks/test-bb"
    bb_path.mkdir(parents=True)

    path = temp_solution("bb-sol", "scaffold", building_blocks=[{"path": str(bb_path)}])
    assert validate_solution(path) is True

def test_validate_building_block_path_missing(temp_solution):
    path = temp_solution("bb-sol", "scaffold", building_blocks=[{"path": "non-existent-bb"}])
    assert validate_solution(path) is False

def test_validate_package_map_sources(temp_solution, tmp_path):
    src_path = tmp_path / "src/my-source"
    src_path.mkdir(parents=True)

    sol_dir = tmp_path / "pkg-sol"
    sol_dir.mkdir()

    config = {
        "name": "pkg-sol",
        "status": "executable",
        "building_blocks": []
    }
    with open(sol_dir / "solution.yaml", "w") as f:
        yaml.dump(config, f)

    pkg_config = {
        "artifacts": [
            {
                "name": "app",
                "type": "azure_function",
                "sources": [str(src_path)]
            }
        ]
    }
    pkg_dir = sol_dir / "deploy"
    pkg_dir.mkdir()
    with open(pkg_dir / "package-map.yaml", "w") as f:
        yaml.dump(pkg_config, f)

    # Still need other executable files
    (sol_dir / "runtime-map.md").touch()
    (sol_dir / "infra/terraform").mkdir(parents=True)
    (sol_dir / "tests").mkdir()

    assert validate_solution(str(sol_dir)) is True

def test_validate_package_map_source_missing(temp_solution, tmp_path):
    sol_dir = tmp_path / "pkg-sol"
    sol_dir.mkdir()

    config = {
        "name": "pkg-sol",
        "status": "executable",
        "building_blocks": []
    }
    with open(sol_dir / "solution.yaml", "w") as f:
        yaml.dump(config, f)

    pkg_config = {
        "artifacts": [
            {
                "name": "app",
                "type": "azure_function",
                "sources": ["missing-source"]
            }
        ]
    }
    pkg_dir = sol_dir / "deploy"
    pkg_dir.mkdir()
    with open(pkg_dir / "package-map.yaml", "w") as f:
        yaml.dump(pkg_config, f)

    (sol_dir / "runtime-map.md").touch()
    (sol_dir / "infra/terraform").mkdir(parents=True)
    (sol_dir / "tests").mkdir()

    assert validate_solution(str(sol_dir)) is False

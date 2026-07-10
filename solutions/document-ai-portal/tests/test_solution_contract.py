import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def test_solution_yaml_paths_exist():
    """Validate that every path referenced in solution.yaml exists."""
    yaml_path = REPO_ROOT / "solutions" / "document-ai-portal" / "solution.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    # Check building_blocks
    for block in config.get("building_blocks", []):
        if isinstance(block, str):
            bb_path = block
        else:
            bb_path = block.get("path")

        full_path = REPO_ROOT / bb_path
        assert full_path.exists(), f"Building block path does not exist: {bb_path}"

    # Check contracts
    for contract_path in config.get("contracts", []):
        full_path = REPO_ROOT / contract_path
        assert full_path.exists(), f"Contract path does not exist: {contract_path}"

    # Check entrypoints
    for entry_name, entry_data in config.get("entrypoints", {}).items():
        target_path = entry_data.get("target")
        if target_path:
            full_path = REPO_ROOT / target_path
            assert full_path.exists(), (
                f"Entrypoint '{entry_name}' target path does not exist: {target_path}"
            )


def test_readme_content():
    """Validate that README.md contains required sections and diagrams."""
    readme_path = REPO_ROOT / "solutions" / "document-ai-portal" / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    # Check for Mermaid diagram
    assert "```mermaid" in content, "README.md missing Mermaid diagram"

    # Check for customer-safe status boundary reference
    assert "building-blocks/security/customer-safe-status-boundary/" in content, (
        "README.md missing reference to customer-safe-status-boundary building block"
    )

    # Check for required boundary language
    assert "## Customer-Safe Status & Artifact Boundary" in content, (
        "README.md missing 'Customer-Safe Status & Artifact Boundary' header"
    )
    assert "### Allowed Customer-Facing Data" in content, (
        "README.md missing 'Allowed Customer-Facing Data' section"
    )
    assert "### Forbidden Data (Internal-Only)" in content, (
        "README.md missing 'Forbidden Data (Internal-Only)' section"
    )

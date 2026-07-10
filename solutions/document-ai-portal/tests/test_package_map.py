import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent

def test_package_map_sources_exist():
    """Validate that all source paths in package-map.yaml exist."""
    pkg_map_path = REPO_ROOT / "solutions" / "document-ai-portal" / "deploy" / "package-map.yaml"

    assert pkg_map_path.exists(), "package-map.yaml does not exist"

    with open(pkg_map_path, "r") as f:
        config = yaml.safe_load(f)

    assert "artifacts" in config, "package-map.yaml missing 'artifacts' root"

    for artifact in config["artifacts"]:
        assert "sources" in artifact, f"Artifact '{artifact.get('name')}' missing 'sources'"
        for source_path in artifact["sources"]:
            full_path = REPO_ROOT / source_path
            assert full_path.exists(), f"Source path does not exist: {source_path}"

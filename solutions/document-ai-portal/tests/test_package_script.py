import os
import subprocess
import json
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SOLUTION_ROOT = REPO_ROOT / "solutions" / "document-ai-portal"
PACKAGE_SH = SOLUTION_ROOT / "deploy" / "package.sh"
DIST_DIR = SOLUTION_ROOT / "dist"

def test_package_script_execution():
    """Verify that package.sh runs successfully and produces expected output."""

    # Ensure we start clean
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    # Run the script
    result = subprocess.run(["bash", str(PACKAGE_SH)], capture_output=True, text=True, cwd=str(SOLUTION_ROOT))

    assert result.returncode == 0, f"package.sh failed with error: {result.stderr}"
    assert "Packaging process finished successfully." in result.stdout

    # Verify dist directory exists
    assert DIST_DIR.exists(), "dist directory was not created"

    # Verify global manifest
    global_manifest_path = DIST_DIR / "package-manifest.json"
    assert global_manifest_path.exists(), "package-manifest.json was not created"

    with open(global_manifest_path, "r") as f:
        manifest = json.load(f)
        assert manifest["solution"] == "document-ai-portal"
        assert len(manifest["artifacts"]) > 0

    # Verify specific artifacts
    expected_artifacts = ["pipeline_function_app", "api_function_app", "portal"]
    for art_name in expected_artifacts:
        art_dir = DIST_DIR / art_name
        assert art_dir.exists(), f"Artifact directory {art_name} was not created"

        art_manifest_path = art_dir / "artifact-manifest.json"
        assert art_manifest_path.exists(), f"Artifact manifest for {art_name} was not created"

        with open(art_manifest_path, "r") as f:
            art_manifest = json.load(f)
            assert art_manifest["name"] == art_name

            # Verify that sources are staged in subdirectories
            for source_rel_path in art_manifest["sources"]:
                source_name = Path(source_rel_path).name
                assert (art_dir / source_name).exists(), f"Source subdirectory {source_name} was not created in {art_name}"
                assert (art_dir / source_name).is_dir(), f"Source {source_name} should be a directory in {art_name}"

    # Verify specific content from one of the artifacts
    # pipeline_function_app should have blob-trigger-start-pipeline/function_app.py
    assert (DIST_DIR / "pipeline_function_app" / "blob-trigger-start-pipeline" / "function_app.py").exists()
    assert (DIST_DIR / "pipeline_function_app" / "durable-basic-pipeline" / "function_app.py").exists()

import os
import subprocess
import json
from pathlib import Path
import shutil
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SOLUTION_ROOT = REPO_ROOT / "solutions" / "document-ai-portal"
DEPLOY_SH = SOLUTION_ROOT / "deploy" / "deploy.sh"
DIST_DIR = SOLUTION_ROOT / "dist"

@pytest.fixture
def clean_dist():
    """Ensure dist directory is clean before and after tests."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    yield
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

def test_deploy_fails_if_no_dist(clean_dist):
    """Verify that deploy.sh fails if the dist directory does not exist."""
    result = subprocess.run(["bash", str(DEPLOY_SH)], capture_output=True, text=True, cwd=str(SOLUTION_ROOT))
    assert result.returncode != 0
    assert "ERROR: package-manifest.json not found" in result.stderr or "run the package step first" in result.stderr.lower() or "run the package step first" in result.stdout.lower()

def test_deploy_fails_if_manifest_missing(clean_dist):
    """Verify that deploy.sh fails if dist exists but manifest is missing."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["bash", str(DEPLOY_SH)], capture_output=True, text=True, cwd=str(SOLUTION_ROOT))
    assert result.returncode != 0
    assert "package-manifest.json not found" in result.stderr.lower() or "run the package step first" in result.stderr.lower() or "run the package step first" in result.stdout.lower()

def test_deploy_fails_if_artifact_missing(clean_dist):
    """Verify that deploy.sh fails if an artifact folder is missing."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "solution": "document-ai-portal",
        "artifacts": [
            {"name": "missing_artifact", "type": "azure_function", "sources": [], "path": "dist/missing_artifact"}
        ]
    }
    with open(DIST_DIR / "package-manifest.json", "w") as f:
        json.dump(manifest, f)

    result = subprocess.run(["bash", str(DEPLOY_SH)], capture_output=True, text=True, cwd=str(SOLUTION_ROOT))
    assert result.returncode != 0
    assert "missing_artifact" in result.stderr or "missing_artifact" in result.stdout

def test_deploy_preflight_success_with_artifacts(clean_dist):
    """Verify that deploy.sh passes preflight if all artifacts are present."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = [
        {"name": "pipeline_function_app", "type": "azure_function", "sources": [], "path": "dist/pipeline_function_app"},
        {"name": "api_function_app", "type": "azure_function", "sources": [], "path": "dist/api_function_app"},
        {"name": "portal", "type": "static_web_app", "sources": [], "path": "dist/portal"}
    ]

    for art in artifacts:
        art_path = DIST_DIR / art["name"]
        art_path.mkdir(parents=True, exist_ok=True)
        with open(art_path / "artifact-manifest.json", "w") as f:
            json.dump(art, f)

        if art["type"] == "azure_function":
            (DIST_DIR / f"{art['name']}.zip").touch()

    manifest = {
        "solution": "document-ai-portal",
        "artifacts": artifacts
    }
    with open(DIST_DIR / "package-manifest.json", "w") as f:
        json.dump(manifest, f)

    result = subprocess.run(["bash", str(DEPLOY_SH)], capture_output=True, text=True, cwd=str(SOLUTION_ROOT))

    # Preflight should succeed (return 0)
    assert result.returncode == 0
    assert "Preflight successful" in result.stdout or "Validation successful" in result.stdout
    assert "Next Steps" in result.stdout

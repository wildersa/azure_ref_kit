import yaml
import os
import shutil
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SOLUTION_ROOT = Path(__file__).parent.parent.resolve()
DIST_DIR = SOLUTION_ROOT / "dist"
PACKAGE_MAP_PATH = SOLUTION_ROOT / "deploy" / "package-map.yaml"

def clean_dist():
    if DIST_DIR.exists():
        logger.info(f"Cleaning existing dist directory: {DIST_DIR}")
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

def load_package_map():
    if not PACKAGE_MAP_PATH.exists():
        raise FileNotFoundError(f"package-map.yaml not found at {PACKAGE_MAP_PATH}")

    with open(PACKAGE_MAP_PATH, "r") as f:
        return yaml.safe_load(f)

def copy_source(source_rel_path, artifact_dir):
    source_full_path = (REPO_ROOT / source_rel_path).resolve()
    if not source_full_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_full_path}")

    # Use the building block directory name as a subdirectory to avoid collisions
    # This ensures that files like function_app.py from different BBs don't overwrite each other.
    source_name = source_full_path.name
    target_dir = artifact_dir / source_name

    logger.info(f"  Assembling {source_rel_path} into {target_dir.relative_to(SOLUTION_ROOT)}")

    if source_full_path.is_dir():
        # Exclude common non-runtime files
        exclude_patterns = shutil.ignore_patterns(
            "tests", "infra", "module.yaml", "*.pyc", "__pycache__", ".pytest_cache", ".venv", "venv"
        )
        shutil.copytree(source_full_path, target_dir, dirs_exist_ok=True, ignore=exclude_patterns)
    else:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_full_path, target_dir)

def package_solution():
    try:
        clean_dist()
        config = load_package_map()

        artifacts_manifest = []

        for artifact in config.get("artifacts", []):
            name = artifact.get("name")
            art_type = artifact.get("type")
            sources = artifact.get("sources", [])

            logger.info(f"Packaging artifact: {name} ({art_type})")
            artifact_dir = DIST_DIR / name
            artifact_dir.mkdir(parents=True, exist_ok=True)

            for source in sources:
                copy_source(source, artifact_dir)

            # Create artifact manifest
            manifest = {
                "name": name,
                "type": art_type,
                "sources": sources,
                "path": str(artifact_dir.relative_to(SOLUTION_ROOT))
            }

            with open(artifact_dir / "artifact-manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)

            artifacts_manifest.append(manifest)

        # Create global manifest
        global_manifest = {
            "solution": "document-ai-portal",
            "artifacts": artifacts_manifest
        }
        with open(DIST_DIR / "package-manifest.json", "w") as f:
            json.dump(global_manifest, f, indent=2)

        logger.info(f"Packaging complete. Artifacts located in {DIST_DIR}")

    except Exception as e:
        logger.error(f"Packaging failed: {e}")
        exit(1)

if __name__ == "__main__":
    package_solution()

import argparse
import json
import logging
import sys
from .config import Settings
from .client import DevOpsClient
from .tool import get_build_status


def main():
    """Minimal CLI for local testing of the DevOps status tool."""
    parser = argparse.ArgumentParser(
        description="Fetch Azure DevOps build status (safe tool)."
    )
    parser.add_argument(
        "--org-url", required=True, help="Azure DevOps organization URL."
    )
    parser.add_argument("--project", required=True, help="Project name or ID.")
    parser.add_argument("--build-id", required=True, type=int, help="Build ID.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    try:
        # Load settings (PAT) from environment
        settings = Settings.from_env()
        client = DevOpsClient(pat=settings.devops_pat)

        request_params = {
            "organization_url": args.org_url,
            "project": args.project,
            "build_id": args.build_id,
        }

        # Execute tool
        response = get_build_status(request_params, client)

        # Output safe JSON response
        print(json.dumps(response.model_dump(mode="json"), indent=2))

    except Exception as e:
        # User-friendly error for CLI
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

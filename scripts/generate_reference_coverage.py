#!/usr/bin/env python3
"""Generate the human-readable Azure AI reference coverage dashboard."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = REPO_ROOT / "docs" / "reference-coverage.yaml"
OUTPUT_PATH = REPO_ROOT / "docs" / "reference-coverage.md"

DOMAIN_COVERAGE_STATUSES = {"none", "partial", "covered"}
CANDIDATE_STATUSES = {
    "candidate",
    "researched",
    "issue-open",
    "implementing",
    "covered",
    "rejected",
    "revisit",
}
CANDIDATE_PRIORITIES = {"low", "medium", "high"}
CANDIDATE_KINDS = {"building-block", "solution", "pattern", "research"}


class CoverageValidationError(ValueError):
    """Raised when reference coverage metadata violates its contract."""


def load_coverage(path: Path = SOURCE_PATH) -> dict[str, Any]:
    """Load and validate the coverage source file."""
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CoverageValidationError(f"Coverage source does not exist: {path}") from exc
    except yaml.YAMLError as exc:
        raise CoverageValidationError(f"Invalid YAML in {path}: {exc}") from exc

    errors = validate_coverage(payload)
    if errors:
        joined = "\n- ".join(errors)
        raise CoverageValidationError(f"Coverage validation failed:\n- {joined}")
    return payload


def validate_coverage(payload: Any) -> list[str]:
    """Return all contract violations found in a coverage payload."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be a mapping"]

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    _validate_date(payload.get("last_reviewed"), "last_reviewed", errors)

    discovery = payload.get("continuous_discovery")
    if not isinstance(discovery, dict):
        errors.append("continuous_discovery must be a mapping")
    else:
        for field in ("source_priority", "when_queue_empty", "selection_rules"):
            value = discovery.get(field)
            if not _is_non_empty_string_list(value):
                errors.append(f"continuous_discovery.{field} must be a non-empty string list")

    domains = payload.get("domains")
    if not isinstance(domains, list) or not domains:
        errors.append("domains must be a non-empty list")
        return errors

    domain_ids: set[str] = set()
    candidate_ids: set[str] = set()

    for index, domain in enumerate(domains):
        prefix = f"domains[{index}]"
        if not isinstance(domain, dict):
            errors.append(f"{prefix} must be a mapping")
            continue

        domain_id = domain.get("id")
        if not _is_non_empty_string(domain_id):
            errors.append(f"{prefix}.id must be a non-empty string")
        elif domain_id in domain_ids:
            errors.append(f"duplicate domain id: {domain_id}")
        else:
            domain_ids.add(domain_id)

        if not _is_non_empty_string(domain.get("name")):
            errors.append(f"{prefix}.name must be a non-empty string")

        coverage = domain.get("coverage")
        if coverage not in DOMAIN_COVERAGE_STATUSES:
            errors.append(
                f"{prefix}.coverage must be one of {sorted(DOMAIN_COVERAGE_STATUSES)}"
            )

        _validate_date(domain.get("last_reviewed"), f"{prefix}.last_reviewed", errors)

        for field in ("implemented", "gaps"):
            value = domain.get(field)
            if not isinstance(value, list) or not all(
                _is_non_empty_string(item) for item in value
            ):
                errors.append(f"{prefix}.{field} must be a string list")

        candidates = domain.get("candidates")
        if not isinstance(candidates, list):
            errors.append(f"{prefix}.candidates must be a list")
            continue

        for candidate_index, candidate in enumerate(candidates):
            candidate_prefix = f"{prefix}.candidates[{candidate_index}]"
            _validate_candidate(candidate, candidate_prefix, candidate_ids, errors)

    return errors


def _validate_candidate(
    candidate: Any,
    prefix: str,
    candidate_ids: set[str],
    errors: list[str],
) -> None:
    if not isinstance(candidate, dict):
        errors.append(f"{prefix} must be a mapping")
        return

    candidate_id = candidate.get("id")
    if not _is_non_empty_string(candidate_id):
        errors.append(f"{prefix}.id must be a non-empty string")
    elif candidate_id in candidate_ids:
        errors.append(f"duplicate candidate id: {candidate_id}")
    else:
        candidate_ids.add(candidate_id)

    if not _is_non_empty_string(candidate.get("title")):
        errors.append(f"{prefix}.title must be a non-empty string")
    if candidate.get("kind") not in CANDIDATE_KINDS:
        errors.append(f"{prefix}.kind must be one of {sorted(CANDIDATE_KINDS)}")
    if candidate.get("status") not in CANDIDATE_STATUSES:
        errors.append(
            f"{prefix}.status must be one of {sorted(CANDIDATE_STATUSES)}"
        )
    if candidate.get("priority") not in CANDIDATE_PRIORITIES:
        errors.append(
            f"{prefix}.priority must be one of {sorted(CANDIDATE_PRIORITIES)}"
        )
    if not _is_non_empty_string(candidate.get("reason")):
        errors.append(f"{prefix}.reason must be a non-empty string")

    sources = candidate.get("sources")
    if not isinstance(sources, dict):
        errors.append(f"{prefix}.sources must be a mapping")
    else:
        for source_type in ("official", "external"):
            source_values = sources.get(source_type)
            if not isinstance(source_values, list) or not all(
                _is_non_empty_string(item) for item in source_values
            ):
                errors.append(f"{prefix}.sources.{source_type} must be a string list")

    issue = candidate.get("issue")
    if issue is not None and (
        not isinstance(issue, int) or isinstance(issue, bool) or issue <= 0
    ):
        errors.append(f"{prefix}.issue must be null or a positive integer")
    if candidate.get("status") in {"issue-open", "implementing"} and issue is None:
        errors.append(
            f"{prefix}.issue is required when status is {candidate.get('status')}"
        )


def _validate_date(value: Any, field: str, errors: list[str]) -> None:
    if not _is_non_empty_string(value):
        errors.append(f"{field} must be an ISO date string")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field} must use YYYY-MM-DD")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        _is_non_empty_string(item) for item in value
    )


def generate_markdown(payload: dict[str, Any]) -> str:
    """Render deterministic Markdown from validated coverage metadata."""
    domains = payload["domains"]
    discovery = payload["continuous_discovery"]
    counts = {
        status: sum(domain["coverage"] == status for domain in domains)
        for status in sorted(DOMAIN_COVERAGE_STATUSES)
    }

    lines = [
        "# Azure AI Reference Coverage",
        "",
        "This dashboard is generated from `docs/reference-coverage.yaml`. Edit the YAML source, then regenerate this file.",
        "",
        f"**Last reviewed:** {payload['last_reviewed']}",
        "",
        "## Coverage summary",
        "",
        "| Covered | Partial | None | Total domains |",
        "| ---: | ---: | ---: | ---: |",
        f"| {counts['covered']} | {counts['partial']} | {counts['none']} | {len(domains)} |",
        "",
        "## Continuous discovery workflow",
        "",
    ]

    for index, step in enumerate(discovery["when_queue_empty"], start=1):
        lines.append(f"{index}. {step}")

    lines.extend(["", "### Source priority", ""])
    for source in discovery["source_priority"]:
        lines.append(f"- {source}")

    lines.extend(["", "### Selection rules", ""])
    for rule in discovery["selection_rules"]:
        lines.append(f"- {rule}")

    lines.extend(
        [
            "",
            "## Domain overview",
            "",
            "| Domain | Coverage | Implemented references | Open gaps | Candidates | Last reviewed |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for domain in domains:
        lines.append(
            "| {name} | `{coverage}` | {implemented} | {gaps} | {candidates} | {reviewed} |".format(
                name=domain["name"],
                coverage=domain["coverage"],
                implemented=len(domain["implemented"]),
                gaps=len(domain["gaps"]),
                candidates=len(domain["candidates"]),
                reviewed=domain["last_reviewed"],
            )
        )

    lines.extend(["", "## Domain details", ""])
    for domain in domains:
        lines.extend(
            [
                f"### {domain['name']}",
                "",
                f"Coverage: `{domain['coverage']}`  ",
                f"Last reviewed: `{domain['last_reviewed']}`",
                "",
                "**Implemented references**",
                "",
            ]
        )
        lines.extend(
            _markdown_items(
                domain["implemented"], "No implemented reference recorded."
            )
        )
        lines.extend(["", "**Known gaps**", ""])
        lines.extend(_markdown_items(domain["gaps"], "No gap recorded."))
        lines.extend(["", "**Candidates**", ""])

        if domain["candidates"]:
            lines.extend(
                [
                    "| ID | Title | Kind | Status | Priority | Issue |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for candidate in domain["candidates"]:
                issue = f"#{candidate['issue']}" if candidate["issue"] else "-"
                lines.append(
                    f"| `{candidate['id']}` | {candidate['title']} | `{candidate['kind']}` | "
                    f"`{candidate['status']}` | `{candidate['priority']}` | {issue} |"
                )
                lines.append("")
                lines.append(f"Reason: {candidate['reason']}")
                lines.append("")
                lines.append("Sources:")
                for source in candidate["sources"]["official"]:
                    lines.append(f"- Official: {source}")
                for source in candidate["sources"]["external"]:
                    lines.append(f"- External: {source}")
        else:
            lines.append("- No candidate recorded.")
        lines.append("")

    lines.extend(
        [
            "## Commands",
            "",
            "```bash",
            "python scripts/generate_reference_coverage.py",
            "python scripts/generate_reference_coverage.py --check",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _markdown_items(items: list[str], empty_message: str) -> list[str]:
    if not items:
        return [f"- {empty_message}"]
    return [f"- `{item}`" for item in items]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or validate the Azure AI reference coverage dashboard."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the generated Markdown differs from the committed file.",
    )
    args = parser.parse_args()

    try:
        payload = load_coverage()
        generated = generate_markdown(payload)
    except CoverageValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"Coverage dashboard does not exist: {OUTPUT_PATH}", file=sys.stderr)
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != generated:
            print(
                "Reference coverage dashboard is out of sync. Run "
                "'python scripts/generate_reference_coverage.py'.",
                file=sys.stderr,
            )
            return 1
        print("Reference coverage validation successful.")
        return 0

    OUTPUT_PATH.write_text(generated, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

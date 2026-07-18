from pathlib import Path

import pytest
import yaml

from scripts.generate_reference_coverage import (
    CoverageValidationError,
    generate_markdown,
    load_coverage,
    validate_coverage,
)


def valid_payload() -> dict:
    return {
        "schema_version": 1,
        "last_reviewed": "2026-07-18",
        "continuous_discovery": {
            "source_priority": ["Microsoft Learn"],
            "when_queue_empty": ["Read the catalog."],
            "selection_rules": ["Prefer missing capabilities."],
        },
        "domains": [
            {
                "id": "search-rag",
                "name": "Azure AI Search and RAG",
                "coverage": "partial",
                "last_reviewed": "2026-07-18",
                "implemented": ["building-blocks/search/basic"],
                "gaps": ["Evaluation"],
                "candidates": [
                    {
                        "id": "SEARCH-001",
                        "title": "Hybrid search reference",
                        "kind": "building-block",
                        "status": "candidate",
                        "priority": "high",
                        "reason": "No hybrid search reference exists.",
                        "sources": {
                            "official": ["https://learn.microsoft.com/example"],
                            "external": [],
                        },
                        "issue": None,
                    }
                ],
            }
        ],
    }


def test_validate_coverage_accepts_valid_payload() -> None:
    assert validate_coverage(valid_payload()) == []


def test_validate_coverage_rejects_duplicate_candidate_ids() -> None:
    payload = valid_payload()
    duplicate = dict(payload["domains"][0]["candidates"][0])
    payload["domains"][0]["candidates"].append(duplicate)

    errors = validate_coverage(payload)

    assert "duplicate candidate id: SEARCH-001" in errors


def test_validate_coverage_requires_issue_for_active_candidate() -> None:
    payload = valid_payload()
    payload["domains"][0]["candidates"][0]["status"] = "implementing"

    errors = validate_coverage(payload)

    assert any("issue is required" in error for error in errors)


def test_generate_markdown_is_deterministic() -> None:
    payload = valid_payload()

    first = generate_markdown(payload)
    second = generate_markdown(payload)

    assert first == second
    assert "# Azure AI Reference Coverage" in first
    assert "SEARCH-001" in first
    assert "Microsoft Learn" in first


def test_load_coverage_reports_invalid_yaml(tmp_path: Path) -> None:
    source = tmp_path / "coverage.yaml"
    source.write_text("domains: [", encoding="utf-8")

    with pytest.raises(CoverageValidationError, match="Invalid YAML"):
        load_coverage(source)


def test_repository_coverage_files_are_valid_and_in_sync() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "docs" / "reference-coverage.yaml"
    output = repo_root / "docs" / "reference-coverage.md"

    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    assert validate_coverage(payload) == []
    assert output.read_text(encoding="utf-8") == generate_markdown(payload)

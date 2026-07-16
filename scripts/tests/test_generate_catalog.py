import os
import json
import pytest
import yaml
from pathlib import Path
from scripts.generate_catalog import (
    parse_yaml_file,
    should_exclude,
    format_status,
    format_list,
    generate_markdown,
)

def test_parse_yaml_file_valid(tmp_path):
    d = tmp_path / "test.yaml"
    data = {"name": "test-module", "status": "implemented"}
    with open(d, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
    assert parse_yaml_file(d) == data

def test_parse_yaml_file_invalid(tmp_path):
    d = tmp_path / "test.yaml"
    with open(d, "w", encoding="utf-8") as f:
        f.write("invalid: - yaml: :")
    assert parse_yaml_file(d) == {}

def test_should_exclude():
    assert should_exclude(Path("building-blocks/templates/new-building-block/module.yaml")) is True
    assert should_exclude(Path("building-blocks/agents/pipeline-assistant-foundry/module.yaml")) is False
    assert should_exclude(Path("solutions/.venv/solution.yaml")) is True
    assert should_exclude(Path("solutions/.janitor/solution.yaml")) is True

def test_format_status():
    assert "implemented" in format_status("implemented")
    assert "partial" in format_status("partial")
    assert "unknown" in format_status("unknown")

def test_format_list():
    assert format_list(["a", "b"]) == "`a`, `b`"
    assert format_list([]) == "-"
    assert format_list([{"name": "a"}, {"name": "b"}]) == "`a`, `b`"

def test_generate_markdown():
    blocks = [
        {
            "name": "test-block",
            "category": "agents",
            "path": "building-blocks/agents/test-block",
            "status": "implemented",
            "purpose": "A test block.",
            "azure_resources": ["AI Foundry"],
            "inputs": ["customer_question"],
            "outputs": ["answer"]
        }
    ]
    solutions = [
        {
            "name": "test-solution",
            "path": "solutions/test-solution",
            "status": "partial",
            "purpose": "A test solution.",
            "building_blocks": [],
            "inputs": [],
            "outputs": []
        }
    ]

    md = generate_markdown(blocks, solutions)
    assert "# Azure Reference Kit Catalog" in md
    assert "test-block" in md
    assert "test-solution" in md
    assert "AI Foundry" in md

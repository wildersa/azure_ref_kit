"""
Security regression test for least-privilege RBAC guidance in README.
"""

import pathlib
import re


def test_readme_authorization_least_privilege():
    """
    Verifies that the README authorization section recommends least-privilege roles
    and explicitly forbids broad roles (Owner, Contributor).
    """
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    # 1. Ensure the Authorization and Identity section exists
    # We look for the section starting with '## Authorization and Identity'
    # and stopping at the next '## ' (level 2 header) or end of file.
    auth_match = re.search(
        r"## Authorization and Identity\n(.*?)(?=\n##\s|$)", content, re.DOTALL
    )
    assert auth_match, "README.md is missing '## Authorization and Identity' section."
    auth_section = auth_match.group(1)

    # 2. Ensure Least-Privilege Guidance subsection exists and recommends Foundry User
    assert "### Least-Privilege Guidance" in auth_section
    assert "Foundry User" in auth_section
    assert "53ca6127-db72-4b80-b1b0-d745d6d5456d" in auth_section

    # 3. Ensure broad roles are NOT recommended in the guidance
    # We check the content before the "Forbidden Practices" header
    guidance_match = re.search(
        r"### Least-Privilege Guidance(.*?)(?=\*\*Forbidden Practices:\*\*|$)",
        auth_section,
        re.DOTALL,
    )
    assert guidance_match
    guidance_content = guidance_match.group(1)

    forbidden_roles = ["Owner", "Contributor"]
    for role in forbidden_roles:
        assert role not in guidance_content, (
            f"Broad role '{role}' found in recommendation guidance."
        )

    # Wildcard check: look for standalone '*' or '/*' that isn't part of markdown formatting
    # We avoid matching **bold** or *italic*
    wildcard_pattern = r"(?<!\*)\*(?!\*)"
    assert not re.search(wildcard_pattern, guidance_content), (
        "Wildcard '*' found in recommendation guidance."
    )

    # 4. Ensure Forbidden Practices section explicitly mentions broad roles as forbidden
    assert "**Forbidden Practices:**" in auth_section
    forbidden_section = auth_section.split("**Forbidden Practices:**")[1]
    assert "Owner" in forbidden_section
    assert "Contributor" in forbidden_section
    assert "*" in forbidden_section

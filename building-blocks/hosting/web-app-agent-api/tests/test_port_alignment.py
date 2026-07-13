import os
import re
import hcl2


def test_port_alignment_defaults():
    """
    Verify that the default port is consistent across Docker, Python, and Terraform.
    """
    module_root = os.path.join(os.path.dirname(__file__), "..")

    # 1. Check Dockerfile ENV PORT
    dockerfile_path = os.path.join(module_root, "Dockerfile")
    with open(dockerfile_path, "r") as f:
        docker_content = f.read()
    # Look for PORT=8080 (which can be part of an ENV block)
    docker_port_match = re.search(r"PORT=(\d+)", docker_content)
    assert docker_port_match, "Dockerfile missing PORT assignment"
    docker_port = docker_port_match.group(1)

    # 2. Check main.py default port
    main_py_path = os.path.join(module_root, "src", "main.py")
    with open(main_py_path, "r") as f:
        main_py_content = f.read()
    # Look for os.environ.get("PORT", 8080)
    main_py_port_match = re.search(r"get\(\"PORT\", (\d+)\)\)", main_py_content)
    assert main_py_port_match, "main.py missing default port in os.environ.get"
    main_py_port = main_py_port_match.group(1)

    # 3. Check Terraform variables.tf default listen_port
    variables_tf_path = os.path.join(module_root, "infra", "terraform", "variables.tf")
    with open(variables_tf_path, "r") as f:
        variables_tf = hcl2.load(f)

    listen_port_var = next(
        (
            v
            for v in variables_tf.get("variable", [])
            if list(v.keys())[0].strip('"') == "listen_port"
        ),
        None,
    )
    assert listen_port_var, "variables.tf missing listen_port variable"
    tf_port = str(list(listen_port_var.values())[0]["default"])

    # Assert consistency
    assert (
        docker_port == main_py_port == tf_port
    ), f"Port mismatch: Docker={docker_port}, Python={main_py_port}, TF={tf_port}"


def test_dockerfile_uses_unified_python_entrypoint():
    """
    Verify that the Dockerfile uses the Python entrypoint to unify port handling.
    """
    module_root = os.path.join(os.path.dirname(__file__), "..")
    dockerfile_path = os.path.join(module_root, "Dockerfile")
    with open(dockerfile_path, "r") as f:
        docker_content = f.read()

    assert 'CMD ["python", "src/main.py"]' in docker_content

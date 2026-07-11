import os
import yaml
import hcl2
import pytest

def test_module_terraform_alignment():
    module_root = os.path.join(os.path.dirname(__file__), "..")
    module_yaml_path = os.path.join(module_root, "module.yaml")
    variables_tf_path = os.path.join(module_root, "infra", "terraform", "variables.tf")
    outputs_tf_path = os.path.join(module_root, "infra", "terraform", "outputs.tf")

    with open(module_yaml_path, "r") as f:
        module_config = yaml.safe_load(f)

    with open(variables_tf_path, "r") as f:
        variables_tf = hcl2.load(f)

    with open(outputs_tf_path, "r") as f:
        outputs_tf = hcl2.load(f)

    # Extract clean variable and output names from Terraform
    tf_variables = [list(v.keys())[0].strip('"') for v in variables_tf.get("variable", [])]
    tf_outputs = [list(o.keys())[0].strip('"') for o in outputs_tf.get("output", [])]

    # Extract input and output names from module.yaml
    module_inputs = [i["name"] for i in module_config.get("inputs", [])]
    module_outputs = [o["name"] for o in module_config.get("outputs", [])]

    # Required inputs/outputs defined in the task
    required_inputs = ["container_image", "use_managed_identity_for_registry", "listen_port"]
    required_outputs = ["webapp_name", "api_endpoint", "resource_group_name", "principal_id"]

    # Check alignment
    for req_in in required_inputs:
        assert req_in in module_inputs, f"Required input '{req_in}' missing from module.yaml"
        assert req_in in tf_variables, f"Required input '{req_in}' missing from variables.tf"

    for req_out in required_outputs:
        assert req_out in module_outputs, f"Required output '{req_out}' missing from module.yaml"
        assert req_out in tf_outputs, f"Required output '{req_out}' missing from outputs.tf"

def test_managed_identity_default_false():
    module_root = os.path.join(os.path.dirname(__file__), "..")
    variables_tf_path = os.path.join(module_root, "infra", "terraform", "variables.tf")

    with open(variables_tf_path, "r") as f:
        variables_tf = hcl2.load(f)

    # Find the use_managed_identity_for_registry variable
    var_config = next(
        (v for v in variables_tf.get("variable", []) if list(v.keys())[0].strip('"') == "use_managed_identity_for_registry"),
        None
    )

    assert var_config is not None, "use_managed_identity_for_registry variable missing from variables.tf"

    # Get the inner config
    inner_config = list(var_config.values())[0]
    default_val = inner_config.get("default")

    # Handle hcl2 list wrapping if present
    if isinstance(default_val, list):
        default_val = default_val[0]

    # Assert default is false to preserve public-image deployment
    assert default_val is False, "use_managed_identity_for_registry must default to false"

def test_module_yaml_exposed_inputs_are_backed_by_tf():
    module_root = os.path.join(os.path.dirname(__file__), "..")
    module_yaml_path = os.path.join(module_root, "module.yaml")
    variables_tf_path = os.path.join(module_root, "infra", "terraform", "variables.tf")

    with open(module_yaml_path, "r") as f:
        module_config = yaml.safe_load(f)

    with open(variables_tf_path, "r") as f:
        variables_tf = hcl2.load(f)

    tf_variables = [list(v.keys())[0].strip('"') for v in variables_tf.get("variable", [])]
    module_inputs = [i["name"] for i in module_config.get("inputs", [])]

    for module_input in module_inputs:
        assert module_input in tf_variables, f"Input '{module_input}' in module.yaml is not backed by a Terraform variable"

def test_module_yaml_exposed_outputs_are_backed_by_tf():
    module_root = os.path.join(os.path.dirname(__file__), "..")
    module_yaml_path = os.path.join(module_root, "module.yaml")
    outputs_tf_path = os.path.join(module_root, "infra", "terraform", "outputs.tf")

    with open(module_yaml_path, "r") as f:
        module_config = yaml.safe_load(f)

    with open(outputs_tf_path, "r") as f:
        outputs_tf = hcl2.load(f)

    tf_outputs = [list(o.keys())[0].strip('"') for o in outputs_tf.get("output", [])]
    module_outputs = [o["name"] for o in module_config.get("outputs", [])]

    for module_output in module_outputs:
        assert module_output in tf_outputs, f"Output '{module_output}' in module.yaml is not backed by a Terraform output"

#!/bin/bash
set -e

# Deploy preflight script for Document AI Portal
# This script performs a deterministic, non-destructive local preflight that verifies
# the solution package artifacts and deployment prerequisites.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOLUTION_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
DIST_DIR="$SOLUTION_ROOT/dist"
MANIFEST="$DIST_DIR/package-manifest.json"

echo "---------------------------------------------------------"
echo "Document AI Portal: Deployment Preflight"
echo "---------------------------------------------------------"

# 1. Prerequisite Checks
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed. Please install Python 3.x." >&2
    exit 1
fi
echo "  [OK] python3"

# 2. Artifact Verification
echo "Verifying package artifacts..."
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: package-manifest.json not found in $DIST_DIR" >&2
    echo "Please run the package step first: bash $SCRIPT_DIR/package.sh" >&2
    exit 1
fi

# Check individual artifacts defined in the manifest
ARTIFACTS=$(python3 -c "import json; m=json.load(open('$MANIFEST')); print(' '.join([a['name'] for a in m['artifacts']]))")
for art in $ARTIFACTS; do
    ART_DIR="$DIST_DIR/$art"
    if [ ! -d "$ART_DIR" ]; then
        echo "ERROR: Artifact directory missing: $ART_DIR" >&2
        exit 1
    fi
    if [ ! -f "$ART_DIR/artifact-manifest.json" ]; then
        echo "ERROR: Artifact manifest missing: $ART_DIR/artifact-manifest.json" >&2
        exit 1
    fi
    echo "  [OK] Artifact: $art"
done
echo "  [OK] All artifacts present"

# 3. Terraform Validation (Safe Local Only)
INFRA_DIR="$SOLUTION_ROOT/infra/terraform"
if [ -d "$INFRA_DIR" ]; then
    echo "Validating Terraform foundation..."
    if command -v terraform &> /dev/null; then
        echo "  Running terraform fmt -check..."
        terraform -chdir="$INFRA_DIR" fmt -check || { echo "ERROR: Terraform formatting check failed. Run 'terraform fmt -recursive' to fix." >&2; exit 1; }

        echo "  Running terraform init -backend=false..."
        terraform -chdir="$INFRA_DIR" init -backend=false -input=false > /dev/null

        echo "  Running terraform validate..."
        terraform -chdir="$INFRA_DIR" validate || { echo "ERROR: Terraform validation failed." >&2; exit 1; }
        echo "  [OK] Terraform configuration is valid"
    else
        echo "  [SKIP] Terraform/OpenTofu not found. Skipping automated IaC validation."
        echo "         Manual HCL inspection of $INFRA_DIR is recommended."
    fi
fi

echo "---------------------------------------------------------"
echo "Preflight successful: Solution is ready for deployment."
echo "---------------------------------------------------------"
echo ""
echo "Next Steps (Manual Deployment):"
echo "1. Initialize Terraform with your backend configuration:"
echo "   terraform -chdir=solutions/document-ai-portal/infra/terraform init -backend-config=path/to/config.tfvars"
echo ""
echo "2. Apply Terraform to create Azure resources:"
echo "   terraform -chdir=solutions/document-ai-portal/infra/terraform apply"
echo ""
echo "3. Deploy Function Apps (using Azure CLI or Core Tools):"
echo "   az functionapp deployment source config-zip -g <rg> -n <app-name> --src solutions/document-ai-portal/dist/pipeline_function_app.zip"
echo ""
echo "4. Deploy Static Web App (using SWA CLI or GitHub Actions):"
echo "   swa deploy ./solutions/document-ai-portal/dist/portal --env production"
echo ""
echo "NOTE: Real deployment is typically handled by CI/CD pipelines using the artifacts in dist/."

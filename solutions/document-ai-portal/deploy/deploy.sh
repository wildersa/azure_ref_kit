#!/bin/bash
set -e

# Deploy script for Document AI Portal
# This script follows the global solution-composition-contract.

echo "Deploying Document AI Portal..."

# 1. Initialize and apply Terraform in solutions/document-ai-portal/infra/terraform/
# 2. Extract outputs (Function App names, SWA names)
# 3. Deploy artifacts created by package.sh using Azure CLI or GitHub Actions

echo "NOTE: This is a placeholder script. Real deployment logic is handled by the global CI/CD templates."

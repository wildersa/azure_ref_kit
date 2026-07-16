import os
from azure.identity import DefaultAzureCredential


def get_default_credential() -> DefaultAzureCredential:
    """
    Returns a DefaultAzureCredential configured for both local development
    and Azure runtime with Managed Identity.

    If AZURE_CLIENT_ID is present in the environment, it is used as the
    managed_identity_client_id (required for User-Assigned Managed Identity).
    """
    client_id = os.environ.get("AZURE_CLIENT_ID")
    if client_id:
        return DefaultAzureCredential(managed_identity_client_id=client_id)
    return DefaultAzureCredential()

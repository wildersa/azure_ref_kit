import pytest
from unittest.mock import MagicMock, patch
from src.artifact_store import BlobArtifactStore
from src.models import Artifact


@pytest.fixture
def mock_blob_service_client():
    with patch("src.artifact_store.BlobServiceClient") as mock:
        client = mock.return_value
        client.get_container_client.return_value = MagicMock()
        yield client


@pytest.fixture
def artifact_store(mock_blob_service_client):
    return BlobArtifactStore(
        account_url="https://testaccount.blob.core.windows.net",
        container_name="testcontainer",
        credential=MagicMock(),
    )


def test_store_artifact_validates_ids(artifact_store):
    with pytest.raises(ValueError, match="run_id contains invalid characters"):
        artifact_store.store_artifact(
            run_id="bad/id", artifact_id="valid-id", content=b"test", metadata={}
        )


def test_store_artifact_success(artifact_store):
    run_id = "test-run"
    artifact_id = "test-artifact"
    content = b"hello world"
    metadata = {"kind": "text", "safe_name": "hello.txt", "is_customer_visible": True}

    artifact = artifact_store.store_artifact(
        run_id=run_id, artifact_id=artifact_id, content=content, metadata=metadata
    )

    assert artifact.id == artifact_id
    assert artifact.run_id == run_id
    assert artifact.kind == "text"
    assert artifact.storage_ref == f"{run_id}/{artifact_id}"
    assert artifact.is_customer_visible is True

    # Verify SDK call
    artifact_store.container_client.get_blob_client.assert_called_with(
        f"{run_id}/{artifact_id}"
    )
    blob_client = artifact_store.container_client.get_blob_client.return_value
    blob_client.upload_blob.assert_called_once()


def test_store_artifact_enforces_size_limit(artifact_store, monkeypatch):
    monkeypatch.setenv("ARTIFACT_MAX_SIZE_BYTES", "10")
    with pytest.raises(ValueError, match="Artifact content exceeds maximum size"):
        artifact_store.store_artifact(
            run_id="run", artifact_id="art", content=b"this is too long", metadata={}
        )


@patch("src.artifact_store.generate_blob_sas")
def test_get_safe_read_url(mock_generate_sas, artifact_store):
    mock_generate_sas.return_value = "mock-sas-token"
    artifact = Artifact(
        id="art-1",
        run_id="run-1",
        kind="pdf",
        safe_name="doc.pdf",
        storage_ref="run-1/art-1",
        is_customer_visible=True,
    )

    url = artifact_store.get_safe_read_url(artifact)

    assert "mock-sas-token" in url
    assert "https://testaccount.blob.core.windows.net/testcontainer/run-1/art-1" in url
    artifact_store.blob_service_client.get_user_delegation_key.assert_called_once()


def test_get_safe_read_url_validates_lifetime(artifact_store):
    artifact = Artifact(
        id="art-1",
        run_id="run-1",
        kind="pdf",
        safe_name="doc.pdf",
        storage_ref="run-1/art-1",
    )
    with pytest.raises(ValueError, match="must be between 1 and 24"):
        artifact_store.get_safe_read_url(artifact, expires_in_hours=0)
    with pytest.raises(ValueError, match="must be between 1 and 24"):
        artifact_store.get_safe_read_url(artifact, expires_in_hours=25)


def test_artifact_store_validates_container_name():
    with pytest.raises(ValueError, match="Invalid container name"):
        BlobArtifactStore(
            account_url="https://test.blob.core.windows.net",
            container_name="Upper-Case",
            credential=MagicMock(),
        )


def test_store_artifact_validates_content_type(artifact_store):
    with pytest.raises(ValueError, match="Artifact content must be bytes"):
        artifact_store.store_artifact(
            run_id="run", artifact_id="art", content="not bytes", metadata={}
        )

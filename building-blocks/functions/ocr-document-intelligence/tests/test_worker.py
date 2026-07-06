import unittest
from unittest.mock import MagicMock, patch
from src.worker import process_ocr_task


class TestOCRWorker(unittest.TestCase):
    def setUp(self):
        self.run_id = "test-run"
        self.artifact_id = "test-artifact"
        self.document_type = "prebuilt-invoice"
        self.storage_ref = "container/blob.pdf"

        self.doc_intel_adapter = MagicMock()
        self.storage_adapter = MagicMock()

    def test_process_ocr_task_success(self):
        # Mock storage download
        self.storage_adapter.download_blob.return_value = b"fake pdf content"

        # Mock Document Intelligence result
        mock_result = MagicMock()
        mock_result.content = "Extracted text content"
        mock_result.as_dict.return_value = {
            "content": "Extracted text content",
            "documents": [],
        }
        mock_result.documents = [
            MagicMock(
                fields={
                    "InvoiceId": MagicMock(value="INV-123", confidence=0.95),
                    "Total": MagicMock(value=100.0, confidence=0.90),
                }
            )
        ]
        self.doc_intel_adapter.analyze_document.return_value = mock_result

        # Call worker
        result = process_ocr_task(
            self.run_id,
            self.artifact_id,
            self.document_type,
            self.storage_ref,
            self.doc_intel_adapter,
            self.storage_adapter,
        )

        # Verify result
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["extracted_text"], "Extracted text content")
        self.assertEqual(result["fields"]["InvoiceId"], "INV-123")
        self.assertEqual(result["fields"]["Total"], "100.0")
        self.assertAlmostEqual(result["confidence"], 0.925)
        self.assertTrue(len(result["artifacts"]) > 0)
        self.assertIn("finished_at", result)

        # Ensure raw result was uploaded
        self.storage_adapter.upload_blob.assert_called_once()

    def test_process_ocr_task_failure_mapping(self):
        # Mock storage failure
        self.storage_adapter.download_blob.side_effect = Exception("Storage error")

        # Call worker
        result = process_ocr_task(
            self.run_id,
            self.artifact_id,
            self.document_type,
            self.storage_ref,
            self.doc_intel_adapter,
            self.storage_adapter,
        )

        # Verify safe failure response
        self.assertEqual(result["status"], "failed")
        self.assertEqual(
            result["friendly_error"],
            "Document analysis failed. Please ensure the document is clear and in a supported format.",
        )
        self.assertNotIn("Storage error", result["friendly_error"])
        self.assertIn("finished_at", result)

    def test_process_ocr_task_no_unsafe_fields(self):
        # Mock storage download
        self.storage_adapter.download_blob.return_value = b"fake pdf content"

        # Mock Document Intelligence result
        mock_result = MagicMock()
        mock_result.content = "Extracted text content"
        mock_result.as_dict.return_value = {
            "content": "Extracted text content",
            "internal_metadata": "SECRET_STUFF",
            "subscription_id": "123-456",
        }
        mock_result.documents = []
        self.doc_intel_adapter.analyze_document.return_value = mock_result

        # Call worker
        result = process_ocr_task(
            self.run_id,
            self.artifact_id,
            self.document_type,
            self.storage_ref,
            self.doc_intel_adapter,
            self.storage_adapter,
        )

        # Verify no unsafe fields in result
        self.assertNotIn("internal_metadata", result)
        self.assertNotIn("subscription_id", result)
        self.assertNotIn("SECRET_STUFF", str(result))

    @patch("src.worker.logging")
    def test_process_ocr_task_safe_logging(self, mock_logging):
        # Mock failure with sensitive information
        sensitive_error = "Error: https://secret.blob.core.windows.net/container/doc.pdf?sig=SECRET_SAS_TOKEN"
        self.storage_adapter.download_blob.side_effect = Exception(sensitive_error)

        # Call worker
        process_ocr_task(
            self.run_id,
            self.artifact_id,
            self.document_type,
            self.storage_ref,
            self.doc_intel_adapter,
            self.storage_adapter,
        )

        # Verify that the sensitive information was NOT logged
        # Ensure logging.error was called
        mock_logging.error.assert_called()
        # Get the call arguments
        call_args = mock_logging.error.call_args[0][0]
        self.assertNotIn("https://secret.blob.core.windows.net", call_args)
        self.assertNotIn("SECRET_SAS_TOKEN", call_args)


if __name__ == "__main__":
    unittest.main()

from src.worker import validate_fields


def test_validate_fields_valid():
    extracted_data = {
        "fields": {
            "total_amount": {"value": 100.50, "confidence": 0.95},
            "invoice_date": {"value": "2023-10-27", "confidence": 0.99},
            "vendor_name": {"value": "Contoso Corp", "confidence": 0.8},
        }
    }
    ruleset = {
        "required_fields": ["total_amount", "invoice_date", "vendor_name"],
        "confidence_threshold": 0.6,
        "field_types": {
            "total_amount": "number",
            "invoice_date": "date",
            "vendor_name": "string",
        },
    }

    report = validate_fields(extracted_data, ruleset)

    assert report.status == "valid"
    assert len(report.missing_fields) == 0
    assert len(report.invalid_fields) == 0


def test_validate_fields_missing_required():
    extracted_data = {
        "fields": {
            "total_amount": {"value": 100.50, "confidence": 0.95},
            "invoice_date": {"value": "2023-10-27", "confidence": 0.99},
            # vendor_name is missing
        }
    }
    ruleset = {
        "required_fields": ["total_amount", "invoice_date", "vendor_name"],
        "confidence_threshold": 0.6,
    }

    report = validate_fields(extracted_data, ruleset)

    assert report.status == "invalid"
    assert "vendor_name" in report.missing_fields


def test_validate_fields_low_confidence():
    extracted_data = {
        "fields": {
            "total_amount": {"value": 100.50, "confidence": 0.4},  # Below 0.6
            "invoice_date": {"value": "2023-10-27", "confidence": 0.99},
            "vendor_name": {"value": "Contoso Corp", "confidence": 0.8},
        }
    }
    ruleset = {"required_fields": ["total_amount"], "confidence_threshold": 0.6}

    report = validate_fields(extracted_data, ruleset)

    assert report.status == "warning"
    assert len(report.invalid_fields) == 1
    assert "Confidence" in report.invalid_fields[0]["reason"]


def test_validate_fields_wrong_type():
    extracted_data = {
        "fields": {
            "total_amount": {"value": "not a number", "confidence": 0.95},
            "invoice_date": {"value": "2023-10-27", "confidence": 0.99},
            "vendor_name": {"value": "Contoso Corp", "confidence": 0.8},
        }
    }
    ruleset = {
        "required_fields": ["total_amount"],
        "field_types": {"total_amount": "number"},
    }

    report = validate_fields(extracted_data, ruleset)

    assert report.status == "invalid"
    assert len(report.invalid_fields) == 1
    assert "type" in report.invalid_fields[0]["reason"]


def test_customer_safe_output_no_internals():
    extracted_data = {
        "fields": {
            "total_amount": {
                "value": 100.50,
                "confidence": 0.95,
                "internal_id": "secret-123",
            },
        },
        "raw_ocr_payload": {"very": "secret"},
    }
    ruleset = {
        "required_fields": ["total_amount", "vendor_name"],
        "confidence_threshold": 0.6,
    }

    report = validate_fields(extracted_data, ruleset)
    report_dict = report.to_dict()

    # Ensure no internal data is leaked
    report_str = str(report_dict)
    assert "secret-123" not in report_str
    assert "raw_ocr_payload" not in report_str
    assert "very" not in report_str


def test_safety_boundary_on_failure(caplog):
    from function_app import field_validation_worker
    import unittest.mock as mock
    import asyncio

    # Mock storage to throw an exception with sensitive info
    mock_storage = mock.MagicMock()
    mock_storage.read_artifact.side_effect = Exception(
        "Secret SAS token: https://storage.account.com?sig=secret"
    )

    with mock.patch("function_app.StorageAdapter", return_value=mock_storage):
        with mock.patch("os.environ", {"BlobStorageConnectionString": "dummy"}):
            input_data = {"run_id": "test-run", "artifact_id": "test-art"}

            # Run the activity
            result = asyncio.run(field_validation_worker(input_data))

            assert result["status"] == "failed"
            assert (
                result["friendly_error"]
                == "Could not find or read the extracted data artifact."
            )

            # Ensure the sensitive exception message is not in the result
            result_str = str(result)
            assert "Secret SAS token" not in result_str
            assert "secret" not in result_str

            # Ensure the sensitive exception message is NOT in the logs
            log_text = caplog.text
            assert "Secret SAS token" not in log_text
            assert "sig=secret" not in log_text

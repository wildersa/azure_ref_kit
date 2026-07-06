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

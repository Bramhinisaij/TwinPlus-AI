import pandas as pd

from src.validation import validate_health_data


def test_valid_health_data():
    data = pd.DataFrame({
        "patient_id": ["P001", "P002"],
        "heart_rate": [72, 80]
    })

    result = validate_health_data(data)

    assert result["status"] == "Passed"


def test_missing_required_column():
    data = pd.DataFrame({
        "patient_id": ["P001"]
    })

    result = validate_health_data(data)

    assert "heart_rate" in result["missing_required_columns"]


def test_negative_heart_rate():
    data = pd.DataFrame({
        "patient_id": ["P001"],
        "heart_rate": [-5]
    })

    result = validate_health_data(data)

    assert result["invalid_heart_rate"] == 1
    assert result["status"] == "Issues found"
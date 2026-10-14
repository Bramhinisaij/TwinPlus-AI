import pandas as pd
from src.data_quality import assess_data_quality


def test_assess_data_quality():
    data = pd.DataFrame({
        "name": ["Sindhu", "Ravi", None],
        "age": [20, None, 22]
    })

    result = assess_data_quality(data)

    assert result is not None


def test_assess_data_quality_detects_missing_values():
    data = pd.DataFrame({
        "name": ["Sindhu", None, "Ravi"],
        "age": [20, 21, None]
    })

    result = assess_data_quality(data)

    assert result is not None

def test_empty_data():
    data = pd.DataFrame()

    result = assess_data_quality(data)

    assert result["quality_score"] == 0.0
    assert result["status"] == "No data available"

def test_missing_health_readings():
    data = pd.DataFrame({
        "patient_id": ["P001", "P002"],
        "heart_rate": [72, None]
    })

    result = assess_data_quality(data)

    assert result["missing_cells"] == 1
    assert result["total_cells"] == 4
    assert result["quality_score"] == 75.0
    assert result["status"] == "Check data"

def test_duplicate_health_records():
    data = pd.DataFrame({
        "patient_id": ["P001", "P001"],
        "heart_rate": [72, 72]
    })

    result = assess_data_quality(data)

    assert result["quality_score"] == 100.0
    assert result["missing_cells"] == 0
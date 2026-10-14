
from src.simulator import generate_health_data


def test_generate_health_data():
    data = generate_health_data()

    assert len(data) == 10
    assert "patient_id" in data.columns
    assert "heart_rate" in data.columns
    assert "temperature" in data.columns
    assert "oxygen_level" in data.columns


def test_custom_patient_count():
    data = generate_health_data(5)

    assert len(data) == 5

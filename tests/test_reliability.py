import pandas as pd
from src.reliability import assess_reliability
def test_delayed_reading():
    data = pd.DataFrame({
        "heart_rate": [72],
        "temperature": [36.5],
        "oxygen_level": [98],
        "timestamp": [
            pd.Timestamp.now() - pd.Timedelta(minutes=15)
        ]
    })

    result = assess_reliability(data)

    assert result["delayed_readings"] == 1
    assert result["status"] == "Unreliable"


def test_recent_reading():
    data = pd.DataFrame({
        "heart_rate": [72],
        "temperature": [36.5],
        "oxygen_level": [98],
        "timestamp": [pd.Timestamp.now()]
    })

    result = assess_reliability(data)

    assert result["delayed_readings"] == 0
    assert result["status"] == "Reliable"

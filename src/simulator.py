
import pandas as pd
import numpy as np


def generate_health_data(num_patients=10):
    """Generate sample health readings with timestamps."""

    np.random.seed(42)

    data = pd.DataFrame({
        "patient_id": [
            f"P{i:03d}" for i in range(1, num_patients + 1)
        ],
        "heart_rate": np.random.randint(60, 101, num_patients),
        "temperature": np.round(
            np.random.uniform(36.0, 37.5, num_patients), 1
        ),
        "oxygen_level": np.random.randint(95, 100, num_patients),
        "timestamp": [
            pd.Timestamp.now() - pd.Timedelta(minutes=i * 2)
            for i in range(num_patients)
        ]
    })

    return data

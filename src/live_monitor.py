
import random

from src.reading_service import add_health_reading


def generate_simulated_reading(patient_code, patient_user_id):
    """
    Generate a fictional reading for demonstration.
    This is not a real device measurement.
    """

    heart_rate = random.randint(60, 100)
    temperature = round(random.uniform(36.0, 37.5), 1)
    oxygen_level = random.randint(95, 100)

    result = add_health_reading(
        patient_code=patient_code,
        patient_user_id=patient_user_id,
        heart_rate=heart_rate,
        temperature=temperature,
        oxygen_level=oxygen_level,
        source="simulated",
    )

    return {
        "reading_id": result["reading_id"],
        "patient_code": patient_code,
        "heart_rate": heart_rate,
        "temperature": temperature,
        "oxygen_level": oxygen_level,
        "source": "simulated",
        "message": result["message"],
    }

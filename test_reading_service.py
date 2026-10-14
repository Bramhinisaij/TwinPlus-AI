
from src.reading_service import (
    add_health_reading,
    get_patient_readings
)

try:
    result = add_health_reading(
        patient_code="PAT001",
        heart_rate=78,
        temperature=36.8,
        oxygen_level=98
    )

    print(result)

    print("\nPatient health readings:")

    readings = get_patient_readings("PAT001")

    for reading in readings:
        print(reading)

except Exception as error:
    print("Test failed:", error)

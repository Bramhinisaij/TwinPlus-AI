
import pandas as pd


def assess_health_risk(reading):
    """
    Demonstration-only indicator for a single health reading.
    This is not a medical diagnosis or a validated clinical risk score.
    """

    required_fields = [
        "heart_rate",
        "temperature",
        "oxygen_level",
    ]

    # Check that all required readings are present and numeric.
    values = {}

    for field in required_fields:
        try:
            value = float(reading[field])
        except (KeyError, TypeError, ValueError):
            return {
                "status": "Insufficient data",
                "message": f"{field} is missing or invalid.",
                "review_required": True,
            }

        if not pd.notna(value):
            return {
                "status": "Insufficient data",
                "message": f"{field} is missing or invalid.",
                "review_required": True,
            }

        values[field] = value

    heart_rate = values["heart_rate"]
    temperature = values["temperature"]
    oxygen_level = values["oxygen_level"]

    # Reject impossible values rather than interpreting them as risk.
    if (
        heart_rate <= 0
        or temperature <= 0
        or oxygen_level < 0
        or oxygen_level > 100
    ):
        return {
            "status": "Invalid reading",
            "message": "Check the recorded values before interpreting them.",
            "review_required": True,
        }

    # These are demonstration rules, not clinical thresholds.
    flags = []

    if heart_rate < 50 or heart_rate > 120:
        flags.append("Heart rate is outside the demonstration range.")

    if temperature < 35.0 or temperature > 38.0:
        flags.append("Temperature is outside the demonstration range.")

    if oxygen_level < 92:
        flags.append("Oxygen level is outside the demonstration range.")

    if flags:
        return {
            "status": "Flag for review",
            "message": " ".join(flags),
            "review_required": True,
        }

    return {
        "status": "Within demonstration ranges",
        "message": (
            "No configured rule was triggered. "
            "This does not confirm that the person is healthy."
        ),
        "review_required": False,
    }

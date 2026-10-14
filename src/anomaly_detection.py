
import pandas as pd


# Demonstration thresholds only.
# These are not diagnostic or treatment thresholds.
DEMO_RANGES = {
    "heart_rate": (50, 120),
    "temperature": (35.0, 38.0),
    "oxygen_level": (92, 100),
}


def detect_anomalies(data: pd.DataFrame) -> pd.DataFrame:
    """Flag missing, invalid, or out-of-demo-range health readings."""

    results = []

    if data.empty:
        return pd.DataFrame(
            columns=["reading", "value", "status", "message"]
        )

    for column, (minimum, maximum) in DEMO_RANGES.items():

        if column not in data.columns:
            results.append({
                "reading": column,
                "value": "N/A",
                "status": "Missing column",
                "message": f"The {column} column is missing.",
            })
            continue

        values = pd.to_numeric(data[column], errors="coerce")

        for index, value in values.items():

            if pd.isna(value):
                results.append({
                    "reading": column,
                    "value": "Missing or invalid",
                    "status": "Check data",
                    "message": "The reading is missing or not numeric.",
                })

            elif value < minimum or value > maximum:
                results.append({
                    "reading": column,
                    "value": value,
                    "status": "Flagged for review",
                    "message": (
                        f"Outside the demonstration range "
                        f"of {minimum} to {maximum}."
                    ),
                })

    return pd.DataFrame(
        results,
        columns=["reading", "value", "status", "message"],
    )

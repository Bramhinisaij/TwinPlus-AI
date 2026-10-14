import pandas as pd


def validate_health_data(data: pd.DataFrame) -> dict:
    """Check basic validity of health data."""

    issues = {}

    # Check required columns
    required_columns = ["patient_id", "heart_rate"]
    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    # Check heart rate values when the column exists
    invalid_heart_rate = 0

    if "heart_rate" in data.columns:
        heart_rate = pd.to_numeric(
            data["heart_rate"], errors="coerce"
        )

        # Flag non-numeric values and negative values.
        # These are basic data-quality rules, not medical thresholds.
        invalid_heart_rate = int(
            (
                (heart_rate < 0)
                | (
                    data["heart_rate"].notna()
                    & heart_rate.isna()
                )
            ).sum()
        )

    issues["missing_required_columns"] = missing_columns
    issues["invalid_heart_rate"] = invalid_heart_rate

    issues["status"] = (
        "Issues found"
        if missing_columns or invalid_heart_rate > 0
        else "Passed"
    )

    return issues
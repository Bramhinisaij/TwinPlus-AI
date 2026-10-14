
import pandas as pd


def assess_reliability(data: pd.DataFrame) -> dict:
    """Check missing and delayed health readings."""

    if data.empty:
        return {
            "status": "No data available",
            "missing_readings": 0,
            "delayed_readings": 0,
        }

    required_columns = [
        "heart_rate",
        "temperature",
        "oxygen_level",
    ]

    available_columns = [
        column for column in required_columns
        if column in data.columns
    ]

    missing_readings = sum(
        int(data[column].isna().sum())
        for column in available_columns
    )

    delayed_readings = 0

    if "timestamp" in data.columns:
        timestamps = pd.to_datetime(
            data["timestamp"], errors="coerce"
        )

        current_time = pd.Timestamp.now()

        # A reading older than 10 minutes is considered delayed.
        delayed_readings = int(
            (
                (current_time - timestamps)
                > pd.Timedelta(minutes=10)
            ).fillna(False).sum()
        )

        # Invalid timestamps are also counted as delayed.
        delayed_readings += int(timestamps.isna().sum())

    status = (
        "Unreliable"
        if missing_readings > 0 or delayed_readings > 0
        else "Reliable"
    )

    return {
        "status": status,
        "missing_readings": missing_readings,
        "delayed_readings": delayed_readings,
    }

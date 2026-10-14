from src.alert_service import process_reading_alerts
from src.database import get_connection


def main():
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                p.patient_code,
                p.user_id,
                hr.reading_id,
                hr.heart_rate,
                hr.temperature,
                hr.oxygen_level
            FROM health_readings hr
            JOIN patients p ON p.patient_id = hr.patient_id
            ORDER BY hr.reading_id DESC
            LIMIT 20
            """
        )
        readings = cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    if not readings:
        print("No readings found. Save a reading in the app first.")
        return

    print("Checking recent readings for a demo alert...")

    for reading in readings:
        print(
            f"Reading {reading['reading_id']}: "
            f"HR={reading['heart_rate']}, "
            f"Temp={reading['temperature']}, "
            f"Oxygen={reading['oxygen_level']}"
        )

        try:
            result = process_reading_alerts(
                patient_code=reading["patient_code"],
                patient_user_id=reading["user_id"],
                reading_id=reading["reading_id"],
                test_mode=True,
            )
            print("Result:", result)

            if result.get("alerts"):
                print("\nTEST ALERT PROCESSING FINISHED.")
                print("No email was sent because test_mode=True.")
                return

        except Exception as error:
            print(
                f"Could not process reading "
                f"{reading['reading_id']}: {error}"
            )

    print(
        "\nNo alert was created. The recent readings may all be "
        "within the demonstration thresholds, or no eligible "
        "recipient may be available."
    )


if __name__ == "__main__":
    main()
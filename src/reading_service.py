
import math
from datetime import datetime

from src.database import get_connection


def _validate_patient_code(patient_code):
    if not isinstance(patient_code, str) or not patient_code.strip():
        raise ValueError("Patient code is required.")
    return patient_code.strip()


def _validate_reading(heart_rate, temperature, oxygen_level):
    try:
        heart_rate = float(heart_rate)
        temperature = float(temperature)
        oxygen_level = float(oxygen_level)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Reading values must be valid numbers.") from None

    if not all(
        math.isfinite(value)
        for value in (heart_rate, temperature, oxygen_level)
    ):
        raise ValueError("Reading values must be finite numbers.")

    if not 1 <= heart_rate <= 300:
        raise ValueError("Heart rate must be between 1 and 300.")

    if not 20 <= temperature <= 50:
        raise ValueError("Temperature must be between 20 and 50 °C.")

    if not 0 <= oxygen_level <= 100:
        raise ValueError("Oxygen level must be between 0 and 100%.")

    return heart_rate, temperature, oxygen_level


def add_health_reading(
    patient_code,
    heart_rate,
    temperature,
    oxygen_level,
    patient_user_id=None,
    source="manual",
    actor_user_id=None,
):
    """Save a reading only after verifying patient ownership."""
    patient_code = _validate_patient_code(patient_code)

    if patient_user_id is None:
        raise ValueError("Authenticated patient ID is required.")

    if (
        actor_user_id is not None
        and actor_user_id != patient_user_id
    ):
        raise PermissionError("You cannot save readings for another patient.")

    heart_rate, temperature, oxygen_level = _validate_reading(
        heart_rate, temperature, oxygen_level
    )

    if source not in ("manual", "simulated"):
        raise ValueError("Source must be 'manual' or 'simulated'.")

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT p.patient_id
            FROM patients p
            JOIN users u ON u.user_id = p.user_id
            WHERE p.patient_code = %s
              AND p.user_id = %s
              AND u.role = 'patient'
              AND u.is_active = TRUE
            """,
            (patient_code, patient_user_id),
        )

        patient = cursor.fetchone()

        if patient is None:
            raise PermissionError(
                "Patient account verification failed. Reading not saved."
            )

        patient_id = patient[0]

        cursor.execute(
            """
            INSERT INTO health_readings (
                patient_id,
                heart_rate,
                temperature,
                oxygen_level,
                recorded_at,
                source,
                data_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                patient_id,
                heart_rate,
                temperature,
                oxygen_level,
                datetime.now(),
                source,
                "pending",
            ),
        )

        reading_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO audit_logs (
                actor_user_id,
                action,
                target_type,
                target_id
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                patient_user_id,
                "HEALTH_READING_SAVED",
                "health_reading",
                str(reading_id),
            ),
        )

        connection.commit()

        return {
            "reading_id": reading_id,
            "patient_code": patient_code,
            "source": source,
            "message": "Health reading saved and audit entry recorded.",
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_patient_readings(patient_code, patient_user_id=None):
    """Return readings only for the authenticated patient account."""
    patient_code = _validate_patient_code(patient_code)

    if patient_user_id is None:
        raise ValueError("Authenticated patient ID is required.")

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                hr.reading_id,
                p.patient_code,
                hr.heart_rate,
                hr.temperature,
                hr.oxygen_level,
                hr.recorded_at,
                hr.source,
                hr.data_status
            FROM health_readings hr
            JOIN patients p ON p.patient_id = hr.patient_id
            JOIN users u ON u.user_id = p.user_id
            WHERE p.patient_code = %s
              AND p.user_id = %s
              AND u.role = 'patient'
              AND u.is_active = TRUE
            ORDER BY hr.recorded_at DESC, hr.reading_id DESC
            """,
            (patient_code, patient_user_id),
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

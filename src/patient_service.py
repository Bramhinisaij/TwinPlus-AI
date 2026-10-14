
import uuid
from src.database import get_connection


def register_patient(
    full_name,
    email,
    password_hash,
    phone_number=None,
    gender=None,
):
    """Register a patient and create their patient profile."""

    if not full_name or not full_name.strip():
        raise ValueError("Full name is required.")
    if not email or not email.strip():
        raise ValueError("Email is required.")
    if not password_hash:
        raise ValueError("Password is required.")

    full_name = full_name.strip()
    email = email.strip().lower()
    phone_number = phone_number.strip() if phone_number else None
    gender = gender.strip() if gender else None

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users
                (full_name, email, password_hash, role,
                 phone_number, gender)
            VALUES (%s, %s, %s, 'patient', %s, %s)
            """,
            (full_name, email, password_hash, phone_number, gender),
        )

        user_id = cursor.lastrowid
        patient_code = "PAT-" + uuid.uuid4().hex[:8].upper()

        cursor.execute(
            """
            INSERT INTO patients (user_id, patient_code)
            VALUES (%s, %s)
            """,
            (user_id, patient_code),
        )

        connection.commit()

        return {
            "user_id": user_id,
            "patient_code": patient_code,
            "message": "Patient registered successfully.",
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

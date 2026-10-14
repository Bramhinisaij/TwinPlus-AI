
from werkzeug.security import check_password_hash
from src.database import get_connection


def _authenticate(email, password, role):
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.full_name,
                u.email,
                u.password_hash,
                u.role,
                p.patient_code,
                hs.hospital_id,
                h.hospital_name
            FROM users u
            LEFT JOIN patients p ON p.user_id = u.user_id
            LEFT JOIN hospital_staff hs ON hs.user_id = u.user_id
            LEFT JOIN hospitals h ON h.hospital_id = hs.hospital_id
            WHERE u.email = %s
              AND u.role = %s
              AND u.is_active = TRUE
            """,
            (email.strip().lower(), role),
        )

        user = cursor.fetchone()

        if not user:
            return None

        try:
            valid = check_password_hash(user["password_hash"], password)
        except (ValueError, TypeError):
            valid = False

        if not valid:
            return None

        if role == "patient":
            if not user["patient_code"]:
                return None

            return {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "patient_code": user["patient_code"],
                "role": "patient",
            }

        if role == "hospital_staff":
            if not user["hospital_id"]:
                return None

            return {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "hospital_id": user["hospital_id"],
                "hospital_name": user["hospital_name"],
                "role": "hospital_staff",
            }

        if role == "admin":
            return {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": "admin",
            }

        return None

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def authenticate_patient(email, password):
    return _authenticate(email, password, "patient")


def authenticate_hospital_staff(email, password):
    return _authenticate(email, password, "hospital_staff")


def authenticate_admin(email, password):
    return _authenticate(email, password, "admin")

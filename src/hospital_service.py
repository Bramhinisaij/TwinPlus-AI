
from werkzeug.security import check_password_hash
from src.database import get_connection


def authenticate_hospital_staff(email, password):
    """Authenticate an active hospital staff account."""

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
                hs.hospital_id,
                h.hospital_name
            FROM users u
            JOIN hospital_staff hs ON hs.user_id = u.user_id
            JOIN hospitals h ON h.hospital_id = hs.hospital_id
            WHERE u.email = %s
              AND u.role = 'hospital_staff'
              AND u.is_active = TRUE
            """,
            (email.strip().lower(),)
        )

        staff = cursor.fetchone()

        if not staff:
            return None

        try:
            valid = check_password_hash(
                staff["password_hash"], password
            )
        except (ValueError, TypeError):
            valid = False

        if not valid:
            return None

        return {
            "user_id": staff["user_id"],
            "full_name": staff["full_name"],
            "email": staff["email"],
            "hospital_id": staff["hospital_id"],
            "hospital_name": staff["hospital_name"],
            "role": "hospital_staff",
        }

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_accessible_patients(staff_user_id):
    """List patients accessible to an active hospital staff account."""

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT DISTINCT
                p.patient_id,
                p.patient_code,
                patient_user.full_name
            FROM hospital_staff hs
            JOIN users staff_user
                ON staff_user.user_id = hs.user_id
            JOIN patient_hospital_access a
                ON a.hospital_id = hs.hospital_id
            JOIN patients p
                ON p.patient_id = a.patient_id
            JOIN users patient_user
                ON patient_user.user_id = p.user_id
            WHERE hs.user_id = %s
              AND staff_user.role = 'hospital_staff'
              AND staff_user.is_active = TRUE
              AND patient_user.is_active = TRUE
              AND a.consent_status = 'granted'
            ORDER BY patient_user.full_name
            """,
            (staff_user_id,)
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_authorized_patient_readings(staff_user_id, patient_id):
    """Return readings only with active staff and patient accounts
    and current hospital consent.
    """

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
            FROM hospital_staff hs
            JOIN users staff_user
                ON staff_user.user_id = hs.user_id
            JOIN patient_hospital_access a
                ON a.hospital_id = hs.hospital_id
            JOIN patients p
                ON p.patient_id = a.patient_id
            JOIN users patient_user
                ON patient_user.user_id = p.user_id
            JOIN health_readings hr
                ON hr.patient_id = p.patient_id
            WHERE hs.user_id = %s
              AND p.patient_id = %s
              AND staff_user.role = 'hospital_staff'
              AND staff_user.is_active = TRUE
              AND patient_user.is_active = TRUE
              AND a.consent_status = 'granted'
            ORDER BY hr.recorded_at DESC
            """,
            (staff_user_id, patient_id)
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

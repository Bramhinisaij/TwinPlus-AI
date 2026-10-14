
from src.database import get_connection


def get_patient_consents(patient_code):
    """Show hospitals and their current consent status."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                h.hospital_id,
                h.hospital_name,
                h.address,
                COALESCE(a.consent_status, 'not_granted')
                    AS consent_status
            FROM hospitals h
            JOIN patients p
                ON p.patient_code = %s
            LEFT JOIN patient_hospital_access a
                ON a.hospital_id = h.hospital_id
                AND a.patient_id = p.patient_id
            ORDER BY h.hospital_name
            """,
            (patient_code.strip(),),
        )
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def grant_hospital_access(patient_code, hospital_id, user_id):
    """Grant hospital access and save an audit entry."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT patient_id
            FROM patients
            WHERE patient_code = %s AND user_id = %s
            """,
            (patient_code.strip(), user_id),
        )
        patient = cursor.fetchone()

        if patient is None:
            raise ValueError("Patient account could not be verified.")

        patient_id = patient[0]

        cursor.execute(
            """
            SELECT access_id
            FROM patient_hospital_access
            WHERE patient_id = %s AND hospital_id = %s
            """,
            (patient_id, hospital_id),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE patient_hospital_access
                SET consent_status = 'granted',
                    granted_by_user_id = %s,
                    granted_at = CURRENT_TIMESTAMP,
                    revoked_at = NULL
                WHERE access_id = %s
                """,
                (user_id, existing[0]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO patient_hospital_access (
                    patient_id,
                    hospital_id,
                    granted_by_user_id,
                    consent_status
                )
                VALUES (%s, %s, %s, 'granted')
                """,
                (patient_id, hospital_id, user_id),
            )

        cursor.execute(
            """
            INSERT INTO audit_logs (
                actor_user_id, action, target_type, target_id
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                "HOSPITAL_ACCESS_GRANTED",
                "patient_hospital_access",
                f"patient_id={patient_id},hospital_id={hospital_id}",
            ),
        )

        connection.commit()
        return "Hospital access granted successfully."

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def revoke_hospital_access(patient_code, hospital_id, user_id):
    """Revoke hospital access and save an audit entry."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT patient_id
            FROM patients
            WHERE patient_code = %s AND user_id = %s
            """,
            (patient_code.strip(), user_id),
        )
        patient = cursor.fetchone()

        if patient is None:
            raise ValueError("Patient account could not be verified.")

        patient_id = patient[0]

        cursor.execute(
            """
            UPDATE patient_hospital_access
            SET consent_status = 'revoked',
                revoked_at = CURRENT_TIMESTAMP
            WHERE patient_id = %s
              AND hospital_id = %s
              AND consent_status = 'granted'
            """,
            (patient_id, hospital_id),
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return "No active access was found for this hospital."

        cursor.execute(
            """
            INSERT INTO audit_logs (
                actor_user_id, action, target_type, target_id
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                "HOSPITAL_ACCESS_REVOKED",
                "patient_hospital_access",
                f"patient_id={patient_id},hospital_id={hospital_id}",
            ),
        )

        connection.commit()
        return "Hospital access revoked successfully."

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_patient_access_history(patient_code, user_id):
    """Retrieve a patient's hospital access change history."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.audit_id,
                h.hospital_name,
                a.action,
                a.created_at
            FROM patients p
            JOIN audit_logs a
                ON a.target_type = 'patient_hospital_access'
                AND a.target_id LIKE CONCAT(
                    'patient_id=', p.patient_id, ',hospital_id=%'
                )
            LEFT JOIN hospitals h
                ON a.target_id = CONCAT(
                    'patient_id=', p.patient_id,
                    ',hospital_id=', h.hospital_id
                )
            WHERE p.patient_code = %s
              AND p.user_id = %s
              AND a.action IN (
                  'HOSPITAL_ACCESS_GRANTED',
                  'HOSPITAL_ACCESS_REVOKED'
              )
            ORDER BY a.created_at DESC, a.audit_id DESC
            """,
            (patient_code.strip(), user_id),
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

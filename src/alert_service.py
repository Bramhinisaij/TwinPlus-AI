
import os
import smtplib
from email.message import EmailMessage

from src.database import get_connection
from src.consent_service import get_patient_consents
from src.health_risk import assess_health_risk


ALERT_TYPE = "DEMO_REVIEW_REQUIRED"


def _get_reading(patient_code, patient_user_id, reading_id):
    """Verify ownership and retrieve the requested reading."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                p.patient_id,
                p.patient_code,
                u.email AS patient_email,
                hr.reading_id,
                hr.heart_rate,
                hr.temperature,
                hr.oxygen_level,
                hr.recorded_at,
                hr.source
            FROM patients p
            JOIN users u ON u.user_id = p.user_id
            JOIN health_readings hr ON hr.patient_id = p.patient_id
            WHERE p.patient_code = %s
              AND p.user_id = %s
              AND u.role = 'patient'
              AND u.is_active = TRUE
              AND hr.reading_id = %s
            """,
            (patient_code.strip(), patient_user_id, reading_id),
        )
        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def _get_hospital_emails(hospital_id):
    """Find hospital staff emails using the existing table structure."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SHOW COLUMNS FROM hospital_staff")
        columns = {
            row["Field"].lower() for row in cursor.fetchall()
        }

        if "hospital_id" not in columns:
            return []

        if "email" in columns:
            cursor.execute(
                """
                SELECT DISTINCT email
                FROM hospital_staff
                WHERE hospital_id = %s
                  AND email IS NOT NULL
                  AND email <> ''
                """,
                (hospital_id,),
            )
            return [
                row["email"].strip()
                for row in cursor.fetchall()
                if row["email"] and row["email"].strip()
            ]

        if "user_id" in columns:
            cursor.execute(
                """
                SELECT DISTINCT u.email
                FROM hospital_staff hs
                JOIN users u ON u.user_id = hs.user_id
                WHERE hs.hospital_id = %s
                  AND u.is_active = TRUE
                  AND u.email IS NOT NULL
                  AND u.email <> ''
                """,
                (hospital_id,),
            )
            return [
                row["email"].strip()
                for row in cursor.fetchall()
                if row["email"] and row["email"].strip()
            ]

        return []

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def _send_email(recipient, subject, body):
    """Send an email using SMTP environment configuration."""
    host = os.getenv("TWINPLUS_SMTP_HOST")
    username = os.getenv("TWINPLUS_SMTP_USERNAME")
    password = os.getenv("TWINPLUS_SMTP_PASSWORD")
    sender = os.getenv("TWINPLUS_FROM_EMAIL")
    port = int(os.getenv("TWINPLUS_SMTP_PORT", "587"))

    if not all((host, username, password, sender)):
        raise RuntimeError(
            "Email is not configured. Set the TwinPlus SMTP "
            "environment variables before enabling real delivery."
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(message)


def _save_alert(
    reading_id,
    patient_id,
    recipient_type,
    recipient_email,
    message,
    test_mode,
):
    """Store an alert and avoid duplicate notifications."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT IGNORE INTO alert_history (
                reading_id,
                patient_id,
                recipient_type,
                recipient_email,
                alert_type,
                alert_message,
                delivery_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                reading_id,
                patient_id,
                recipient_type,
                recipient_email,
                ALERT_TYPE,
                message,
                "pending",
            ),
        )

        inserted = cursor.rowcount == 1

        cursor.execute(
            """
            SELECT alert_id, delivery_status
            FROM alert_history
            WHERE reading_id = %s
              AND recipient_type = %s
              AND recipient_email = %s
              AND alert_type = %s
            """,
            (
                reading_id,
                recipient_type,
                recipient_email,
                ALERT_TYPE,
            ),
        )
        alert = cursor.fetchone()

        if not alert:
            raise RuntimeError("Could not retrieve the saved alert.")

        alert_id, status = alert

        if not inserted and status == "sent":
            connection.commit()
            return {"alert_id": alert_id, "status": "duplicate_skipped"}

        if test_mode:
            cursor.execute(
                """
                UPDATE alert_history
                SET delivery_status = 'test_mode'
                WHERE alert_id = %s
                """,
                (alert_id,),
            )
            connection.commit()
            return {"alert_id": alert_id, "status": "test_mode"}

        # A previous test-mode entry can be delivered when explicitly
        # switching to real email mode.
        cursor.execute(
            """
            UPDATE alert_history
            SET delivery_status = 'pending'
            WHERE alert_id = %s
            """,
            (alert_id,),
        )
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    try:
        _send_email(
            recipient_email,
            "TwinPlus AI: Reading flagged for review",
            message,
        )
        status = "sent"
    except Exception:
        status = "failed"

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE alert_history
            SET delivery_status = %s,
                sent_at = CASE
                    WHEN %s = 'sent' THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END
            WHERE alert_id = %s
            """,
            (status, status, alert_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    return {"alert_id": alert_id, "status": status}


def process_reading_alerts(
    patient_code,
    patient_user_id,
    reading_id,
    test_mode=True,
):
    """
    Create review alerts for one owned reading.

    test_mode=True records alerts without sending emails.
    Hospital recipients are included only with current consent.
    """
    reading = _get_reading(
        patient_code, patient_user_id, reading_id
    )

    if reading is None:
        raise PermissionError(
            "Patient ownership could not be verified for this reading."
        )

    risk = assess_health_risk(reading)

    if not risk.get("review_required"):
        return {
            "message": "No demonstration review alert was triggered.",
            "alerts": [],
        }

    # Do not include actual medical measurements in the email.
    message = (
        "A health reading in TwinPlus AI was flagged by a "
        "demonstration rule for review. This is not a diagnosis. "
        "Please sign in to the application and review the record."
    )

    recipients = []

    patient_email = reading.get("patient_email")
    if patient_email and patient_email.strip():
        recipients.append(("patient", patient_email.strip()))

    # Consent is retrieved again for every processing request.
    consents = get_patient_consents(patient_code)

    for consent in consents:
        if consent.get("consent_status") != "granted":
            continue

        for email in _get_hospital_emails(consent["hospital_id"]):
            recipients.append(("hospital", email))

    # Avoid processing the same recipient twice.
    recipients = list(dict.fromkeys(recipients))

    results = []
    for recipient_type, email in recipients:
        result = _save_alert(
            reading["reading_id"],
            reading["patient_id"],
            recipient_type,
            email,
            message,
            test_mode,
        )
        result["recipient_type"] = recipient_type
        results.append(result)

    return {
        "message": "Alert processing completed.",
        "risk_status": risk["status"],
        "test_mode": test_mode,
        "alerts": results,
    }


def get_alert_history(patient_code, patient_user_id):
    """Return alert history only for the authenticated patient."""
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                ah.alert_id,
                ah.reading_id,
                ah.recipient_type,
                ah.recipient_email,
                ah.alert_type,
                ah.alert_message,
                ah.delivery_status,
                ah.created_at,
                ah.sent_at
            FROM alert_history ah
            JOIN patients p ON p.patient_id = ah.patient_id
            WHERE p.patient_code = %s
              AND p.user_id = %s
            ORDER BY ah.created_at DESC, ah.alert_id DESC
            """,
            (patient_code.strip(), patient_user_id),
        )
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from werkzeug.security import check_password_hash, generate_password_hash

from src.database import get_connection


OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5


def _send_email_otp(email, otp):
    """Send the password reset OTP to the user's registered email."""

    host = os.getenv("TWINPLUS_SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("TWINPLUS_SMTP_PORT", "587"))
    username = os.getenv("TWINPLUS_SMTP_USERNAME")
    password = os.getenv("TWINPLUS_SMTP_PASSWORD")
    from_email = os.getenv("TWINPLUS_FROM_EMAIL") or username

    if not username or not password or not from_email:
        raise RuntimeError(
            "Email is not configured. Set the TWINPLUS_SMTP_USERNAME, "
            "TWINPLUS_SMTP_PASSWORD, and TWINPLUS_FROM_EMAIL variables."
        )

    message = EmailMessage()
    message["Subject"] = "TwinPlus AI - Password Reset OTP"
    message["From"] = from_email
    message["To"] = email
    message.set_content(
        f"""Hello,

Your TwinPlus AI password reset OTP is: {otp}

This code expires in {OTP_EXPIRY_MINUTES} minutes.
If you did not request this code, please ignore this email.

TwinPlus AI Security Team
"""
    )

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(message)


def request_password_reset(email, channel="email"):
    """Create and email a new OTP for an active account."""

    if channel != "email":
        raise ValueError(
            "Phone OTP is not configured yet. Set up an SMS provider first."
        )

    if not email or not email.strip():
        raise ValueError("Please enter your registered email address.")

    email = email.strip().lower()
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, email, is_active
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,),
        )
        user = cursor.fetchone()

        generic_message = (
            "If an active account exists for that email, "
            "a password reset code will be sent."
        )

        if not user or not user["is_active"]:
            return generic_message

        otp = f"{secrets.randbelow(1_000_000):06d}"
        otp_hash = generate_password_hash(otp)
        expires_at = datetime.now() + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        )

        # Remove previous OTPs before creating a new one.
        cursor.execute(
            "DELETE FROM password_reset_otps WHERE user_id = %s",
            (user["user_id"],),
        )

        cursor.execute(
            """
            INSERT INTO password_reset_otps
                (user_id, otp_hash, channel, expires_at, attempts)
            VALUES (%s, %s, 'email', %s, 0)
            """,
            (user["user_id"], otp_hash, expires_at),
        )

        connection.commit()

        try:
            _send_email_otp(email, otp)
        except Exception as exc:
            cursor.execute(
                "DELETE FROM password_reset_otps WHERE user_id = %s",
                (user["user_id"],),
            )
            connection.commit()
            raise RuntimeError(
                "Could not send OTP email. Check SMTP configuration. "
                f"Details: {exc}"
            ) from exc

        return generic_message

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def verify_otp_and_reset_password(email, otp, new_password):
    """Verify the OTP and update the account password."""

    if not email or not email.strip():
        raise ValueError("Please enter your registered email address.")

    if not otp or not otp.strip():
        raise ValueError("Please enter the OTP sent to your email.")

    if not new_password:
        raise ValueError("Please enter a new password.")

    if len(new_password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    email = email.strip().lower()
    otp = otp.strip()

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                r.reset_id,
                r.user_id,
                r.otp_hash,
                r.expires_at,
                r.attempts
            FROM password_reset_otps AS r
            JOIN users AS u ON u.user_id = r.user_id
            WHERE u.email = %s
              AND u.is_active = 1
              AND r.channel = 'email'
            ORDER BY r.created_at DESC, r.reset_id DESC
            LIMIT 1
            """,
            (email,),
        )

        reset_record = cursor.fetchone()

        if not reset_record:
            raise ValueError(
                "No reset request found. Please request a new OTP."
            )

        if reset_record["attempts"] >= MAX_OTP_ATTEMPTS:
            cursor.execute(
                "DELETE FROM password_reset_otps WHERE user_id = %s",
                (reset_record["user_id"],),
            )
            connection.commit()
            raise ValueError(
                "Too many incorrect attempts. Please request a new OTP."
            )

        if reset_record["expires_at"] <= datetime.now():
            cursor.execute(
                "DELETE FROM password_reset_otps WHERE user_id = %s",
                (reset_record["user_id"],),
            )
            connection.commit()
            raise ValueError("OTP expired. Please request a new one.")

        if not check_password_hash(reset_record["otp_hash"], otp):
            cursor.execute(
                """
                UPDATE password_reset_otps
                SET attempts = attempts + 1
                WHERE reset_id = %s
                """,
                (reset_record["reset_id"],),
            )
            connection.commit()
            raise ValueError("Incorrect OTP. Please check and try again.")

        new_password_hash = generate_password_hash(new_password)

        cursor.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE user_id = %s
            """,
            (new_password_hash, reset_record["user_id"]),
        )

        cursor.execute(
            "DELETE FROM password_reset_otps WHERE user_id = %s",
            (reset_record["user_id"],),
        )

        connection.commit()
        return "Password reset successfully. You can now log in."

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

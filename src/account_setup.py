
from src.database import get_connection


def setup_account_fields():
    """Add account contact fields and the password-reset OTP table safely."""

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        # Check existing columns so we do not add duplicates.
        cursor.execute("SHOW COLUMNS FROM users")
        existing_columns = {
            row[0] for row in cursor.fetchall()
        }

        if "phone_number" not in existing_columns:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL"
            )
            print("Added phone_number to users.")

        if "gender" not in existing_columns:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN gender VARCHAR(30) NULL"
            )
            print("Added gender to users.")

        # Store hashed OTPs, expiry times, and attempt counts.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_otps (
                reset_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                otp_hash VARCHAR(255) NOT NULL,
                channel ENUM('email', 'phone') NOT NULL,
                expires_at DATETIME NOT NULL,
                attempts INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_reset_user (user_id),
                INDEX idx_reset_expiry (expires_at)
            )
            """
        )

        connection.commit()
        print("TwinPlus AI account setup completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


if __name__ == "__main__":
    setup_account_fields()

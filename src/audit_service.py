
from src.database import get_connection


def log_action(
    actor_user_id,
    action,
    target_type,
    target_id=None,
):
    """Record an application action in the audit log."""

    if not action or not action.strip():
        raise ValueError("Action is required.")

    if not target_type or not target_type.strip():
        raise ValueError("Target type is required.")

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

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
                actor_user_id,
                action.strip(),
                target_type.strip(),
                str(target_id) if target_id is not None else None,
            ),
        )

        connection.commit()

        return {
            "audit_id": cursor.lastrowid,
            "message": "Audit log saved successfully.",
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_recent_audit_logs(limit=50):
    """Retrieve recent audit log entries."""

    limit = int(limit)

    if not 1 <= limit <= 500:
        raise ValueError("Limit must be between 1 and 500.")

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.audit_id,
                a.actor_user_id,
                u.full_name AS actor_name,
                a.action,
                a.target_type,
                a.target_id,
                a.created_at
            FROM audit_logs a
            LEFT JOIN users u
                ON u.user_id = a.actor_user_id
            ORDER BY a.created_at DESC, a.audit_id DESC
            LIMIT %s
            """,
            (limit,),
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

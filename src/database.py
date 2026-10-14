
import os
import mysql.connector
import streamlit as st


def get_connection():
    """Connect to the TwinPlus AI MySQL database."""

    config = {
        "host": os.getenv("TWINPLUS_DB_HOST", "localhost"),
        "port": int(os.getenv("TWINPLUS_DB_PORT", "3306")),
        "user": os.getenv("TWINPLUS_DB_USER", "root"),
        "password": os.getenv("TWINPLUS_DB_PASSWORD", ""),
        "database": "twinplus_ai",
    }

    # Use Streamlit secrets if they are configured.
    try:
        mysql_settings = st.secrets["mysql"]
        config.update(dict(mysql_settings))
    except (FileNotFoundError, KeyError):
        pass

    return mysql.connector.connect(**config)


def get_hospitals():
    """Retrieve hospitals stored in MySQL."""

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT hospital_id, hospital_name, address
            FROM hospitals
            ORDER BY hospital_id
            """
        )

        hospitals = cursor.fetchall()
        return hospitals

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


import streamlit as st
from werkzeug.security import generate_password_hash

from src.auth_service import (
    authenticate_patient,
    authenticate_hospital_staff,
    authenticate_admin,
)
from src.patient_service import register_patient
from src.patient_page import show_patient_page
from src.hospital_page import show_hospital_page
from src.audit_service import get_recent_audit_logs


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TwinPlus AI",
    page_icon="🏥",
    layout="wide",
)

st.title("TwinPlus AI")
st.subheader("Healthcare Digital Twin Platform")
st.divider()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "patient" not in st.session_state:
    st.session_state["patient"] = None

account = st.session_state["patient"]


# --------------------------------------------------
# LOGIN FUNCTION
# --------------------------------------------------

def login_form(title, role, authenticate):
    st.header(title)

    with st.form(f"{role}_login_form"):
        email = st.text_input(
            "Email Address",
            key=f"{role}_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            key=f"{role}_password",
        )

        submitted = st.form_submit_button("Login")

    if submitted:
        if not email.strip() or not password:
            st.error("Enter your email and password.")
            return

        try:
            user = authenticate(email.strip(), password)

            if user:
                st.session_state["patient"] = user
                st.rerun()
            else:
                st.error("Invalid email or password.")

        except Exception as error:
            st.error(f"Login failed: {error}")


# --------------------------------------------------
# LOGGED-IN DASHBOARDS
# --------------------------------------------------

if account is not None:

    st.sidebar.success(
        f"Logged in: {account['full_name']}"
    )

    st.sidebar.write(
        "Account type: "
        + account["role"].replace("_", " ").title()
    )

    if st.sidebar.button("Log Out"):
        st.session_state["patient"] = None
        st.rerun()

    # Patient dashboard
    if account["role"] == "patient":
        show_patient_page()

    # Hospital staff dashboard
    elif account["role"] == "hospital_staff":
        show_hospital_page()

    # Administrator dashboard
    elif account["role"] == "admin":

        st.title("Admin Dashboard")
        st.write(f"Welcome, {account['full_name']}.")

        st.subheader("Audit Log Viewer")

        limit = st.selectbox(
            "Number of recent entries",
            [10, 25, 50, 100],
            index=1,
        )

        if st.button("Refresh Audit Logs"):
            st.rerun()

        try:
            logs = get_recent_audit_logs(limit)

            if logs:
                st.dataframe(
                    logs,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No audit log entries are available.")

        except Exception as error:
            st.error(
                f"Could not load audit logs: {error}"
            )

        st.caption(
            "Audit logs support accountability but are "
            "not tamper-proof in this prototype."
        )

    else:
        st.error(
            "Unrecognized account role. Please log out."
        )


# --------------------------------------------------
# LOGIN AND REGISTRATION TABS
# --------------------------------------------------

else:

    patient_tab, hospital_tab, admin_tab, register_tab = st.tabs(
        [
            "Patient Login",
            "Hospital Staff Login",
            "Admin Login",
            "Patient Registration",
        ]
    )

    # PATIENT LOGIN
    with patient_tab:
        login_form(
            "Patient Login",
            "patient",
            authenticate_patient,
        )

    # HOSPITAL STAFF LOGIN
    with hospital_tab:
        login_form(
            "Hospital Staff Login",
            "hospital",
            authenticate_hospital_staff,
        )

    # ADMIN LOGIN
    with admin_tab:
        st.header("Administrator Login")

        st.write(
            "Authorized administrators can review audit logs."
        )

        login_form(
            "Administrator Login",
            "admin",
            authenticate_admin,
        )

    # PATIENT REGISTRATION
    with register_tab:

        st.header("Patient Registration")

        with st.form("patient_registration_form"):

            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")

            gender = st.selectbox(
                "Gender",
                [
                    "Prefer not to say",
                    "Female",
                    "Male",
                    "Other",
                ],
            )

            password = st.text_input(
                "Create Password",
                type="password",
            )

            confirm = st.text_input(
                "Confirm Password",
                type="password",
            )

            submitted = st.form_submit_button(
                "Register Patient"
            )

        if submitted:

            if not full_name.strip() or not email.strip():
                st.error("Name and email are required.")

            elif len(password) < 8:
                st.error(
                    "Password must contain at least 8 characters."
                )

            elif password != confirm:
                st.error("Passwords do not match.")

            else:
                try:
                    result = register_patient(
                        full_name=full_name.strip(),
                        email=email.strip(),
                        password_hash=generate_password_hash(
                            password
                        ),
                        phone_number=phone.strip() or None,
                        gender=(
                            None
                            if gender == "Prefer not to say"
                            else gender
                        ),
                    )

                    st.success(
                        "Registration successful! Patient code: "
                        + result["patient_code"]
                    )

                    st.info(
                        "You can now log in using Patient Login."
                    )

                except Exception as error:
                    st.error(
                        f"Registration failed: {error}"
                    )

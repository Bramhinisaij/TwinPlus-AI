
import streamlit as st
import pandas as pd
import plotly.express as px

from src.reading_service import (
    add_health_reading,
    get_patient_readings,
)
from src.live_monitor import generate_simulated_reading
from src.consent_service import (
    get_patient_consents,
    grant_hospital_access,
    revoke_hospital_access,
    get_patient_access_history,
)
from src.anomaly_detection import detect_anomalies
from src.health_risk import assess_health_risk
from src.validation import validate_health_data
from src.reliability import assess_reliability
from src.data_quality import assess_data_quality
from src.database import get_hospitals
from src.alert_service import get_alert_history, process_reading_alerts


def show_patient_page():
    st.title("Patient Digital Twin Portal")
    st.caption(
        "TwinPlus AI — healthcare demonstration prototype. "
        "Results are not medical diagnoses or treatment advice."
    )

    # --------------------------------------------------
    # 1. AUTHENTICATED PATIENT DETAILS
    # --------------------------------------------------
    patient = st.session_state.get("patient", {})

    patient_code = (
        st.session_state.get("patient_code")
        or patient.get("patient_code")
    )

    user_id = (
        st.session_state.get("user_id")
        or patient.get("user_id")
    )

    if not patient_code or user_id is None:
        st.error(
            "Patient session information is missing. "
            "Please log in again."
        )
        return

    st.success(f"Patient Code: {patient_code}")

    # --------------------------------------------------
    # 2. LOAD PATIENT READING HISTORY
    # --------------------------------------------------
    try:
        readings = get_patient_readings(
            patient_code,
            patient_user_id=user_id,
        )
        df = pd.DataFrame(readings)

    except Exception as error:
        st.error(f"Unable to load readings: {error}")
        return

    # --------------------------------------------------
    # 3. SIMULATED LIVE MONITORING
    # --------------------------------------------------
    st.header("Live Monitoring")

    st.write(
        "Generate a demonstration reading to test the "
        "digital twin monitoring features."
    )

    if st.button(
        "Generate Simulated Reading",
        key="generate_simulated_reading",
    ):
        try:
            simulated = generate_simulated_reading()

            saved = add_health_reading(
                patient_code=patient_code,
                heart_rate=simulated["heart_rate"],
                temperature=simulated["temperature"],
                oxygen_level=simulated["oxygen_level"],
                patient_user_id=user_id,
                source="simulated",
                actor_user_id=user_id,
            )

            st.success(
                f"Simulated reading saved. "
                f"Reading ID: {saved['reading_id']}"
            )

            st.rerun()

        except Exception as error:
            st.error(
                f"Unable to generate or save reading: {error}"
            )

    # --------------------------------------------------
    # 4. MANUAL HEALTH READING
    # --------------------------------------------------
    st.header("Record Health Reading")

    with st.form("manual_health_reading_form"):
        heart_rate = st.number_input(
            "Heart Rate (beats per minute)",
            min_value=1,
            max_value=300,
            value=75,
            step=1,
        )

        temperature = st.number_input(
            "Body Temperature (°C)",
            min_value=20.0,
            max_value=50.0,
            value=36.8,
            step=0.1,
        )

        oxygen_level = st.number_input(
            "Oxygen Level (%)",
            min_value=0.0,
            max_value=100.0,
            value=98.0,
            step=1.0,
        )

        save_reading = st.form_submit_button(
            "Save Reading"
        )

    if save_reading:
        try:
            saved = add_health_reading(
                patient_code=patient_code,
                heart_rate=heart_rate,
                temperature=temperature,
                oxygen_level=oxygen_level,
                patient_user_id=user_id,
                source="manual",
                actor_user_id=user_id,
            )

            st.success(
                f"Reading saved successfully. "
                f"Reading ID: {saved['reading_id']}"
            )

            st.rerun()

        except Exception as error:
            st.error(f"Unable to save reading: {error}")

    # Reload after possible changes.
    try:
        readings = get_patient_readings(
            patient_code,
            patient_user_id=user_id,
        )
        df = pd.DataFrame(readings)

    except Exception as error:
        st.error(f"Unable to refresh readings: {error}")
        return

    # --------------------------------------------------
    # 5. PATIENT DASHBOARD AND LATEST METRICS
    # --------------------------------------------------
    st.header("Health Dashboard")

    if df.empty:
        st.info(
            "No readings recorded yet. Save a manual reading "
            "or generate a simulated reading to begin."
        )
        latest = None

    else:
        df["recorded_at"] = pd.to_datetime(
            df["recorded_at"],
            errors="coerce",
        )

        df = df.sort_values(
            ["recorded_at", "reading_id"],
            ascending=[False, False],
        ).reset_index(drop=True)

        latest = df.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Heart Rate",
            f"{float(latest['heart_rate']):.0f} bpm",
        )

        col2.metric(
            "Temperature",
            f"{float(latest['temperature']):.1f} °C",
        )

        col3.metric(
            "Oxygen Level",
            f"{float(latest['oxygen_level']):.0f}%",
        )

        st.caption(
            f"Latest reading source: {latest.get('source', 'unknown')} "
            f"| Recorded: {latest['recorded_at']}"
        )

        st.subheader("Reading Trends")

        chart_df = df.dropna(
            subset=[
                "recorded_at",
                "heart_rate",
                "temperature",
                "oxygen_level",
            ]
        ).sort_values("recorded_at")

        if not chart_df.empty:
            heart_chart = px.line(
                chart_df,
                x="recorded_at",
                y="heart_rate",
                markers=True,
                title="Heart Rate Over Time",
            )
            st.plotly_chart(
                heart_chart,
                use_container_width=True,
            )

            temperature_chart = px.line(
                chart_df,
                x="recorded_at",
                y="temperature",
                markers=True,
                title="Temperature Over Time",
            )
            st.plotly_chart(
                temperature_chart,
                use_container_width=True,
            )

            oxygen_chart = px.line(
                chart_df,
                x="recorded_at",
                y="oxygen_level",
                markers=True,
                title="Oxygen Level Over Time",
            )
            st.plotly_chart(
                oxygen_chart,
                use_container_width=True,
            )

    # --------------------------------------------------
    # 6. DEMONSTRATION HEALTH-RISK ASSESSMENT
    # --------------------------------------------------
    st.header("Demonstration Health-Risk Assessment")

    if latest is not None:
        try:
            risk_input = {
                "heart_rate": latest["heart_rate"],
                "temperature": latest["temperature"],
                "oxygen_level": latest["oxygen_level"],
            }

            risk = assess_health_risk(risk_input)

            st.write("**Status:**", risk["status"])
            st.write("**Explanation:**", risk["message"])

            if risk.get("review_required"):
                st.warning(
                    "The configured demonstration rules flagged "
                    "this reading for review. This is not a "
                    "clinical assessment."
                )
            else:
                st.info(
                    "No configured demonstration rule was "
                    "triggered. This does not establish that "
                    "the person is healthy."
                )

        except Exception as error:
            st.error(
                f"Unable to assess the demonstration reading: {error}"
            )

    # --------------------------------------------------
    # 7. ANOMALY DETECTION AND DATA QUALITY
    # --------------------------------------------------
    st.header("Anomaly Detection")

    if not df.empty:
        try:
            anomaly_df = detect_anomalies(df)

            if anomaly_df.empty:
                st.success(
                    "No anomalies were flagged by the configured "
                    "demonstration rules."
                )
            else:
                st.dataframe(
                    anomaly_df,
                    use_container_width=True,
                )

        except Exception as error:
            st.error(
                f"Unable to detect anomalies: {error}"
            )

        with st.expander(
            "Data Quality, Validation and Reliability"
        ):
            try:
                quality = assess_data_quality(df)
                st.subheader("Data Quality")
                st.write(quality)

            except Exception as error:
                st.warning(
                    f"Data quality assessment unavailable: {error}"
                )

            try:
                validation = validate_health_data(df)
                st.subheader("Data Validation")
                st.write(validation)

            except Exception as error:
                st.warning(
                    f"Data validation unavailable: {error}"
                )

            try:
                reliability = assess_reliability(df)
                st.subheader("Data Reliability")
                st.write(reliability)

            except Exception as error:
                st.warning(
                    f"Reliability assessment unavailable: {error}"
                )

    # --------------------------------------------------
    # 8. COMPLETE READING HISTORY
    # --------------------------------------------------
    st.header("Complete Reading History")

    if df.empty:
        st.info("No reading history is available yet.")

    else:
        st.dataframe(
            df,
            use_container_width=True,
        )

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Reading History (CSV)",
            data=csv_data,
            file_name="twinplus_reading_history.csv",
            mime="text/csv",
        )

    # --------------------------------------------------
    # 9. HOSPITAL CONSENT AND ACCESS MANAGEMENT
    # --------------------------------------------------
    st.header("Hospital Access and Consent")

    try:
        consents = get_patient_consents(patient_code)

        if consents:
            consent_df = pd.DataFrame(consents)
            st.dataframe(
                consent_df,
                use_container_width=True,
            )

            hospital_options = {
                (
                    f"{hospital['hospital_name']} "
                    f"(ID: {hospital['hospital_id']})"
                ): hospital["hospital_id"]
                for hospital in consents
            }

            selected_hospital_label = st.selectbox(
                "Select Hospital",
                options=list(hospital_options.keys()),
                key="consent_hospital_select",
            )

            selected_hospital_id = hospital_options[
                selected_hospital_label
            ]

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "Grant Hospital Access",
                    key="grant_hospital_access",
                ):
                    try:
                        message = grant_hospital_access(
                            patient_code,
                            selected_hospital_id,
                            user_id,
                        )
                        st.success(message)
                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"Unable to grant access: {error}"
                        )

            with col2:
                if st.button(
                    "Revoke Hospital Access",
                    key="revoke_hospital_access",
                ):
                    try:
                        message = revoke_hospital_access(
                            patient_code,
                            selected_hospital_id,
                            user_id,
                        )
                        st.info(message)
                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"Unable to revoke access: {error}"
                        )

        else:
            st.info("No hospitals are currently listed.")

    except Exception as error:
        st.error(
            f"Unable to load hospital consent information: {error}"
        )

    st.subheader("Consent Change History")

    try:
        access_history = get_patient_access_history(
            patient_code,
            user_id,
        )

        if access_history:
            history_df = pd.DataFrame(access_history)

            history_df = history_df.rename(
                columns={
                    "hospital_name": "Hospital",
                    "action": "Action",
                    "created_at": "Date and Time",
                    "audit_id": "Record ID",
                }
            )

            st.dataframe(
                history_df,
                use_container_width=True,
            )

        else:
            st.info("No consent changes have been recorded.")

    except Exception as error:
        st.warning(
            f"Unable to load consent history: {error}"
        )

    # --------------------------------------------------
    # 10. EMAIL ALERT HISTORY
    # --------------------------------------------------
    st.header("Email Alert History")

    st.caption(
        "View alert records and delivery statuses for your account."
    )

    try:
        alert_history = get_alert_history(
            patient_code,
            user_id,
        )

        if alert_history:
            alert_df = pd.DataFrame(alert_history)

            st.dataframe(
                alert_df,
                use_container_width=True,
            )

            alert_csv = alert_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Alert History (CSV)",
                data=alert_csv,
                file_name="twinplus_alert_history.csv",
                mime="text/csv",
                key="download_alert_history",
            )

        else:
            st.info(
                "No email alerts have been recorded yet. "
                "Alert history will appear here when alerts "
                "are processed."
            )

    except Exception as error:
        st.warning(
            f"Unable to load email alert history: {error}"
        )

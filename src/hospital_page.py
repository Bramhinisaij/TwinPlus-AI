
import pandas as pd
import plotly.express as px
import streamlit as st

from src.hospital_service import (
    get_accessible_patients,
    get_authorized_patient_readings,
)
from src.anomaly_detection import detect_anomalies
from src.health_risk import assess_health_risk
from src.validation import validate_health_data
from src.reliability import assess_reliability
from src.data_quality import assess_data_quality


def show_hospital_page():
    staff = st.session_state.get("patient")

    if not staff or staff.get("role") != "hospital_staff":
        st.error("Please log in with a hospital staff account.")
        return

    st.title("Hospital Digital Twin Dashboard")
    st.caption(f"Hospital: {staff['hospital_name']}")
    st.write(f"Welcome, {staff['full_name']}.")

    try:
        patients = get_accessible_patients(staff["user_id"])

        st.subheader("Hospital Overview")
        st.metric("Patients with Granted Access", len(patients))

        if not patients:
            st.info("No patients have granted access to your hospital yet.")
            return

        options = {
            f"{p['full_name']} ({p['patient_code']})": p
            for p in patients
        }

        selected_label = st.selectbox(
            "Select an authorized patient",
            list(options.keys()),
        )
        selected_patient = options[selected_label]

        st.write(f"**Patient:** {selected_patient['full_name']}")
        st.write(f"**Patient code:** {selected_patient['patient_code']}")

        readings = get_authorized_patient_readings(
            staff["user_id"],
            selected_patient["patient_id"],
        )

        if not readings:
            st.info("No health readings are available for this patient.")
            return

        df = pd.DataFrame(readings)
        df["recorded_at"] = pd.to_datetime(
            df["recorded_at"], errors="coerce"
        )
        df = df.sort_values("recorded_at")

        st.divider()
        st.subheader("Latest Health Readings")

        latest = df.iloc[-1]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Heart Rate",
            f"{latest['heart_rate']}"
            if pd.notna(latest["heart_rate"]) else "N/A",
        )
        col2.metric(
            "Temperature",
            f"{latest['temperature']} °C"
            if pd.notna(latest["temperature"]) else "N/A",
        )
        col3.metric(
            "Oxygen Level",
            f"{latest['oxygen_level']}%"
            if pd.notna(latest["oxygen_level"]) else "N/A",
        )

        st.caption(
            "Recorded readings are for demonstration and do not "
            "provide a medical diagnosis."
        )

        # New feature: demonstration health-risk indicator.
        st.divider()
        st.subheader("AI-Assisted Health Risk Indicator")

        risk_result = assess_health_risk(latest)

        if risk_result["status"] == "Within demonstration ranges":
            st.success(risk_result["status"])
        elif risk_result["status"] == "Flag for review":
            st.warning(risk_result["status"])
        else:
            st.error(risk_result["status"])

        st.write(risk_result["message"])
        st.caption(
            "This is a rule-based demonstration, not a trained AI model "
            "or a clinically validated risk score. Do not use it to "
            "diagnose, treat, or rule out a health problem."
        )

        st.divider()
        st.subheader("Health Trend Dashboard")

        chart_data = df.dropna(subset=["recorded_at"])

        if chart_data.empty:
            st.info("No valid timestamps are available for the charts.")
        else:
            heart_chart = px.line(
                chart_data,
                x="recorded_at",
                y="heart_rate",
                markers=True,
                title="Heart Rate Trend",
                labels={
                    "recorded_at": "Recorded Time",
                    "heart_rate": "Heart Rate",
                },
            )
            st.plotly_chart(heart_chart, use_container_width=True)

            temperature_chart = px.line(
                chart_data,
                x="recorded_at",
                y="temperature",
                markers=True,
                title="Temperature Trend",
                labels={
                    "recorded_at": "Recorded Time",
                    "temperature": "Temperature (°C)",
                },
            )
            st.plotly_chart(
                temperature_chart, use_container_width=True
            )

            oxygen_chart = px.line(
                chart_data,
                x="recorded_at",
                y="oxygen_level",
                markers=True,
                title="Oxygen-Level Trend",
                labels={
                    "recorded_at": "Recorded Time",
                    "oxygen_level": "Oxygen Level (%)",
                },
            )
            st.plotly_chart(oxygen_chart, use_container_width=True)

        st.divider()
        st.subheader("Anomaly Detection")

        anomaly_data = detect_anomalies(df)

        if anomaly_data.empty:
            st.success(
                "No readings were flagged by the demonstration detector."
            )
        else:
            st.dataframe(
                anomaly_data,
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Flags use demonstration ranges and are not diagnoses."
            )

        st.divider()
        st.subheader("Data Quality and Reliability")

        quality = assess_data_quality(df)

        validation_data = df.copy()
        validation_data["patient_id"] = validation_data["patient_code"]
        validation = validate_health_data(validation_data)

        reliability_data = df.copy()
        reliability_data["timestamp"] = reliability_data["recorded_at"]
        reliability = assess_reliability(reliability_data)

        q1, q2, q3 = st.columns(3)
        q1.metric("Data Quality Score", f"{quality['quality_score']}%")
        q2.metric("Validation Status", validation["status"])
        q3.metric("Reliability Status", reliability["status"])

        with st.expander("View check details"):
            st.write("**Data Quality**")
            st.write(f"Status: {quality['status']}")
            st.write(f"Missing cells: {quality['missing_cells']}")
            st.write(f"Duplicate rows: {quality['duplicate_rows']}")

            st.write("**Validation**")
            st.write(
                "Invalid heart-rate entries: "
                f"{validation['invalid_heart_rate']}"
            )

            if validation["missing_required_columns"]:
                st.write(
                    "Missing required columns: "
                    f"{validation['missing_required_columns']}"
                )

            st.write("**Reliability**")
            st.write(f"Missing readings: {reliability['missing_readings']}")
            st.write(f"Delayed readings: {reliability['delayed_readings']}")

        st.divider()
        st.subheader("Health Reading History")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as error:
        st.error(f"Could not load the hospital dashboard: {error}")

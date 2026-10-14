
import streamlit as st
import pandas as pd

from src.pipeline import run_pipeline


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TwinPlus AI | Digital Twin",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f 0%, #0b1729 55%, #101c32 100%);
    color: #e5f0ff;
}
[data-testid="stSidebar"] {
    background: #091323;
    border-right: 1px solid #1b3855;
}
[data-testid="stSidebar"] * {
    color: #d8e8ff;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #e8f4ff !important;
}
p, label {
    color: #a9bdd5;
}
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #10243b, #0d1b2e);
    border: 1px solid #214765;
    border-radius: 14px;
    padding: 18px;
}
div[data-testid="stMetricLabel"] {
    color: #9db9d5;
}
div[data-testid="stMetricValue"] {
    color: #4de2ff;
}
div.stButton > button {
    background: linear-gradient(90deg, #087fce, #06b6d4);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    padding: 0.65rem 1rem;
    width: 100%;
}
div.stButton > button:hover {
    border: 1px solid #65eaff;
    color: white;
}
.panel {
    background: #0e1d30;
    border: 1px solid #203d59;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}
.small-label {
    color: #89a8c8;
    font-size: 13px;
}
.status-good {
    color: #42e8b4;
    font-weight: bold;
}
.status-warning {
    color: #ffc66d;
    font-weight: bold;
}
hr {
    border-color: #203d59;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("# 🔷 TwinPlus AI")
    st.caption("HEALTHCARE DIGITAL TWIN")
    st.divider()

    st.markdown("### Navigation")
    section = st.radio(
        "Choose section",
        [
            "Overview",
            "Patient Readings",
            "Data Reliability",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### Simulation Settings")

    patient_count = st.slider(
        "Number of sample patients",
        min_value=5,
        max_value=20,
        value=10,
    )

    refresh = st.button("⟳ Run Analysis")

    st.divider()
    st.caption("TwinPlus AI · Research Prototype")
    st.caption("Simulated data only — not for medical decisions.")


# ---------------- RUN PIPELINE ----------------
if refresh or "twinplus_result" not in st.session_state:
    st.session_state["twinplus_result"] = run_pipeline(patient_count)

result = st.session_state["twinplus_result"]

# Update when patient count changes
if len(result["data"]) != patient_count:
    st.session_state["twinplus_result"] = run_pipeline(patient_count)
    result = st.session_state["twinplus_result"]

data = result["data"]
quality = result["quality"]
validation = result["validation"]
reliability = result["reliability"]


# ---------------- HEADER ----------------
st.markdown(
    "<p style='color:#4de2ff; letter-spacing:3px; "
    "font-size:12px;'>AI-POWERED HEALTH MONITORING</p>",
    unsafe_allow_html=True,
)
st.title("Digital Twin Control Center")
st.write(
    "Monitor simulated patient readings, data quality, "
    "and incoming data reliability from one workspace."
)

st.markdown("---")


# ---------------- STATUS CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Patients Monitored", len(data))
col2.metric("Data Quality", f'{quality["quality_score"]}%')
col3.metric("Missing Readings", reliability["missing_readings"])
col4.metric("Delayed Readings", reliability["delayed_readings"])

st.write("")

# ---------------- OVERVIEW ----------------
if section == "Overview":

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("### 〽️ Heart Rate Monitor")
        heart_chart = data.set_index("patient_id")[["heart_rate"]]
        st.line_chart(
            heart_chart,
            color="#36cfff",
            height=280,
        )

        st.markdown("### 🫧 Oxygen Level Monitor")
        oxygen_chart = data.set_index("patient_id")[["oxygen_level"]]
        st.bar_chart(
            oxygen_chart,
            color="#19d3b0",
            height=230,
        )

    with right:
        st.markdown("### ◈ System Health")

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">DATA VALIDATION</div>
                <h3>{validation["status"]}</h3>
                <div class="small-label">
                    Basic required-field and heart-rate checks
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">DATA QUALITY</div>
                <h3>{quality["status"]}</h3>
                <div class="small-label">
                    Missing cells: {quality["missing_cells"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">READING RELIABILITY</div>
                <h3>{reliability["status"]}</h3>
                <div class="small-label">
                    Delayed readings use a 10-minute prototype threshold
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🌡️ Temperature")
        temp_chart = data.set_index("patient_id")[["temperature"]]
        st.line_chart(
            temp_chart,
            color="#ffb454",
            height=200,
        )


# ---------------- PATIENT READINGS ----------------
elif section == "Patient Readings":

    st.markdown("### Patient Reading Explorer")
    st.write("Browse the sample readings generated by the simulator.")

    search_id = st.text_input(
        "Search patient ID",
        placeholder="Example: P001",
    )

    filtered_data = data.copy()

    if search_id.strip():
        filtered_data = filtered_data[
            filtered_data["patient_id"].str.contains(
                search_id.strip(),
                case=False,
                na=False,
            )
        ]

    st.dataframe(
        filtered_data,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "All records shown here are simulated and are not real patient records."
    )


# ---------------- DATA RELIABILITY ----------------
elif section == "Data Reliability":

    st.markdown("### Reliability & Validation Center")

    a, b = st.columns(2)

    with a:
        st.markdown("#### Data Quality")
        st.metric("Quality Score", f'{quality["quality_score"]}%')
        st.metric("Missing Cells", quality["missing_cells"])
        st.metric("Duplicate Rows", quality.get("duplicate_rows", 0))
        st.write("Quality status:", quality["status"])

    with b:
        st.markdown("#### Reliability")
        st.metric("Missing Readings", reliability["missing_readings"])
        st.metric("Delayed Readings", reliability["delayed_readings"])
        st.write("Reliability status:", reliability["status"])

        st.markdown("#### Validation")
        st.write("Validation status:", validation["status"])
        st.write(
            "Missing required columns:",
            validation.get("missing_required_columns", []),
        )
        st.write(
            "Invalid heart-rate values:",
            validation.get("invalid_heart_rate", 0),
        )

    st.info(
        "This is a research prototype. The delay threshold and data checks "
        "are software demonstration rules, not clinical standards."
    )


# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(
    "TwinPlus AI | Reliability-Aware Healthcare Digital Twin | "
    "Research Prototype — simulated data only"
)

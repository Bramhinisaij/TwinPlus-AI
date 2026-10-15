 TwinPlus AI – Healthcare Digital Twin

## Overview

TwinPlus AI is a healthcare digital twin application designed to help patients and hospital staff monitor health readings, review health trends, identify unusual readings, and assess data reliability through a centralized digital platform.

The project combines Python, Streamlit, and MySQL to demonstrate how healthcare data can be collected, validated, analyzed, and presented through interactive dashboards.

**Project Type:** Healthcare Technology | AI-Assisted Monitoring | Digital Health

## Key Features

- **Patient Portal:** Patient registration, login, and health reading management.
- **Hospital Staff Portal:** Dedicated access for hospital staff.
- **Health Monitoring:** Record and monitor heart rate, body temperature, and oxygen saturation.
- **Live Simulation:** Generate simulated health readings for demonstration purposes.
- **Health Risk Assessment:** Flag readings that may require further review.
- **Anomaly Detection:** Identify unusual patterns in health data.
- **Data Validation:** Validate incoming health readings.
- **Data Quality Assessment:** Evaluate completeness and quality of recorded data.
- **Reliability Assessment:** Assess the reliability of available health information.
- **Trend Visualization:** Display health metrics and historical readings using interactive charts.
- **Consent Management:** Allow patients to manage hospital access permissions.
- **Audit Logging:** Record selected application activities for accountability.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Database | MySQL |
| Data Processing | Pandas |
| Data Visualization | Plotly |
| Testing | Pytest |
| Development Environment | Visual Studio Code |

## Project Structure

```text
TwinPlus-AI/
├── app.py
├── patient_app.py
├── requirements.txt
├── src/
│   ├── account_setup.py
│   ├── alert_service.py
│   ├── anomaly_detection.py
│   ├── audit_service.py
│   ├── auth_service.py
│   ├── consent_service.py
│   ├── data_quality.py
│   ├── database.py
│   ├── health_risk.py
│   ├── hospital_page.py
│   ├── hospital_service.py
│   ├── live_monitor.py
│   ├── patient_page.py
│   ├── patient_service.py
│   ├── reading_service.py
│   ├── reliability.py
│   ├── simulator.py
│   └── validation.py
├── tests/
└── .gitignore
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Bramhinisaij/TwinPlus-AI.git
cd TwinPlus-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

- Install and start MySQL Server.
- Create the required project database and tables.
- Configure the database connection using environment variables or a secure secrets configuration.
- Ensure the application has the required database permissions.

Do not commit database passwords, private credentials, or real patient records to GitHub.

### 5. Run the Application

To start the patient portal:

```bash
streamlit run patient_app.py
```

To start the main application, if required by your setup:

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

`http://localhost:8501`

## Running Tests

Run the project tests from the root directory:

```bash
pytest
```

## Deployment

TwinPlus AI can be exposed for temporary demonstrations using a tunneling service such as ngrok.

For example, after starting Streamlit on port 8501, run:

```bash
ngrok http 8501
```

The service provides a public HTTPS URL that forwards requests to the local application.

**Note:** This is temporary access, not permanent cloud hosting. Your computer and application must remain running. For permanent deployment, host the Python application and database on suitable cloud infrastructure and configure credentials securely.

## Security and Privacy

- Do not publish real patient data or sensitive medical information.
- Keep database credentials and secret keys out of source control.
- Protect patient and hospital accounts with appropriate authentication.
- Restrict database access and use encrypted connections where supported.
- Use synthetic data for public demonstrations.

## Disclaimer

TwinPlus AI is an educational and research prototype. Its risk assessments, anomaly detection, and simulated readings are intended for demonstration purposes only. The application is not a substitute for professional medical advice, clinical diagnosis, or emergency medical care.

## Future Enhancements

- Machine learning models for personalized anomaly detection.
- Integration with wearable health monitoring devices.
- Secure hospital-to-hospital data exchange.
- Improved real-time alerts and notifications.
- Cloud deployment with stronger privacy and access controls.

## Repository

GitHub: https://github.com/Bramhinisaij/TwinPlus-AI

---

**TwinPlus AI — Connecting patient health data, reliability assessment, and digital healthcare monitoring.**

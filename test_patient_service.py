
from src.patient_service import register_patient
from werkzeug.security import generate_password_hash

try:
    result = register_patient(
        full_name="Sample Patient",
        email="sample.patient@example.com",
        password_hash=generate_password_hash("DemoPass!482")
    )

    print(result)

except Exception as error:
    print("Registration test failed:", error)

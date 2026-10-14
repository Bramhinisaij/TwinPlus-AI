
from src.database import get_hospitals

try:
    hospitals = get_hospitals()

    print("MySQL connection successful!")
    print("Hospitals found:")

    for hospital in hospitals:
        print(hospital)

except Exception as error:
    print("Connection failed.")
    print(error)

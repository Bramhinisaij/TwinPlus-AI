
from src.simulator import generate_health_data
from src.data_quality import assess_data_quality
from src.reliability import assess_reliability
from src.validation import validate_health_data


def run_pipeline(num_patients=10):
    """Generate health data and run all quality checks."""

    data = generate_health_data(num_patients)

    validation = validate_health_data(data)
    quality = assess_data_quality(data)
    reliability = assess_reliability(data)

    return {
        "data": data,
        "validation": validation,
        "quality": quality,
        "reliability": reliability,
    }

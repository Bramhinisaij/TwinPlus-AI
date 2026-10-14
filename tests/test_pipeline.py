
from src.pipeline import run_pipeline


def test_pipeline_runs_successfully():
    result = run_pipeline()

    assert len(result["data"]) == 10
    assert result["validation"]["status"] == "Passed"
    assert result["quality"]["quality_score"] == 100
    assert "reliability" in result


def test_pipeline_custom_patient_count():
    result = run_pipeline(5)

    assert len(result["data"]) == 5

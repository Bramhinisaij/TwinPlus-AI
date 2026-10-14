
from unittest.mock import patch

from src.alert_service import process_reading_alerts


def test_reading_without_review_does_not_create_alert():
    with patch(
        "src.alert_service._get_reading",
        return_value={
            "reading_id": 10,
            "patient_id": 1,
            "patient_email": "patient@example.com",
        },
    ), patch(
        "src.alert_service.assess_health_risk",
        return_value={
            "status": "Within demonstration ranges",
            "review_required": False,
        },
    ):
        result = process_reading_alerts(
            "TEST001", 1, 10, test_mode=True
        )

    assert result["alerts"] == []


def test_alert_history_returns_patient_records_only():
    from src.alert_service import get_alert_history

    with patch(
        "src.alert_service.get_connection"
    ) as mock_connection:
        connection = mock_connection.return_value
        cursor = connection.cursor.return_value
        cursor.fetchall.return_value = [
            {
                "alert_id": 1,
                "reading_id": 10,
                "delivery_status": "test_mode",
            }
        ]

        result = get_alert_history("TEST001", 1)

        assert len(result) == 1
        assert result[0]["alert_id"] == 1

        cursor.execute.assert_called_once()
        assert "p.patient_code = %s" in cursor.execute.call_args[0][0]


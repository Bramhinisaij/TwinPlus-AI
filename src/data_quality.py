import pandas as pd


def assess_data_quality(data: pd.DataFrame) -> dict:
    """Assess completeness and detect duplicate health records."""

    if data.empty:
        return {
            "quality_score": 0.0,
            "missing_cells": 0,
            "total_cells": 0,
            "duplicate_rows": 0,
            "status": "No data available",
        }

    # Count total and missing cells
    total_cells = data.size
    missing_cells = int(data.isna().sum().sum())

    # Calculate completeness score
    completeness = 1 - (missing_cells / total_cells)
    quality_score = round(completeness * 100, 2)

    # Count completely duplicated rows
    duplicate_rows = int(data.duplicated().sum())

    # Determine data quality status
    if quality_score < 75:
        status = "Poor"
    elif quality_score < 95 or duplicate_rows > 0:
        status = "Check data"
    else:
        status = "Good"

    return {
        "quality_score": quality_score,
        "missing_cells": missing_cells,
        "total_cells": total_cells,
        "duplicate_rows": duplicate_rows,
        "status": status,
    }
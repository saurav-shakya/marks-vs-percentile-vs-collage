import pandas as pd
import numpy as np
from ai_utils import analyze_percentile

def calculate_percentile(marks, historical_data):
    """Calculate estimated percentile based on historical data"""
    try:
        marks = float(marks)
        historical_marks = historical_data['marks'].values

        # Count students with marks less than the given marks
        students_below = np.sum(historical_marks < marks)
        total_students = len(historical_marks)

        # Calculate percentile using the standardized formula
        if total_students > 0:
            # The standard percentile formula: P = (n_below / N) * 100
            # where n_below is number of observations below the value
            # and N is total number of observations
            percentile = (students_below / total_students) * 100

            # Cap at 99.99 percentile
            percentile = min(99.99, max(0, percentile))
            return round(percentile, 2)

        return None

    except Exception as e:
        print(f"Error calculating percentile: {e}")
        return None

def suggest_colleges(percentile, category, college_data):
    """Suggest colleges based on percentile and category"""
    try:
        category = category.lower()
        cutoff_col = f'cutoff_{category}'

        # Filter colleges where student's percentile is above cutoff
        eligible_colleges = college_data[
            college_data[cutoff_col] <= percentile
        ].copy()

        # Sort by cutoff in descending order
        eligible_colleges = eligible_colleges.sort_values(
            by=cutoff_col, 
            ascending=False
        )

        # Select relevant columns for display
        return eligible_colleges[['college_name', 'branch', cutoff_col, 'city']]
    except Exception as e:
        print(f"Error suggesting colleges: {e}")
        return pd.DataFrame()
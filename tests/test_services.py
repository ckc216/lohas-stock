import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta
from services import LohasService

@pytest.fixture
def sample_stock_data() -> pd.DataFrame:
    """Creates a sample DataFrame for testing."""
    dates = pd.to_datetime([datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)])
    data = {
        'date': dates,
        'close': np.linspace(100, 150, 100) + np.random.normal(0, 5, 100)
    }
    return pd.DataFrame(data)

def test_calculate_five_lines_structure_and_types(sample_stock_data):
    """
    Tests the output structure and data types of calculate_five_lines.
    """
    prepared_data = LohasService.prepare_data(sample_stock_data)
    result = LohasService.calculate_five_lines(prepared_data)

    # 1. Check if the result is a dictionary
    assert isinstance(result, dict)

    # 2. Check for the presence of essential keys
    expected_keys = ['data', 'std', 'z69', 'z95', 'lines']
    for key in expected_keys:
        assert key in result

    # 3. Check the 'lines' dictionary for its keys
    expected_line_keys = ['+2SD', '+1SD', '-1SD', '-2SD', 'Trend']
    assert isinstance(result['lines'], dict)
    for key in expected_line_keys:
        assert key in result['lines']

    # 4. Check if the line values are pandas Series
    for key in expected_line_keys:
        assert isinstance(result['lines'][key], pd.Series)

    # 5. Check if the data length is consistent
    assert len(result['lines']['Trend']) == len(prepared_data)

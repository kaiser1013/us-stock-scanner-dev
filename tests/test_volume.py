from datetime import datetime

import pandas as pd
from zoneinfo import ZoneInfo

from indicator import (
    select_completed_volume_index,
)

def create_sample_volume_df():
    """
    Create 40 business-day sample volume history.
    """
    
    dates = pd.date_range(
        "2026-01-01",
        periods=40,
        freq="B",
    )
    
    return pd.DataFrame(
        {
            "Volume": range(40)
        },
        index=dates,
    )
    
def test_before_cutoff_uses_previous_session():
    """
    Before 16:15 NY time the scanner
    should use the previous completed session.
    """
    
    df = create_sample_volume_df()
    
    latest_day = df.index[-1]
    
    now = datetime(
        latest_day.year,
        latest_day.month,
        latest_day.day,
        15,
        0,
        tzinfo=ZoneInfo(
            "America/New_York"
        ),
    )
    
    position, source = (
        select_completed_volume_index(
            df,
            now=now,
        )
    )
    
    assert position == -2
    
    assert (
        source
        == "Previous completed session"
    )
    
    
    
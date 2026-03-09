import pandas as pd
from pathlib import Path

def load_historical_data(follower_name: str) -> pd.DataFrame:
    """
    Load the historical 100-day data for a given follower.
    follower_name is exactly the name used in the data sheet, e.g. 'Mk1', 'Mk2', etc.
    """
    # Assuming data.xlsx is in the COMP34612_Student directory
    data_path = Path("COMP34612_Student/data.xlsx")
    
    # If not running from the root of the project, try going up a directory
    if not data_path.exists():
        data_path = Path("../COMP34612_Student/data.xlsx")
        
    try:
        sheet_name = f"Follower_{follower_name}"
        df = pd.read_excel(data_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        # Fallback to empty if it's MK4/5/6 and no data exists, though the coursework 
        # says 100 days of data is available for each... wait, MK4/5/6 don't have sheets
        # in the initial data.xlsx. They are hidden. We will return an empty dataframe for them.
        return pd.DataFrame()

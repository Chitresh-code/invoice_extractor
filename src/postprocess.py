from src.logger import setup_logger  # Import the logger
import pandas as pd  # Import Pandas for DataFrame creation
from typing import Optional, Dict  # Import types for type hinting
from io import StringIO  # Import StringIO
import json  # Import json module
import os  # Import os module

logger = setup_logger(__name__)  # Set up the logger

def create_dataframe(image_dict: Dict[str, Optional[str]]) -> Optional[pd.DataFrame]:
    """Creates a Pandas DataFrame from the JSON data in the image_dict."""
    json_data = []  # Initialize an empty list to hold JSON data
    for key, value in image_dict.items():
        if value != 'None':  # Check if value is not None
            try:
                # Convert the JSON string to a Python object (list of dictionaries)
                data = json.loads(value)
                json_data.extend(data)  # Extend the list with the new data
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON for key {key}: {e}")  # Log JSON decoding errors
                continue

    if json_data:
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(json_data)
        logger.info("DataFrame created successfully.")
        return df
    else:
        logger.warning("No valid JSON data found to create DataFrame.")
        return None

def save_dataframe_to_excel(df: pd.DataFrame, file_path: str) -> None:
    """Saves the given DataFrame to an Excel file."""
    try:
        with pd.ExcelWriter(file_path) as writer:
            df.to_excel(writer, sheet_name='Extracted Data', index=False)  # Write DataFrame to a sheet
        logger.info(f"DataFrame successfully saved to {file_path}.")  # Log success message
        return True
    except Exception as e:
        logger.error(f"Error saving DataFrame to Excel: {e}")  # Log the error
        return False
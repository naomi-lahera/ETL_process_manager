import pandas as pd

def extract_csv(file_path):
    """Read a tab-separated file into a DataFrame."""
    return pd.read_csv(file_path, delimiter='\t')

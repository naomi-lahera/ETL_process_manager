from tqdm import tqdm
from src.process.df_columns import dfColumns
from src.process.transform.llm import summarize

def row_summary(text, provider):
    try:
        return summarize(text, provider)
    except Exception as e:
        print(f"Summary failed: {e}")
        return None

def summary(data, provider=None):
    data[dfColumns.summary.value] = [
        row_summary(text, provider)
        for text in tqdm(data[dfColumns.content.value], desc="Summary")
    ]
    return data

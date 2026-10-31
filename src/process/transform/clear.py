import pandas as pd
from src.process.transform.nlp import nlp
from src.process.df_columns import dfColumns

def extract_entities(data):
  docs = nlp.pipe(data[dfColumns.content.value], batch_size=50)
  return [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]

# Rules: a row is dropped if its date is missing or not a valid date, or if its content is empty.
# A missing author is not an error, it becomes "anonymous".
def keep_valid_rows(data):
  dates = pd.to_datetime(data[dfColumns.fecha.value], errors="coerce")
  content = data[dfColumns.content.value].fillna("").astype(str).str.strip()
  data = data[dates.notna() & (content != "")].copy()
  author = data[dfColumns.author.value].str.strip()
  data[dfColumns.author.value] = author.fillna("anonymous").replace("", "anonymous")
  return data

def clear(data):
  data = keep_valid_rows(data)
  data[dfColumns.ne.value] = extract_entities(data)
  return data

import pandas as pd
from src.process.transform.nlp import nlp
from src.process.df_columns import dfColumns

def extract_entities(data):
  """Return the (text, label) entities found in each row's content."""
  docs = nlp.pipe(data[dfColumns.content.value], batch_size=50)
  return [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]

def keep_valid_rows(data):
  """Drop rows with an invalid date or empty content; a missing author becomes "anonymous"."""
  dates = pd.to_datetime(data[dfColumns.fecha.value], errors="coerce")
  content = data[dfColumns.content.value].fillna("").astype(str).str.strip()
  data = data[dates.notna() & (content != "")].copy()
  author = data[dfColumns.author.value].str.strip()
  data[dfColumns.author.value] = author.fillna("anonymous").replace("", "anonymous")
  return data

def clear(data):
  """Drop invalid rows and add the named entities."""
  data = keep_valid_rows(data)
  data[dfColumns.ne.value] = extract_entities(data)
  return data

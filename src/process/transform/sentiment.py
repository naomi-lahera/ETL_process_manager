from tqdm import tqdm
from src.process.df_columns import dfColumns
from src.process.transform.llm import entity_sentiments

ENTITY_LABELS = {"PERSON", "ORG", "GPE", "LOC", "FAC", "EVENT", "PRODUCT"}

def row_sentiments(text, entities, provider):
    names = sorted({name for name, label in entities if label in ENTITY_LABELS})
    if not names:
        return []
    try:
        return [o.model_dump() for o in entity_sentiments(text, names, provider)]
    except Exception as e:
        print(f"Sentiment failed: {e}")
        return []

def sentiment(data, provider=None):
    rows = zip(data[dfColumns.content.value], data[dfColumns.ne.value])
    data[dfColumns.sentiments.value] = [
        row_sentiments(text, entities, provider)
        for text, entities in tqdm(rows, total=len(data), desc="Sentiment")
    ]
    return data

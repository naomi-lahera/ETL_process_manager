from enum import Enum

class dfColumns(Enum):
    fecha = "date"
    source = "source"
    author = "author"
    content = "content"
    ne = "named_entities"
    sentiments = "entity_sentiments"
    summary = "summary"
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from src.db.models import Author, News, Source, EntitySentiment
from src.process.df_columns import dfColumns

def get_id(session, model, name):
    return session.scalar(
        insert(model).values(name=name)
        .on_conflict_do_update(index_elements=["name"], set_={"name": name})
        .returning(model.id)
    )

def store(data, engine):
    with Session(engine) as session:
        for row in data.to_dict("records"):
            session.add(News(
                date=pd.to_datetime(row[dfColumns.fecha.value]).date(),
                content=row[dfColumns.content.value],
                summary=row[dfColumns.summary.value],
                named_entities=row[dfColumns.ne.value],
                author_id=get_id(session, Author, row[dfColumns.author.value]),
                source_id=get_id(session, Source, row[dfColumns.source.value]),
                sentiments=[EntitySentiment(**s) for s in row[dfColumns.sentiments.value]],
            ))
        session.commit()

    return data

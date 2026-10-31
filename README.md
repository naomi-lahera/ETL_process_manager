# ETL_process_manager

ETL process manager that extracts named entities from news articles.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_md
```

The sentiment step uses an LLM. Copy `.env.example` to `.env` and set `GEMINI_API_KEY` and/or `NVIDIA_API_KEY`. Only the providers with a key are used.

## Usage

```bash
./run.sh path/to/file.tsv [gemini|nvidia]
```

The optional second argument is the LLM provider to try first (`nvidia` by default). If it fails, the other available one is used.

Wrap the path in quotes if it contains spaces.

## Process

### Extract
Reads a tab-separated file with the columns:
- date
- source
- author
- content

### Transform
- Row validation: rows that break a rule are dropped (see below); an empty author becomes `anonymous`
- Named entity extraction (spaCy) on the original text. Each entity is stored as `(text, label)`, e.g. `('Keir Starmer', 'PERSON')`
- LLM summary: 2-sentence summary of the article
- LLM sentiment per entity: whether the article portrays each entity positively, neutrally or negatively, with a short reason

#### Validation rules

A row is dropped when:

| Rule |
|---|
| The date is missing or is not a valid date |
| The content is empty or only whitespace |

A missing author is not an error: it becomes `anonymous`. The rules live in `keep_valid_rows` in `src/process/transform/clear.py`.

The dropped rows are not stored in the database.

### Load
Stores everything in PostgreSQL (SQLAlchemy ORM) in four tables: `news`, `authors`, `sources` and `entity_sentiments`. Authors and sources are deduplicated, and the named entities are kept as JSONB so they can be queried.

## LLM integration

The LLM works on the original article text:

- **Summary:** short description of each article.
- **Sentiment per entity:** it receives the entities extracted by spaCy and also merges variants of the same entity (`Starmer` and `Keir Starmer` become one), so the stored sentiments are not duplicated.

Two providers are supported, NVIDIA (`mistralai/mistral-large-4-1t-a52b`, default) and Gemini. Only the providers with a key in `.env` are used, the one passed to `run.sh` goes first, and if it fails the other one is used as a fallback. A failed call never stops the process: that article is stored without summary or sentiments.

## Examples

### Dropped rows

`data_example/anomalies.tsv` has one correct news and one with an invalid date (`not available`). Run it with `./run.sh data_example/anomalies.tsv`: only the correct news goes on through the pipeline and is stored.

### Processed news

Two articles from `data_example/example.tsv`, run with `./run.sh data_example/example.tsv`. Output of the Transform steps for each one.

### Example 1: The Guardian, 2026-10-01

**Input** (author: Emily Carter)
> British Prime Minister Keir Starmer met with French President Emmanuel Macron in Paris on Monday to discuss a new border agreement between the United Kingdom and France. The talks, which lasted nearly three hours, also covered defense cooperation within NATO. Officials from both governments said a joint statement would be released later this week. Starmer told reporters that the meeting was constructive and that both countries were committed to reducing illegal crossings in the English Channel.

**Named entities** (spaCy)
```
('British', 'NORP'), ('Keir Starmer', 'PERSON'), ('French', 'NORP'), ('Emmanuel Macron', 'PERSON'), ('Paris', 'GPE'), ('Monday', 'DATE'), ('the United Kingdom', 'GPE'), ('France', 'GPE'), ('nearly three hours', 'TIME'), ('NATO', 'ORG'), ('later this week', 'DATE'), ('Starmer', 'PERSON'), ('the English Channel', 'ORG')
```

**Summary** (LLM)
> British Prime Minister Keir Starmer met with French President Emmanuel Macron in Paris on Monday to discuss a new border agreement and NATO defense cooperation. Starmer described the nearly three-hour meeting as constructive and stated that both countries are committed to reducing illegal crossings in the English Channel.

**Sentiment per entity** (LLM)

| Entity | Sentiment | Reason |
|---|---|---|
| Keir Starmer | positive | Described meeting as constructive and committed to solutions |
| Emmanuel Macron | neutral | Mentioned as meeting counterpart without evaluation |
| France | neutral | Referenced as party to border agreement |
| the United Kingdom | neutral | Referenced as party to border agreement |
| NATO | neutral | Mentioned as context for defense cooperation |
| Paris | neutral | Cited as meeting location |
| the English Channel | neutral | Referenced as location of crossings |

spaCy detected `Starmer` and `Keir Starmer` as two entities and the LLM merged them into one.

### Example 2: ESPN, 2026-10-04

**Input** (author: Michael Brooks)
> Lionel Messi scored two goals as Inter Miami defeated Orlando City 3-1 at Chase Stadium in Florida on Saturday night. The Argentine forward opened the scoring in the 12th minute and added a second from the penalty spot after halftime. Coach Javier Mascherano praised the team for its discipline and said the victory moves Inter Miami closer to the top of the Eastern Conference. The club will travel to Atlanta next weekend to face Atlanta United.

**Named entities** (spaCy)
```
('Lionel Messi', 'PERSON'), ('two', 'CARDINAL'), ('Inter Miami', 'LOC'), ('Orlando City', 'GPE'), ('3-1', 'CARDINAL'), ('Chase Stadium', 'FAC'), ('Florida', 'GPE'), ('Saturday night', 'TIME'), ('Argentine', 'NORP'), ('the 12th minute', 'TIME'), ('second', 'ORDINAL'), ('Javier Mascherano', 'PERSON'), ('Inter Miami', 'LOC'), ('the Eastern Conference', 'EVENT'), ('Atlanta', 'GPE'), ('next weekend', 'DATE'), ('Atlanta United', 'GPE')
```

**Summary** (LLM)
> Lionel Messi scored two goals to lead Inter Miami to a 3-1 victory over Orlando City at Chase Stadium, opening the scoring in the 12th minute and adding a penalty after halftime. Coach Javier Mascherano praised the team's discipline and said the win moves Inter Miami closer to the top of the Eastern Conference, with the club set to travel to Atlanta next weekend.

**Sentiment per entity** (LLM)

| Entity | Sentiment | Reason |
|---|---|---|
| Lionel Messi | positive | Scored two goals in 3-1 victory |
| Inter Miami | positive | Won match and moved closer to top |
| Orlando City | negative | Lost 3-1 to Inter Miami |
| Javier Mascherano | positive | Praised team discipline after win |
| Chase Stadium | neutral | Venue where match was played |
| Florida | neutral | Location of the match |
| Atlanta | neutral | Next destination for Inter Miami |
| Atlanta United | neutral | Upcoming opponent for Inter Miami |
| the Eastern Conference | neutral | Standings context mentioned for victory |

Only entities that are people, organizations, places, facilities, events or products are sent to the LLM; dates, times and numbers are skipped.

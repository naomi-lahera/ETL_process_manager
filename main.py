import sys
from functools import partial
from src.process.extract.csv import extract_csv
from src.process.transform.clear import clear
from src.process.transform.summary import summary
from src.process.transform.sentiment import sentiment
from src.db.database import get_engine, init_db
from src.process.store.news import store
from tqdm import tqdm

class Step:
    def __init__(self, func, name):
        self.func = func
        self.name = name

    def run(self, data):
        """Run the step on the data and return the result."""
        return self.func(data)

if __name__ == "__main__":
    file_path = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else None
    engine = get_engine()
    init_db(engine)

    process = [Step(extract_csv, 'Load'), Step(clear, 'Clear'), Step(partial(summary, provider=provider), 'Summary'), Step(partial(sentiment, provider=provider), 'Sentiment'), Step(partial(store, engine=engine), 'Store')]

    try:
        data = process[0].run(file_path)

        for step in tqdm(process[1:], desc="Processing iterations..."):
            print(f"\nRunning {step.name}")
            data = step.run(data)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        engine.dispose()

    print("✅ Processing complete.")

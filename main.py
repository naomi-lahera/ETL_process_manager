import sys
from src.process.extract.csv import extract_csv
from src.process.transform.clear import clear
from tqdm import tqdm

class Step:
    def __init__(self, func, name):
        self.func = func
        self.name = name

    def run(self, data):
        return self.func(data)

process = [Step(extract_csv, 'Load'), Step(clear, 'Clear')]

if __name__ == "__main__":
    file_path = sys.argv[1]
    data = process[0].run(file_path)
    
    for step in tqdm(process[1:], desc="Processing iterations..."):
        print(f"\nRunning {step.name}")
        data = step.run(data)

    print("✅ Processing complete.")
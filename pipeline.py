import subprocess
from datetime import datetime

def run_pipeline():
    print(f"\n{'='*40}")
    print(f"Pipeline run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print('='*40)

    print("\n[1/3] Running ingest.py...")
    subprocess.run(['python3', 'ingest.py'])

    print("\n[2/3] Running process.py...")
    subprocess.run(['python3', 'process.py'])

    print("\n[3/3] Running export.py...")
    subprocess.run(['python3', 'export.py'])

    print("\n✓ Pipeline complete!")
    print("Output: finance_dashboard.xlsx")

run_pipeline()
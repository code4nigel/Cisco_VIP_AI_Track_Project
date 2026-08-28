import sys
import os
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
from src.checker import run_deterministic_checks

def test_all_cases():
    df = pd.read_csv('data/cases.csv')
    detected_count = 0
    print(f"Testing {len(df)} cases against Deterministic Checker...\n")
    for idx, row in df.iterrows():
        result = run_deterministic_checks(
            show_output=str(row['show_outputs']),
            topology_note=str(row['topology_note']),
            symptom=str(row['symptom'])
        )
        if result['status'] == 'ERRORS_DETECTED':
            detected_count += 1
            finding = result['findings'][0]
            print(f"[{row['case_id']}] DETECTED: {finding['title']} | Expected: {row['expected_fault']}")
        else:
            print(f"[{row['case_id']}] MISSED: Expected {row['expected_fault']}")

    accuracy = (detected_count / len(df)) * 100
    print(f"\n==========================================")
    print(f"Total Detected: {detected_count}/{len(df)} ({accuracy:.1f}%)")
    print(f"==========================================")

if __name__ == '__main__':
    test_all_cases()

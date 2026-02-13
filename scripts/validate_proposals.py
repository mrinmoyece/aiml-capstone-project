
#!/usr/bin/env python3
import sys
import pandas as pd
from pathlib import Path

def main(week: int, runs='runs'):
    p = Path(runs) / f"week_{int(week):02d}" / "proposals.csv"
    df = pd.read_csv(p)
    errs = 0
    if df['function_id'].nunique() != 8:
        print("[ERROR] expected 8 unique function_id; got", df['function_id'].nunique()); errs += 1
    if 'x_concat' not in df.columns or df['x_concat'].isna().any():
        print("[ERROR] x_concat missing or NaN"); errs += 1
    if errs:
        sys.exit(2)
    print("[OK] proposals look valid.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: validate_proposals.py <week>"); sys.exit(2)
    main(int(sys.argv[1]))


#!/usr/bin/env python3
from __future__ import annotations
import sys, argparse
from pathlib import Path
import pandas as pd

ALLOWED = {"function_id","kappa_delta","tr_halfwidth","n_candidates_multiplier","note"}

def warn(m): print(f"[WARN] {m}")
def die(m): print(f"[ERROR] {m}", file=sys.stderr); sys.exit(2)
def ok(m): print(f"[OK] {m}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-N","--week", type=int, required=True)
    ap.add_argument("--runs", default="runs")
    args = ap.parse_args()
    csv = Path(args.runs) / f"week_{args.week:02d}" / "overrides.csv"
    if not csv.exists():
        die(f"Overrides not found: {csv}")
    df = pd.read_csv(csv)
    if df.empty:
        warn("CSV empty; no manual overrides will be applied."); ok("Validated"); return 0
    extra = set(df.columns) - ALLOWED
    if extra: warn(f"Unknown columns ignored: {sorted(extra)}")
    if "function_id" not in df.columns: die("Missing 'function_id' column.")
    fids = df["function_id"].dropna().astype(int)
    if fids.empty: warn("No function_id entries found.")
    if (fids<1).any() or (fids>8).any(): warn("function_id should be in [1,8].")
    if "tr_halfwidth" in df.columns:
        th = df["tr_halfwidth"].dropna().astype(float)
        if (th<=0).any() or (th>1.0).any(): warn("tr_halfwidth should be in (0,1].")
    if "kappa_delta" in df.columns:
        kd = df["kappa_delta"].dropna().astype(float)
        if (kd<-2).any() or (kd>2).any(): warn("kappa_delta outside recommended [-2,2].")
    if "n_candidates_multiplier" in df.columns:
        nm = df["n_candidates_multiplier"].dropna().astype(float)
        if (nm<0.5).any() or (nm>5.0).any(): warn("n_candidates_multiplier recommended [0.5,5.0].")
    ok("Overrides CSV validated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

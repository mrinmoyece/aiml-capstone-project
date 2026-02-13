
#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd, sys

ROOT = Path(".")
init_root = ROOT / "initial_data"

def check_initial_data():
    issues = []
    for fdir in sorted([p for p in init_root.iterdir() if p.is_dir() and p.name.startswith("function_")]):
        Xp, yp = fdir / "initial_inputs.npy", fdir / "initial_outputs.npy"
        if not Xp.exists() or not yp.exists():
            issues.append(f"[MISSING] {fdir} missing npy files"); continue
        try:
            X = np.load(Xp); y = np.load(yp).reshape(-1)
        except Exception as e:
            issues.append(f"[LOAD-ERR] {fdir}: {e}"); continue
        if len(X) != len(y): issues.append(f"[LEN] {fdir}: X={X.shape}, y={y.shape}")
        if np.any((X < 0.0) | (X > 1.0)): issues.append(f"[BOUNDS] {fdir}: x outside [0,1]")
        # duplicates
        try:
            uniq = np.unique(np.round(X, 8), axis=0)
            if len(uniq) < len(X): issues.append(f"[DUPLICATES] {fdir}: {len(X)-len(uniq)} duplicated rows (rounded 1e-8)")
        except Exception:
            pass
        if np.std(y) < 1e-12: issues.append(f"[CONST-Y] {fdir}: y appears constant/near-constant")
    return issues

def check_latest_week():
    runs = ROOT / "runs"
    weeks = sorted([p for p in runs.iterdir() if p.is_dir() and p.name.startswith("week_")])
    if not weeks: return []
    last = weeks[-1]
    issues = []
    csv = last / "proposals.csv"
    if not csv.exists(): return issues
    df = pd.read_csv(csv)
    if "function_id" not in df.columns: issues.append(f"[CSV] {csv} missing function_id")
    xcols = [c for c in df.columns if str(c).startswith("x")]
    if not xcols: issues.append(f"[CSV] {csv} missing x columns")
    for _, r in df.iterrows():
        xs = []
        for c in xcols:
            try: xs.append(float(r[c]))
            except: pass
        if xs and (min(xs) < 0.0 or max(xs) > 1.0):
            issues.append(f"[CSV-BOUNDS] {csv} row with x outside [0,1]")
    return issues

if __name__ == "__main__":
    issues = []
    issues += check_initial_data()
    issues += check_latest_week()
    if issues:
        print("Sanity Check: FOUND ISSUES")
        for s in issues: print(" -", s)
        sys.exit(2)
    else:
        print("Sanity Check: OK")

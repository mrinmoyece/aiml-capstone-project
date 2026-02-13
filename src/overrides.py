
from __future__ import annotations
from pathlib import Path
import pandas as pd

def week_dir(runs_base: Path, week: int) -> Path:
    wd = runs_base / f"week_{int(week):02d}"
    wd.mkdir(parents=True, exist_ok=True)
    return wd

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    # Accept either 'function_id' or 'function'
    if 'function' in df2.columns and 'function_id' not in df2.columns:
        df2['function_id'] = df2['function'].astype(str).str.replace(r'[^0-9]', '', regex=True).astype(int)
    if 'function_id' not in df2.columns:
        raise ValueError("overrides.csv must include 'function_id' or 'function'")
    # unify column names
    ren = {}
    for c in df2.columns:
        lc = str(c).strip().lower()
        if lc in {'kappa_delta','kappa','delta_kappa'}: ren[c] = 'kappa_delta'
        if lc in {'tr_halfwidth','trust_region','trust_region_halfwidth','tr'}: ren[c] = 'tr_halfwidth'
        if lc in {'n_candidates_multiplier','candidate_multiplier','n_mult','multiplier'}: ren[c] = 'n_candidates_multiplier'
    if ren: df2 = df2.rename(columns=ren)
    return df2

def load_overrides_csv(runs_base: Path, week: int) -> dict[int, dict]:
    wd = week_dir(runs_base, week)
    csv = wd / 'overrides.csv'
    if not csv.exists():
        return {}
    df = pd.read_csv(csv)
    if df.empty:
        return {}
    df = _normalize_cols(df)
    out = {}
    for _, r in df.iterrows():
        fid = int(r['function_id'])
        rec = {}
        if 'kappa_delta' in r and pd.notna(r['kappa_delta']):
            rec['kappa_delta'] = float(r['kappa_delta'])
        if 'tr_halfwidth' in r and pd.notna(r['tr_halfwidth']):
            rec['tr_halfwidth_override'] = float(r['tr_halfwidth'])
        if 'n_candidates_multiplier' in r and pd.notna(r['n_candidates_multiplier']):
            rec['n_candidates_multiplier'] = float(r['n_candidates_multiplier'])
        if rec:
            out[fid] = rec
    return out

def write_overrides_template(runs_base: Path, week: int, function_ids: list[int]) -> Path:
    wd = week_dir(runs_base, week)
    csv = wd / 'overrides.csv'
    if csv.exists():
        return csv
    df = pd.DataFrame({
        'function_id': function_ids,
        'kappa_delta': [None]*len(function_ids),
        'tr_halfwidth': [None]*len(function_ids),
        'n_candidates_multiplier': [None]*len(function_ids),
        'note': ['edit values (optional) and rerun proposal cell']*len(function_ids),
    })
    df.to_csv(csv, index=False)
    return csv

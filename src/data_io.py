from __future__ import annotations
from pathlib import Path
from datetime import datetime
import time, tempfile, shutil, os
import numpy as np, pandas as pd
from src.config import INITIAL_DATA_ROOT


def list_functions(root: Path = INITIAL_DATA_ROOT):
    return sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("function_")])


def load_xy(func_dir: Path):
    Xp, yp = func_dir / "initial_inputs.npy", func_dir / "initial_outputs.npy"
    X = np.load(Xp);
    y = np.load(yp).reshape(-1);
    return X, y


def backup_file(path: Path):
    bkp = path.with_suffix(path.suffix + f".bak.{int(time.time())}")
    shutil.copy2(path, bkp)


def atomic_save_npy(array: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent);
    os.close(fd)
    np.save(tmp, array);
    shutil.move(tmp + ".npy", str(path))


def write_csv_with_precision(df, csv_path: Path, decimals: int = 6) -> None:
    """
    Write DataFrame to CSV with fixed decimal precision for x columns.
    Skips x_concat column if it exists.
    """
    df_out = df.copy()

    # Get x columns but exclude x_concat
    x_cols = [c for c in df_out.columns if str(c).startswith("x") and c != "x_concat"]

    for col in x_cols:
        df_out[col] = df_out[col].map(lambda v: f"{float(v):.{decimals}f}")

    # Only create x_concat if it doesn't already exist
    if "x_concat" not in df_out.columns:
        df_out["x_concat"] = df_out[x_cols].apply(lambda r: "-".join(r.values.astype(str)), axis=1)

    df_out.to_csv(csv_path, index=False)


# === STATUS UPDATE PATCH ===
import datetime as dt
import re


def _row_function_id(row):
    if 'function_id' in row and not pd.isna(row['function_id']):
        return int(row['function_id'])
    if 'function' in row and isinstance(row['function'], str):
        m = re.search(r'(\d+)', row['function'])
        if m: return int(m.group(1))
    raise ValueError("proposals.csv must include function_id or function column.")


def _x_from_row(row, d):
    xs = []
    for j in range(1, d + 1):
        key = f"x{j}"
        if key not in row or pd.isna(row[key]):
            raise ValueError(f"Missing {key} in proposals.csv")
        xs.append(float(row[key]))
    return np.array(xs, dtype=float).reshape(1, -1)


def apply_week_csv(csv_dir: Path, initial_root: Path, dry_run: bool = False):
    """Apply proposals.csv (with returned y) into initial_*.npy AND update status column.

    Status values:
      - 'applied' (within [0,1])
      - 'applied_clipped' (values clipped to [0,1])
      - 'skipped_missing_y' (y empty/NaN)
      - 'skipped_invalid' (non-finite y or malformed row)

    Also sets 'applied_at' ISO timestamp.
    """
    csv_path = csv_dir / "proposals.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"proposals.csv not found in {csv_dir}")

    df = pd.read_csv(csv_path)

    # Ensure applied_at column exists and has correct dtype
    if 'applied_at' not in df.columns:
        df['applied_at'] = ''
    df['applied_at'] = df['applied_at'].astype(str)  # Explicitly set dtype to string

    changed = False

    for idx, row in df.iterrows():
        try:
            if 'y' not in df.columns or pd.isna(row['y']) or str(row['y']).strip() == '':
                df.at[idx, 'status'] = 'skipped_missing_y'
                continue

            y_val = float(row['y'])
            if not np.isfinite(y_val):
                df.at[idx, 'status'] = 'skipped_invalid'
                continue

            fid = _row_function_id(row)
            fdir = initial_root / f"function_{fid}"
            Xp = fdir / "initial_inputs.npy";
            yp = fdir / "initial_outputs.npy"

            if not Xp.exists() or not yp.exists():
                df.at[idx, 'status'] = 'skipped_invalid'
                continue

            X = np.load(Xp);
            y = np.load(yp)
            d = X.shape[1]

            x = _x_from_row(row, d)

            clipped = False
            if not (np.all(x >= 0) and np.all(x <= 1)):
                x = np.clip(x, 0.0, 1.0)
                clipped = True

            if not dry_run:
                (fdir / "backup").mkdir(exist_ok=True, parents=True)
                ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                np.save(fdir / "backup" / f"inputs_before_{ts}.npy", X)
                np.save(fdir / "backup" / f"outputs_before_{ts}.npy", y)
                np.save(Xp, np.vstack([X, x]))
                np.save(yp, np.concatenate([y, [y_val]]))

            # Update timestamp (now compatible with string dtype)
            df.at[idx, 'applied_at'] = dt.datetime.utcnow().isoformat()
            df.at[idx, 'status'] = 'applied_clipped' if clipped else 'applied'
            changed = True

        except Exception as e:
            df.at[idx, 'status'] = 'skipped_invalid'
            df.at[idx, 'error'] = str(e)

    if changed and not dry_run:
        backup = csv_path.with_name(f"proposals_backup.csv")
        try:
            if not backup.exists():
                shutil.copy2(csv_path, backup)
        except Exception:
            pass

        df.to_csv(csv_path, index=False)

    return int((df['status'] == 'applied').sum()), int((df['status'] == 'applied_clipped').sum())


# === X_CONCAT SAFE BUILDER ===
def build_x_concat(df: 'pd.DataFrame') -> 'pd.Series':
    """Return hyphen-joined x1..xD at 6dp per row; error if a required xj is missing."""
    if df is None or df.empty:
        return pd.Series([], dtype=str)

    xcols = sorted([c for c in df.columns if re.fullmatch(r"x\d+", str(c))], key=lambda c: int(str(c)[1:]))
    if not xcols:
        return pd.Series(["" for _ in range(len(df))], index=df.index, dtype=str)

    def _join(r):
        vals = []
        for c in xcols:
            if c in r and pd.notna(r[c]):
                vals.append(f"{float(r[c]):.6f}")
            else:
                # allow shorter dimensional functions by skipping nan columns
                continue
        return "-".join(vals)

    return df.apply(_join, axis=1)

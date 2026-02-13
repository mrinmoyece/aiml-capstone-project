import numpy as np
import pandas as pd
import json
import warnings
from pathlib import Path
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as Ck
from src.config import INITIAL_DATA_ROOT, RUNS_BASE
from src.data_io import list_functions, load_xy

# Suppress GP convergence warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn.gaussian_process')


def _fit_gp_diag(X, y):
    d = X.shape[1]
    # Wider bounds to prevent convergence warnings
    kernel = Ck(1.0, (1e-3, 1e3)) * RBF(
        length_scale=np.ones(d),
        length_scale_bounds=(1e-3, 50.0)  # Increased from (1e-2, 10.0)
    ) + WhiteKernel(
        noise_level=1e-5,
        noise_level_bounds=(1e-10, 1.0)  # Widened from (1e-8, 1e-1)
    )
    gp = GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        n_restarts_optimizer=3,  # Increased from 1
        random_state=0
    )
    gp.fit(X, y)
    return gp


def strategy_rule(fid, X, y, week: int):
    y = np.asarray(y).reshape(-1)
    win = y[-min(10, len(y)):]
    mean, std = float(np.mean(win)), float(np.std(win, ddof=1)) if len(win) >= 2 else 0.0
    y_last = float(y[-1])
    z = (y_last - mean) / (std if std > 1e-12 else 1.0)
    gp = _fit_gp_diag(X, y)
    i_best = int(np.argmax(y))
    sigma_best = float(gp.predict(X[i_best].reshape(1, -1), return_std=True)[1][0])

    decision = "balanced"
    kappa_delta = 0.0
    n_mult = 1.0
    tr_override = None
    notes = []

    if y_last >= (win.max() - 1e-12) and len(win) >= 3:
        decision = "exploit_local"
        kappa_delta = -0.4
        tr_override = 0.12
        notes.append("Latest y near local max.")

    if z < -1.5:
        decision = "increase_exploration"
        kappa_delta = max(kappa_delta, 0.3)
        n_mult = max(n_mult, 1.5)
        tr_override = None
        notes.append("Negative surprise (z<-1.5).")

    if sigma_best > 0.35:
        n_mult = max(n_mult, 1.5)
        kappa_delta = max(kappa_delta, 0.1)
        notes.append("High σ near incumbent.")

    return {
        "function_id": int(fid),
        "decision": decision,
        "kappa_delta": round(float(kappa_delta), 3),
        "n_candidates_multiplier": round(float(n_mult), 2),
        "tr_halfwidth_override": tr_override,
        "z_last": round(float(z), 3),
        "sigma_at_best": round(float(sigma_best), 3),
        "notes": "; ".join(notes)
    }


def run_strategy_scan(week: int, data_root: Path = INITIAL_DATA_ROOT, runs_root: Path = RUNS_BASE) -> pd.DataFrame:
    recs = []
    for fdir in list_functions(data_root):
        fid = int(fdir.name.split("_")[1])
        X, y = load_xy(fdir)
        recs.append(strategy_rule(fid, X, y, week))

    df = pd.DataFrame(recs).sort_values("function_id").reset_index(drop=True)
    week_dir = runs_root / f"week_{int(week):02d}"
    week_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(week_dir / "strategy_recommendations.csv", index=False)
    manual_overrides = load_overrides(week, runs_root)

    overrides = {}
    for _, r in df.iterrows():
        fid = int(r["function_id"])
        auto_override = {
            "kappa_delta": float(r["kappa_delta"]),
            "n_candidates_multiplier": float(r["n_candidates_multiplier"]),
            "tr_halfwidth_override": None if pd.isna(r["tr_halfwidth_override"]) else float(r["tr_halfwidth_override"])
        }

        if fid in manual_overrides:
            overrides[fid] = manual_overrides[fid]
        else:
            overrides[fid] = auto_override

    with open(week_dir / "strategy_overrides.json", "w", encoding="utf-8") as f:
        json.dump(overrides, f, indent=2)

    return df


def load_overrides(week: int, runs_root: Path = RUNS_BASE):
    csv_path = runs_root / f"week_{int(week):02d}" / "overrides.csv"

    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            overrides = {}
            for _, row in df.iterrows():
                fid = int(row['function_id'])
                override_dict = {}

                if 'kappa_delta' in row and pd.notna(row['kappa_delta']):
                    override_dict['kappa_delta'] = float(row['kappa_delta'])

                if 'n_candidates_multiplier' in row and pd.notna(row['n_candidates_multiplier']):
                    override_dict['n_candidates_multiplier'] = float(row['n_candidates_multiplier'])

                if 'tr_halfwidth_override' in row and pd.notna(row['tr_halfwidth_override']):
                    override_dict['tr_halfwidth_override'] = float(row['tr_halfwidth_override'])

                if override_dict:
                    overrides[fid] = override_dict

            return overrides
        except Exception as e:
            print(f"Warning: Failed to load overrides from {csv_path}: {e}")
            return {}

    json_path = runs_root / f"week_{int(week):02d}" / "strategy_overrides.json"
    if json_path.exists():
        try:
            with open(json_path, "r") as f:
                return {int(k): v for k, v in json.load(f).items()}
        except Exception as e:
            print(f"Warning: Failed to load overrides from {json_path}: {e}")

    return {}

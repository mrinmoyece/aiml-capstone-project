import numpy as np
import pandas as pd

from src.acquisition import kappa_schedule, tr_halfwidth, diversity_tiebreak, ensure_min_distance
from src.config import INITIAL_DATA_ROOT, GLOBAL_CANDS_LOW_DIM, GLOBAL_CANDS_HIGH_DIM, MIN_CANDS, TR_FRACTION
from src.data_io import list_functions, load_xy
from src.gp_model import fit_gp, bounds_from_data
from src.strategy import load_overrides


def propose_points_for_week(seed: int, week: int) -> pd.DataFrame:
    """
    Propose one point per function using GP-UCB with adaptive strategy.
    Returns DataFrame with columns: function_id, x1, x2, ..., x8, x_concat
    """
    rng = np.random.default_rng(seed)
    overrides = load_overrides(week)

    # Collect all function IDs first for logging
    fids = []
    for fdir in list_functions(INITIAL_DATA_ROOT):
        fid = int(fdir.name.split("_")[1])
        fids.append(fid)
    fids.sort()

    # Log strategy selection report
    print("\n=== Strategy Selection Report ===")
    for fid in fids:
        if fid in overrides and overrides[fid]:
            override_params = ", ".join(f"{k}={v}" for k, v in overrides[fid].items())
            print(f"function_{fid}: USING MANUAL override → {override_params}")
        else:
            print(f"function_{fid}: USING DEFAULT strategy")
    print("=================================\n")

    # Define dimensions for each function
    dimensions = {1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 8}

    out = []
    for fdir in list_functions(INITIAL_DATA_ROOT):
        fid = int(fdir.name.split("_")[1])
        X, y = load_xy(fdir)
        d = X.shape[1]

        # Fit GP and get bounds
        gp = fit_gp(X, y)
        lo, hi = bounds_from_data(X)

        # Determine number of global candidates
        n_global = GLOBAL_CANDS_LOW_DIM if d <= 4 else GLOBAL_CANDS_HIGH_DIM

        # Apply strategy overrides
        ov = overrides.get(fid, {})
        n_global = int(max(MIN_CANDS, n_global * float(ov.get("n_candidates_multiplier", 1.0))))

        # Generate global candidates
        C_global = rng.uniform(lo, hi, size=(n_global, d))

        # Trust region logic
        use_tr = (week >= 4)
        tr_hw = tr_halfwidth(week)

        if ov.get("tr_halfwidth_override") is not None:
            use_tr = True
            tr_hw = float(ov["tr_halfwidth_override"])

        if use_tr:
            x_best = X[np.argmax(y)]
            lo_tr = np.maximum(lo, x_best - tr_hw)
            hi_tr = np.minimum(hi, x_best + tr_hw)
            n_tr = max(MIN_CANDS, int(n_global * TR_FRACTION))
            C_tr = rng.uniform(lo_tr, hi_tr, size=(n_tr, d))
            Cands = np.vstack([C_global, C_tr])
        else:
            Cands = C_global

        # GP-UCB acquisition
        mu, std = gp.predict(Cands, return_std=True)
        kappa = max(0.5, kappa_schedule(d, week) + float(ov.get("kappa_delta", 0.0)))
        acq = mu + kappa * std

        # Select best candidate with diversity tiebreaking
        best = int(np.argmax(acq))
        near = np.where(acq >= acq[best] * 0.99)[0]
        if len(near) > 1:
            best = diversity_tiebreak(Cands, X, near)

        # Ensure minimum distance from existing points
        x_star = ensure_min_distance(Cands[best], X, eps=None)

        # Clean any potential NaN values
        x_star = np.nan_to_num(x_star, nan=0.0)

        # Build row dictionary
        row = {"function_id": fid}

        # Add individual x columns (x1 through x8)
        for j in range(1, 9):  # Always create x1 to x8
            if j <= d:
                row[f"x{j}"] = float(x_star[j - 1])
            else:
                row[f"x{j}"] = np.nan  # Pad with NaN for higher dimensions

        # Add x_concat with dash separator (only actual dimensions, no NaN)
        actual_dim = dimensions.get(fid, d)
        x_concat_values = [f"{float(x_star[i]):.6f}" for i in range(actual_dim)]
        row["x_concat"] = "-".join(x_concat_values)

        out.append(row)

    return pd.DataFrame(out).sort_values("function_id").reset_index(drop=True)

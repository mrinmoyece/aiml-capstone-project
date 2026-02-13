from pathlib import Path
import pandas as pd
import numpy as np
from src.config import RUNS_BASE, INITIAL_DATA_ROOT
from src.data_io import load_xy, list_functions


def generate_reflection_pre_report(week: int, runs_root: Path = RUNS_BASE):
    wd = runs_root / f"week_{int(week):02d}"
    csv = wd / "proposals.csv"
    if not csv.exists():
        raise FileNotFoundError(f"No proposals.csv found at {csv}")

    df = pd.read_csv(csv)

    # Load strategy overrides
    strategy_path = wd / "strategy_overrides.json"
    strategy_data = {}
    if strategy_path.exists():
        import json
        with open(strategy_path, 'r') as f:
            strategy_data = json.load(f)

    # Define dimensionality for each function
    dimensions = {1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 8}

    lines = [
        f"# Week {int(week):02d} Reflection — Pre-Results",
        "",
        "## Strategy Overview",
        "",
        "This week's adaptive strategy decisions:",
        ""
    ]

    # Add strategy summary
    for fid in sorted(df['function_id'].unique()):
        strat = strategy_data.get(str(fid), {})
        lines.append(f"**Function {fid}**:")
        if strat:
            lines.append(f"- kappa_delta: {strat.get('kappa_delta', 0.0)}")
            lines.append(f"- n_candidates_multiplier: {strat.get('n_candidates_multiplier', 1.0)}")
            tr_override = strat.get('tr_halfwidth_override')
            if tr_override is not None:
                lines.append(f"- tr_halfwidth_override: {tr_override}")
        else:
            lines.append("- Using default strategy")
        lines.append("")

    lines.extend(["", "## Proposed Points", ""])

    for _, r in df.iterrows():
        fid = int(r["function_id"])
        dim = dimensions.get(fid, 8)

        # Load current data to show context
        fdir_name = f"function_{fid}"
        fdir = INITIAL_DATA_ROOT / fdir_name
        if fdir.exists():
            X, y = load_xy(fdir)
            n_obs = len(y)
            y_best = float(y.max())
        else:
            n_obs = 0
            y_best = np.nan

        # Extract x values for this function
        x_vals = []
        for i in range(dim):
            col_name = f"x{i}"
            if col_name in r and pd.notna(r[col_name]):
                x_vals.append(f"{float(r[col_name]):.6f}")
            else:
                x_vals.append("0.000000")

        x_str = ", ".join(x_vals)

        lines.append(f"**Function {fid}** (d={dim}, n={n_obs}, y_best={y_best:.6f})")
        lines.append(f"- Proposed x = [{x_str}]")
        lines.append("")

    out = wd / "reflection_pre_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_reflection_post_results(week: int, runs_root: Path = RUNS_BASE):
    wd = runs_root / f"week_{int(week):02d}"
    csv = wd / "proposals.csv"
    if not csv.exists():
        return None

    df = pd.read_csv(csv)
    dimensions = {1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 8}

    lines = [
        f"# Week {int(week):02d} Reflection — Post-Results",
        "",
        "## Results Summary",
        ""
    ]

    for _, r in df.iterrows():
        fid = int(r["function_id"])
        dim = dimensions.get(fid, 8)
        y_val = r.get("y", "")

        # Load historical data
        fdir_name = f"function_{fid}"
        fdir = INITIAL_DATA_ROOT / fdir_name
        if fdir.exists():
            _, y_hist = load_xy(fdir)
            y_prev_best = float(y_hist.max())
        else:
            y_prev_best = np.nan

        lines.append(f"**Function {fid}** (d={dim})")

        if pd.notna(y_val) and y_val != "":
            y_new = float(y_val)
            lines.append(f"- Observed y = {y_new:.6f}")

            if not np.isnan(y_prev_best):
                improvement = y_new - y_prev_best
                if improvement > 0:
                    lines.append(f"- **Improvement**: +{improvement:.6f} (new best!)")
                elif improvement < 0:
                    lines.append(f"- Change: {improvement:.6f} (below previous best)")
                else:
                    lines.append("- No change from previous best")
        else:
            lines.append("- y = <pending>")

        lines.append("")

    out = wd / "reflection_post_results.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_weekly_md_report(week: int, runs_root: Path = RUNS_BASE) -> Path:
    """Generate comprehensive weekly report with plots and reflections."""
    wd = runs_root / f"week_{int(week):02d}"
    csv = wd / "proposals.csv"
    plots_dir = wd / "plots"

    if not csv.exists():
        raise FileNotFoundError(f"No proposals.csv found at {csv}")

    df = pd.read_csv(csv)
    dimensions = {1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 8}

    lines = [
        f"# Week {int(week):02d} Report",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Proposed Points",
        ""
    ]

    for _, r in df.iterrows():
        fid = int(r["function_id"])
        dim = dimensions.get(fid, 8)

        # Load current data
        fdir_name = f"function_{fid}"
        fdir = INITIAL_DATA_ROOT / fdir_name
        if fdir.exists():
            X, y = load_xy(fdir)
            n_obs = len(y)
            y_best = float(y.max())
        else:
            n_obs = 0
            y_best = np.nan

        # Extract x values - use x1 to x{dim}, not x0
        x_vals = []
        for i in range(1, dim + 1):  # Changed from range(dim) to range(1, dim+1)
            col_name = f"x{i}"
            if col_name in r and pd.notna(r[col_name]):
                x_vals.append(f"{float(r[col_name]):.6f}")
            else:
                x_vals.append("0.000000")

        x_str = ", ".join(x_vals)

        lines.append(f"### Function {fid} (d={dim}, n={n_obs})")
        lines.append(f"- Current best: y = {y_best:.6f}")
        lines.append(f"- Proposed x = [{x_str}]")

        # Add plot if available
        snapshot_plot = plots_dir / f"function_{fid}_snapshot.png"
        if snapshot_plot.exists():
            lines.append(f"- ![Function {fid} Snapshot](plots/function_{fid}_snapshot.png)")

        pca_plot = plots_dir / f"function_{fid}_pca.png"
        if pca_plot.exists():
            lines.append(f"- ![Function {fid} PCA](plots/function_{fid}_pca.png)")

        lines.append("")

    lines.extend([
        "---",
        "",
        "## Strategy Notes",
        "",
        "See `strategy_overrides.json` for adaptive strategy parameters.",
        ""
    ])

    out = wd / "weekly_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out

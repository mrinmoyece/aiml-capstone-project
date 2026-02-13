"""
Analysis utilities for trend analysis and performance monitoring
"""
import pandas as pd
from pathlib import Path

from src.config import RUNS_BASE


def analyze_trends_for_next_week(current_week: int, runs_base: Path = RUNS_BASE) -> None:
    """
    Analyze trends from all weeks and recommend overrides for next week

    Args:
        current_week: Current week number
        runs_base: Path to runs directory
    """
    print("="*80)
    print(f"ANALYZING TRENDS FOR WEEK {current_week + 1} RECOMMENDATIONS")
    print("="*80)

    # Load recent weeks data
    weeks_data = {}
    for week in range(max(1, current_week - 2), current_week + 1):
        try:
            df = pd.read_csv(runs_base / f'week_{week:02d}' / 'proposals.csv')
            weeks_data[week] = df
        except:
            pass

    if len(weeks_data) < 2:
        print("⚠️  Need at least 2 weeks of data for trend analysis")
        return

    # Show recent trends
    print(f"\nRecent Performance Trends:")
    print("-"*80)
    print(f"{'Fn':<4} {'W{current_week-1}':<15} {'W{current_week}':<15} {'Change':<12} {'Status':<20}")
    print("-"*80)

    for fid in range(1, 9):
        recent_y = []
        for week in sorted(weeks_data.keys())[-2:]:
            row = weeks_data[week][weeks_data[week]['function_id'] == fid]
            if not row.empty:
                try:
                    recent_y.append(float(row.iloc[0]['y']))
                except:
                    pass

        if len(recent_y) == 2:
            y_prev, y_curr = recent_y
            change = ((y_curr - y_prev) / abs(y_prev)) * 100 if y_prev != 0 else 0

            if abs(change) < 5:
                status = "⏸️ STABLE"
            elif change > 20:
                status = "✅ BIG GAIN"
            elif change > 5:
                status = "↗️ IMPROVING"
            elif change > -20:
                status = "↘️ DECLINING"
            else:
                status = "⚠️ BIG DROP"

            print(f"F{fid:<3} {y_prev:<15.6e} {y_curr:<15.6e} {change:+7.1f}%    {status:<20}")

    print("\n💡 Next steps:")
    print(f"   1. Review trends above")
    print(f"   2. Manually edit runs/week_{current_week+1:02d}/overrides.csv based on patterns")
    print(f"   3. Or use automated recommendation: run analyze_trends.py from project root")


def check_week_performance(week: int, runs_base: Path = RUNS_BASE) -> None:
    """
    Validate if week N results met expectations

    Args:
        week: Week number to check
        runs_base: Path to runs directory
    """
    print(f"\n{'='*80}")
    print(f"WEEK {week} PERFORMANCE CHECK")
    print(f"{'='*80}\n")

    try:
        current = pd.read_csv(runs_base / f'week_{week:02d}' / 'proposals.csv')
        if week > 1:
            previous = pd.read_csv(runs_base / f'week_{week-1:02d}' / 'proposals.csv')
        else:
            previous = None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    week_prev_label = f"Week {week-1}" if previous is not None else "N/A"
    print(f"{'Function':<12} {week_prev_label:<15} {'Week ' + str(week):<15} {'Change':<12} {'Status':<10}")
    print("-" * 80)

    for fid in range(1, 9):
        curr_row = current[current['function_id'] == fid]

        if curr_row.empty:
            continue

        try:
            y_curr = float(curr_row.iloc[0]['y'])

            if previous is not None:
                prev_row = previous[previous['function_id'] == fid]
                if not prev_row.empty:
                    y_prev = float(prev_row.iloc[0]['y'])
                    pct_change = ((y_curr - y_prev) / abs(y_prev)) * 100 if y_prev != 0 else 0

                    if abs(pct_change) < 5:
                        status = "⏸️ STABLE"
                    elif pct_change > 15:
                        status = "✅ IMPROVED"
                    elif pct_change > 0:
                        status = "↗️ UP"
                    elif pct_change > -15:
                        status = "↘️ DOWN"
                    else:
                        status = "⚠️ DECLINED"

                    print(f"Function {fid:<4} {y_prev:<15.6e} {y_curr:<15.6e} {pct_change:+7.1f}%    {status}")
                else:
                    print(f"Function {fid:<4} {'N/A':<15} {y_curr:<15.6e} {'N/A':<12} {'NEW'}")
            else:
                print(f"Function {fid:<4} {'N/A':<15} {y_curr:<15.6e} {'N/A':<12} {'BASELINE'}")

        except (ValueError, TypeError):
            print(f"Function {fid:<4} {'N/A':<15} {'N/A':<15} {'N/A':<12} {'❌ NO DATA'}")

    print("\n" + "="*80)


def compare_override_strategies(week1: int, week2: int, runs_base: Path = RUNS_BASE) -> None:
    """
    Compare override strategies between two weeks

    Args:
        week1: First week number
        week2: Second week number
        runs_base: Path to runs directory
    """
    print(f"\n{'='*80}")
    print(f"OVERRIDE COMPARISON: Week {week1} vs Week {week2}")
    print(f"{'='*80}\n")

    try:
        w1 = pd.read_csv(runs_base / f'week_{week1:02d}' / 'overrides.csv')
        w2 = pd.read_csv(runs_base / f'week_{week2:02d}' / 'overrides.csv')
    except Exception as e:
        print(f"❌ Error loading overrides: {e}")
        return

    w1 = w1.rename(columns={
        'kappa_delta': 'w1_kappa',
        'tr_halfwidth_override': 'w1_tr',
        'n_candidates_multiplier': 'w1_n'
    })
    w2 = w2.rename(columns={
        'kappa_delta': 'w2_kappa',
        'tr_halfwidth_override': 'w2_tr',
        'n_candidates_multiplier': 'w2_n'
    })

    comparison = pd.merge(
        w1[['function_id', 'w1_kappa', 'w1_tr', 'w1_n']],
        w2[['function_id', 'w2_kappa', 'w2_tr', 'w2_n']],
        on='function_id'
    )

    comparison['Δkappa'] = comparison['w2_kappa'] - comparison['w1_kappa']
    comparison['Δtr'] = comparison['w2_tr'] - comparison['w1_tr']

    print(f"{'Fn':<4} {'W' + str(week1) + ' κ':<8} {'W' + str(week2) + ' κ':<8} {'Δκ':<8} {'W' + str(week1) + ' TR':<8} {'W' + str(week2) + ' TR':<8} {'ΔTR':<8} {'Strategy Shift':<30}")
    print("-"*80)

    for _, row in comparison.iterrows():
        fid = int(row['function_id'])
        dk = row['Δkappa']
        dtr = row['Δtr']

        if dk > 0.1:
            shift = "MORE EXPLORATION ↑"
        elif dk < -0.1:
            shift = "MORE EXPLOITATION ↓"
        else:
            shift = "MAINTAIN APPROACH →"

        print(f"F{fid:<3} {row['w1_kappa']:>7.3f}  {row['w2_kappa']:>7.3f}  {dk:+7.3f}  {row['w1_tr']:>7.3f}  {row['w2_tr']:>7.3f}  {dtr:+7.3f}  {shift:<30}")

    print("\n" + "="*80)

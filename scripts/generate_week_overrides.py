#!/usr/bin/env python3
"""
Automated override generation based on trend analysis
"""
import pandas as pd
import numpy as np
from pathlib import Path
import argparse


def analyze_function_trend(fid, weeks_data):
    """Analyze trend for a single function and recommend strategy"""
    history = []
    for week in sorted(weeks_data.keys()):
        row = weeks_data[week][weeks_data[week]['function_id'] == fid]
        if not row.empty:
            try:
                y_val = float(row.iloc[0]['y'])
                history.append({'week': week, 'y': y_val})
            except:
                pass

    if len(history) < 3:
        return None

    df_hist = pd.DataFrame(history)
    recent = df_hist.tail(3)
    y_vals = recent['y'].values

    # Calculate changes
    change_w6_w7 = ((y_vals[-1] - y_vals[-2]) / abs(y_vals[-2]) * 100) if y_vals[-2] != 0 else 0
    change_w5_w6 = ((y_vals[-2] - y_vals[-3]) / abs(y_vals[-3]) * 100) if y_vals[-3] != 0 else 0

    best_ever = df_hist['y'].max()
    current_rank = (df_hist['y'] >= y_vals[-1]).sum()
    total_weeks = len(df_hist)

    # Determine trend category
    if abs(y_vals[-1]) < 1e-20:
        trend = 'near_zero'
    elif change_w6_w7 > 50:
        trend = 'massive_gain'
    elif change_w6_w7 > 15:
        trend = 'strong_gain'
    elif change_w6_w7 > 5:
        trend = 'improving'
    elif change_w6_w7 > -5:
        trend = 'stable'
    elif change_w6_w7 > -15:
        trend = 'declining'
    elif change_w6_w7 > -50:
        trend = 'strong_drop'
    else:
        trend = 'massive_drop'

    return {
        'history': df_hist,
        'recent_values': y_vals,
        'change_w6_w7': change_w6_w7,
        'change_w5_w6': change_w5_w6,
        'best_ever': best_ever,
        'current_rank': current_rank,
        'total_weeks': total_weeks,
        'trend': trend
    }


def recommend_strategy(fid, analysis, prev_overrides):
    """Recommend strategy based on analysis"""

    # Get previous week's strategy
    prev = prev_overrides[prev_overrides['function_id'] == fid].iloc[0]
    prev_kappa = float(prev['kappa_delta'])
    prev_tr = float(prev['tr_halfwidth_override'])
    prev_n = float(prev['n_candidates_multiplier'])

    trend = analysis['trend']
    change = analysis['change_w6_w7']

    # Strategy rules based on trend
    if trend == 'near_zero':
        # Function 1 - oscillating near zero, need strong exploration
        kappa = 0.3
        tr = 0.18
        n = 2.0
        notes = f"Still near zero (W7: {analysis['recent_values'][-1]:.2e}) → moderate exploration | W6→W7 recovered from negative but still minimal | Need broader search while avoiding extreme moves"

    elif trend == 'massive_gain':
        # Functions 6, 7 - big recovery, continue exploration but consolidate
        if change > 500:  # Function 7
            kappa = 0.5
            tr = 0.24
            n = 2.2
            notes = f"HUGE breakthrough (+{change:.0f}%, {analysis['recent_values'][-2]:.4f} → {analysis['recent_values'][-1]:.4f}) → continue exploration to build on success | Best: {analysis['best_ever']:.4f} still ahead | Strong exploration to find even better regions"
        else:  # Function 6
            kappa = 0.4
            tr = 0.22
            n = 2.0
            notes = f"Strong recovery (+{change:.1f}%, {analysis['recent_values'][-2]:.4f} → {analysis['recent_values'][-1]:.4f}) → moderate exploration | W7 exploration succeeded, balance to consolidate | Still below best ({analysis['best_ever']:.4f}) → keep searching"

    elif trend == 'massive_drop':
        # Functions 3, 4 - dramatic decline, reset with strong exploration
        kappa = 0.7
        tr = 0.28
        n = 2.5
        notes = f"MAJOR REGRESSION ({change:.0f}%, {analysis['recent_values'][-2]:.4f} → {analysis['recent_values'][-1]:.4f}) → emergency exploration | W7 strategy failed badly | Aggressive search to escape poor region | Target: return to ~{analysis['best_ever']:.4f}"

    elif trend == 'stable':
        # Functions 2, 5, 8 - performing well, fine-tune
        if analysis['recent_values'][-1] > 1000:  # Function 5
            kappa = -0.5
            tr = 0.08
            n = 1.2
            notes = f"High performer stable ({analysis['recent_values'][-1]:.1f}, -{abs(change):.1f}% from peak) → strong exploitation | W6 peak: {analysis['best_ever']:.1f} → tight refinement | Lock in high-value region | Minimal exploration"
        elif analysis['recent_values'][-1] > 5:  # Function 8
            kappa = -0.1
            tr = 0.12
            n = 1.4
            notes = f"Strong stable performer ({analysis['recent_values'][-1]:.2f}) → gentle exploitation | Near best ({analysis['best_ever']:.2f}) → careful refinement | Avoid disrupting good performance"
        else:  # Function 2
            kappa = 0.3
            tr = 0.18
            n = 1.8
            notes = f"Slow steady climb ({change:+.1f}%, {analysis['recent_values'][-1]:.4f}) → moderate exploration | Best: {analysis['best_ever']:.4f} still ahead → increase search to break plateau | Need stronger push upward"

    else:  # declining, strong_gain, improving
        # Default adaptive strategy
        if trend == 'strong_gain':
            kappa = prev_kappa - 0.1  # Shift toward exploitation
            tr = prev_tr - 0.03
            n = prev_n
            notes = f"Good gain (+{change:.1f}%) → consolidate success | Reduce exploration slightly to exploit good region"
        elif trend == 'declining':
            kappa = prev_kappa + 0.2  # Increase exploration
            tr = prev_tr + 0.05
            n = prev_n + 0.2
            notes = f"Declining ({change:.1f}%) → increase exploration | Escape declining region"
        else:  # improving
            kappa = prev_kappa
            tr = prev_tr
            n = prev_n
            notes = f"Improving (+{change:.1f}%) → maintain strategy"

    return {
        'function_id': fid,
        'kappa_delta': kappa,
        'tr_halfwidth_override': tr,
        'n_candidates_multiplier': n,
        'notes': notes
    }


def generate_overrides(week_num, runs_base='runs'):
    """Generate overrides.csv for specified week based on trend analysis"""
    runs_base = Path(runs_base)

    # Load historical data
    weeks_data = {}
    for week in range(1, week_num):
        try:
            df = pd.read_csv(runs_base / f'week_{week:02d}' / 'proposals.csv')
            weeks_data[week] = df
        except:
            pass

    if len(weeks_data) < 2:
        print(f"❌ Need at least 2 weeks of data to generate week {week_num} overrides")
        return None

    # Load previous week's overrides
    prev_overrides = pd.read_csv(runs_base / f'week_{week_num-1:02d}' / 'overrides.csv')

    print("="*80)
    print(f"GENERATING WEEK {week_num} OVERRIDES BASED ON TREND ANALYSIS")
    print("="*80)

    recommendations = []

    for fid in range(1, 9):
        analysis = analyze_function_trend(fid, weeks_data)
        if analysis:
            rec = recommend_strategy(fid, analysis, prev_overrides)
            recommendations.append(rec)

            print(f"\n📊 Function {fid}:")
            print(f"   Trend: {analysis['trend']}")
            print(f"   W6→W7: {analysis['change_w6_w7']:+.1f}%")
            print(f"   Current: {analysis['recent_values'][-1]:.4e}")
            print(f"   Best: {analysis['best_ever']:.4e}")
            print(f"   → κ={rec['kappa_delta']:.2f}, TR={rec['tr_halfwidth_override']:.2f}, N={rec['n_candidates_multiplier']:.1f}")

    # Create DataFrame and save
    df = pd.DataFrame(recommendations)

    # Ensure output directory exists
    out_dir = runs_base / f'week_{week_num:02d}'
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / 'overrides.csv'
    df.to_csv(out_path, index=False)

    print(f"\n✅ Generated: {out_path}")
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate week overrides based on trend analysis')
    parser.add_argument('week', type=int, help='Week number to generate overrides for')
    parser.add_argument('--runs-base', default='runs', help='Base directory for runs (default: runs)')

    args = parser.parse_args()

    df = generate_overrides(args.week, args.runs_base)
    if df is not None:
        print("\n" + "="*80)
        print("GENERATED OVERRIDES:")
        print("="*80)
        print(df.to_string(index=False))


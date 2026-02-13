# Developer Guide

*Technical details for understanding and extending the codebase*

---

## Architecture Overview

This project implements Bayesian Optimization using a modular architecture. The core idea: separate concerns so you can swap strategies, test alternatives, and debug issues without touching everything.

### Core Components

**1. Gaussian Process Model (`src/gp_model.py`)**

The GP acts as our "map" of the unknown function. Given past observations, it predicts both the expected value μ(x) and uncertainty σ(x) at any new point.

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

# ARD RBF kernel: learns different length scales per dimension
kernel = RBF(length_scale=[1.0]*d, length_scale_bounds=(0.01, 10.0)) + WhiteKernel()
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
```

**Why ARD (Automatic Relevance Determination)?** Some dimensions matter more than others. ARD figures this out automatically by learning separate length scales. If dimension 3 has length_scale=0.1 and dimension 5 has length_scale=5.0, the function changes faster along dimension 3—so that's more important.

**2. Acquisition Function (`src/acquisition.py`)**

This is where decisions happen. UCB (Upper Confidence Bound) combines exploitation and exploration:

```python
def ucb(gp, X_candidates, kappa=2.0):
    mu, sigma = gp.predict(X_candidates, return_std=True)
    return mu + kappa * sigma
```

- **High μ(x)**: Go where predictions look good (exploitation)
- **High σ(x)**: Go where we're uncertain (exploration)
- **kappa**: The dial that controls the balance

**The kappa discovery**: Standard textbooks say κ=2.0. That's fine for early exploration, but terrible near peaks. Week 10 crash taught me that κ=-0.7 makes the GP overconfident—it searches within 0.05 units of current best, missing peaks 0.10 units away. Sweet spot: κ=-0.3 for exploitation, κ=+0.7 for emergency exploration.

**3. Candidate Generation (`src/proposer.py`)**

We don't optimize UCB analytically (no closed form). Instead, we sample 20k-45k candidate points and evaluate UCB on all of them. The best one wins.

```python
# Generate candidates
if d <= 3:
    n_candidates = 20000  # Lower dimensions need fewer
else:
    n_candidates = 45000  # Higher dimensions need denser sampling

X_cands = np.random.uniform(0, 1, size=(n_candidates, d))

# Apply trust region constraint
if trust_region_active:
    X_cands = filter_by_trust_region(X_cands, x_best, radius)

# Evaluate and select
scores = ucb(gp, X_cands, kappa=adaptive_kappa)
x_next = X_cands[np.argmax(scores)]
```

**Why so many candidates?** In 8D, the search space has 10^8 grid points (if you discretized to 0.01 resolution). Random sampling with 45k points gives decent coverage while staying computationally feasible.

**4. Adaptive Strategy (`src/strategy.py`)**

This is where the intelligence lives. Each function gets analyzed weekly:

```python
def analyze_function(func_id, history):
    # Performance metrics
    y_best = history.max()
    y_current = history[-1]
    pct_of_best = (y_current / y_best) * 100
    
    # Volatility
    cv = history.std() / abs(history.mean())
    
    # Trend
    recent_change = (history[-1] - history[-3]) / history[-3] * 100
    
    # Decide strategy
    if pct_of_best >= 95 and cv < 0.3:
        return {"kappa": -0.3, "trust_region": 0.08, "mode": "gentle_exploit"}
    elif pct_of_best < 50 or recent_change < -70:
        return {"kappa": +0.7, "trust_region": 0.28, "mode": "emergency_explore"}
    else:
        return {"kappa": +0.2, "trust_region": 0.15, "mode": "balanced"}
```

This isn't magic—it's pattern matching based on what worked in previous weeks.

**5. Data I/O (`src/data_io.py`)**

Handles loading/saving with validation:

```python
def load_function_data(func_id):
    """Load initial + all weekly results"""
    inputs = np.load(f"initial_data/function_{func_id}/initial_inputs.npy")
    outputs = np.load(f"initial_data/function_{func_id}/initial_outputs.npy")
    
    # Validation
    assert inputs.shape[0] == outputs.shape[0]
    assert np.all((inputs >= 0) & (inputs <= 1))
    
    return inputs, outputs
```

Always validates bounds. Week 3 had a bug where a proposal outside [0,1] got submitted—cost me a week. Now everything's checked.

---

## Configuration

### Global Settings (`src/config.py`)

```python
WEEK = 13  # Current week
SEED = 123  # Reproducibility
GLOBAL_CANDS_LOW_DIM = 20000
GLOBAL_CANDS_HIGH_DIM = 45000
TR_FRACTION = 0.5  # Trust region as fraction of [0,1]
```

Change `WEEK` before each run. Everything else stays constant for reproducibility.

### Per-Function Overrides (`runs/week_XX/overrides.csv`)

```csv
function_id,kappa_delta,tr_halfwidth_override,n_candidates_multiplier,notes
5,-0.3,0.08,1.0,"Stable performer, gentle exploitation"
7,+0.7,0.28,2.0,"Emergency mode after Week 11 stagnation"
```

This file overrides defaults. Empty means "use adaptive strategy."

---

## Weekly Workflow

This is how I actually ran things each week:

### Step 1: Update Data with Previous Week's Results

```python
# In notebook or Python REPL
from src.data_io import apply_week_csv
apply_week_csv("runs/week_12", bounds_policy="clip")
```

This reads `runs/week_12/proposals.csv` (which now has y values filled in), validates them, and updates the .npy files.

### Step 2: Generate New Strategy

```bash
make trends N=13
```

Or manually:
```python
from scripts.generate_week_overrides import main
main(week=13)
```

This analyzes all functions, detects patterns (crash/breakthrough/plateau), and writes `runs/week_13/overrides.csv` with recommendations.

### Step 3: Review and Adjust

Open `runs/week_13/overrides.csv`. If the automated strategy seems wrong (e.g., it wants to exploit a function that just crashed), manually edit it.

### Step 4: Run Optimization

Open `notebooks/01_bo_ucb_week_runner.ipynb` and run top to bottom. This:
- Loads data
- Fits GPs
- Generates candidates
- Applies UCB
- Writes `runs/week_13/proposals.csv`

### Step 5: Validate

```bash
make validate N=13
```

Checks:
- All coordinates in [0,1]
- Correct number of proposals (8)
- CSV format correct
- No duplicate points

### Step 6: Submit

Upload `runs/week_13/proposals.csv` to the course portal. Wait a week for results.

---

## Key Design Decisions

### Why scikit-learn Instead of BoTorch?

BoTorch is fancier—supports batch acquisition, fantasy models, GPU acceleration. But:

1. **We have <100 samples per function**. Exact GP inference is O(n³). With n=23, that's 12k operations—trivial on CPU.
2. **No batch acquisition needed**. We submit 1 point per function per week.
3. **Simpler debugging**. When Week 10 crashed, I could inspect `gp.kernel_.length_scale_` directly. BoTorch's PyTorch backend is more opaque.
4. **Stability**. scikit-learn has 15 years of battle-testing. BoTorch is newer, API still evolving.

If this were a production system with 1000+ samples, I'd reconsider. For research/coursework, sklearn is perfect.

### Why Trust Regions?

Without trust regions, UCB sometimes suggests points far from current best—especially when σ(x) is high in unexplored regions. In Week 4, F6 got a suggestion 0.4 units away from its peak (in a 5D space). That sample wasted a week.

Trust regions say: "Only search within radius R of current best." This focuses samples where they're likely to matter. You can still explore by widening R (F7 used R=0.28 in emergency mode).

Trade-off: Trust regions can trap you in local optima. That's why we adaptive-size them based on volatility.

### Why Adaptive kappa?

Fixed κ=2.0 (textbook default) treats all functions the same. Reality:

- **F5 at 95.8% of best**: Needs κ=-0.3 (gentle refinement)
- **F7 at 0.4% of best**: Needs κ=+0.7 (aggressive exploration)
- **F4 after crashing**: Needs κ=+0.7 (recovery mode)

One size doesn't fit all. Adaptive κ based on performance + volatility works way better.

---

## Validation & Testing

### Pre-Submission Checks

```bash
# Check proposals format
python scripts/validate_proposals.py --week 13

# Check overrides format
python scripts/validate_overrides.py --week 13

# Sanity check data integrity
python scripts/sanity_check.py
```

### What Can Go Wrong

**Issue**: Proposal outside [0,1] bounds  
**Solution**: `validate_proposals.py` catches this. If it happens, usually means trust region + current best is near boundary.

**Issue**: GaussianProcessRegressor fails to converge  
**Solution**: Usually means kernel hyperparameters hit bounds. Increase `n_restarts_optimizer` or widen `length_scale_bounds`.

**Issue**: All candidates have similar UCB scores  
**Solution**: Either you're at optimum (σ(x) ≈ 0 everywhere) or GP is overconfident. Check σ values. If all < 0.01, consider increasing noise or adding more exploration.

---

## Extending the Code

### Adding a New Acquisition Function

1. Create `src/acquisition_new.py`:
```python
def expected_improvement(gp, X_candidates, y_best):
    mu, sigma = gp.predict(X_candidates, return_std=True)
    z = (mu - y_best) / sigma
    ei = sigma * (z * norm.cdf(z) + norm.pdf(z))
    return ei
```

2. Modify `src/proposer.py`:
```python
from src.acquisition_new import expected_improvement
scores = expected_improvement(gp, X_cands, y_best)
```

### Adding a New Kernel

```python
from sklearn.gaussian_process.kernels import Matern

# Matern 5/2: twice differentiable (vs infinite for RBF)
kernel = Matern(length_scale=[1.0]*d, nu=2.5) + WhiteKernel()
```

Matern is good for functions with "kinks" or sudden changes. RBF assumes infinite smoothness.

### Adding Multi-Fidelity

This requires cheap approximations of the expensive function. Not applicable to our black-box setting (no cheap evaluations available).

But if you had them:
```python
# High-fidelity: expensive, accurate
# Low-fidelity: cheap, approximate

# Train 2 GPs
gp_high = fit_gp(X_high, y_high)
gp_low = fit_gp(X_low, y_low)

# Model correlation
rho = learn_correlation(gp_high, gp_low)

# Use low-fi to pre-screen, high-fi to refine
```

---

## Performance Tuning

### M1/M2 Mac Optimization

The code runs fast on Apple Silicon because:
1. NumPy uses Accelerate framework (BLAS/LAPACK)
2. No GPU needed (sklearn is CPU-bound anyway)
3. Candidate generation is vectorized

45k candidates in 8D takes ~2 seconds total (generation + UCB eval).

### Bottlenecks

- **GP fitting**: O(n³) in samples. With n=23, negligible. If you had n=1000, use inducing points.
- **Candidate evaluation**: O(n_cands * n_samples). Dominates runtime. Parallelizable but not necessary.

---

## Common Pitfalls

**1. Forgetting to update WEEK in config.py**  
Result: Proposals overwrite previous week

**2. Not validating before submitting**  
Result: Out-of-bounds proposal, wasted week

**3. Trusting GP uncertainty far from data**  
Result: σ(x) is huge in unexplored regions, UCB suggests bad points. Use trust regions.

**4. Aggressive exploitation too early**  
Result: Week 10 crash. See REFLECTIONS.md for full story.

**5. Ignoring volatility**  
Result: Applying tight trust regions to volatile functions. They need space to explore.

---

## Debugging Tips

### GP isn't fitting well
```python
print(gp.kernel_)  # Check learned hyperparameters
print(gp.log_marginal_likelihood_value_)  # Should be reasonable
```

If length_scales hit bounds (0.01 or 10.0), widen them.

### Proposals seem random
```python
# Check UCB distribution
scores = ucb(gp, X_cands, kappa=current_kappa)
print(f"UCB range: [{scores.min():.3f}, {scores.max():.3f}]")
print(f"UCB std: {scores.std():.3f}")
```

If std is tiny, GP is overconfident. Increase kappa or add noise.

### Function not improving
Check:
1. Are you stuck in local optimum? (Try wider trust region)
2. Is GP overconfident? (Check σ values, increase noise)
3. Is landscape truly difficult? (F7 stayed hard despite everything)

---

## References

For deeper understanding:

- **Rasmussen & Williams (2006)**: GP textbook, explains kernels/inference
- **Srinivas et al. (2010)**: GP-UCB algorithm, regret bounds
- **Frazier (2018)**: Practical BO tutorial, good for implementation details


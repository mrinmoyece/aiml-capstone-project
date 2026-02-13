# Project Structure & Organization

This document provides a detailed overview of the repository structure, explaining the purpose of each component.

---

## 📁 Directory Structure

```
aiml-capstone-project/
├── src/                    # Core Python modules
├── scripts/                # Utility scripts
├── notebooks/              # Jupyter notebooks
├── initial_data/           # Initial training data
├── runs/                   # Weekly execution results
├── docs/                   # Documentation
├── Makefile                # Automation
├── requirements.txt        # Dependencies
├── README.md               # Main documentation
├── .gitignore              # Git ignore rules
└── cleanup.sh              # Repository cleanup
```

---

## 📦 Core Modules (`src/`)

### `config.py`
**Global Configuration**
- `WEEK`: Current week number
- `SEED`: Random seed for reproducibility
- `PROJECT_ROOT`, `RUNS_BASE`: Path management
- `GLOBAL_CANDS_LOW_DIM/HIGH_DIM`: Candidate generation sizes
- `TR_FRACTION`: Trust region sizing

### `data_io.py`
**Data Loading & Validation**
- `load_initial_data()`: Load initial training samples
- `load_week_data()`: Load specific week results
- `load_all_data()`: Aggregate historical data
- `save_proposals()`: Write proposals.csv
- Handles numpy `.npy` files and CSV formats

### `gp_model.py`
**Gaussian Process Surrogate**
- `fit_gp()`: Train GP with ARD RBF kernel
- `predict()`: Get mean and variance predictions
- Uses `sklearn.gaussian_process.GaussianProcessRegressor`
- ARD (Automatic Relevance Determination) for feature importance

### `acquisition.py`
**UCB Acquisition Function**
- `ucb(gp, X_cands, kappa)`: Compute UCB scores
- `UCB(x) = μ(x) + κ·σ(x)`
- Supports adaptive κ per function
- Handles batch candidate evaluation

### `proposer.py`
**Candidate Generation & Selection**
- `generate_candidates()`: Create candidate points
  - Random sampling in bounds
  - Trust region constraints
  - Boundary handling
- `select_best()`: Maximize UCB to pick x*
- `ensure_valid()`: Bounds clipping, precision formatting

### `strategy.py`
**Adaptive Strategy Logic**
- `determine_kappa()`: Compute adaptive exploration weight
- `determine_trust_region()`: Set search radius
- `analyze_performance()`: Assess recent trajectory
- Implements pattern-based decision rules

### `overrides.py`
**Per-Function Parameter Overrides**
- `load_overrides()`: Read `overrides.csv`
- `apply_overrides()`: Override default κ, TR, N
- `validate_overrides()`: Check format and bounds
- Enables differential treatment per function

### `visualize.py`
**Plotting & Visualization**
- `plot_gp_prediction()`: 2D GP landscape (mean, std)
- `plot_acquisition()`: UCB surface
- `plot_convergence()`: Performance over weeks
- `plot_performance_summary()`: Multi-function dashboard
- Uses matplotlib with consistent styling

### `analysis.py`
**Performance Analysis Tools**
- `compute_regret()`: Distance from best known
- `analyze_convergence()`: Detect saturation
- `identify_clusters()`: Spatial pattern recognition
- `compute_statistics()`: Mean, std, trends
- Supports multi-week comparative analysis

### `report.py`
**Report Generation**
- `generate_weekly_report()`: Markdown report
- `create_summary_table()`: Performance metrics
- `export_pdf()`: PDF conversion (optional)
- Integrates plots and analysis

### `reflect.py`
**Automated Reflection Generation**
- `generate_reflection()`: Create reflection prompts
- `analyze_patterns()`: Pattern recognition
- `suggest_improvements()`: Next-week recommendations
- Supports critical thinking documentation

---

## 🔧 Utility Scripts (`scripts/`)

### `generate_week_overrides.py`
**Automated Strategy Generation**
```bash
python scripts/generate_week_overrides.py 11
```
- Analyzes past 3-5 weeks performance
- Detects trends (improving, declining, crashing)
- Generates adaptive overrides.csv
- Categorizes into emergency/strong/moderate/exploit

### `validate_proposals.py`
**Pre-Submission Validation**
```bash
python scripts/validate_proposals.py --week 11
```
- Checks bounds [0, 1]
- Verifies dimensions per function
- Validates precision (6 decimal places)
- Ensures no duplicates or NaN values

### `validate_overrides.py`
**Override Format Checking**
```bash
python scripts/validate_overrides.py --week 11
```
- Validates CSV structure
- Checks κ, TR, N ranges
- Ensures all 8 functions present
- Verifies notes field exists

### `sanity_check.py`
**Data Integrity Verification**
```bash
python scripts/sanity_check.py
```
- Checks initial_data/ completeness
- Validates numpy file formats
- Verifies X-y alignment
- Detects corrupted data

---

## 📓 Jupyter Notebooks (`notebooks/`)

### `01_bo_ucb_week_runner.ipynb`
**Main Weekly Execution Notebook**

**Cell 1: Audit**
- Load and verify all historical data
- Display dataset statistics
- Check for missing weeks

**Cell 2: Initial Data Visualization (Optional)**
- Plot initial training samples
- Show data distributions

**Cell 3: Strategy Scan**
- Load overrides.csv
- Display adaptive parameters per function
- Show differential strategies

**Cell 4: Generate Proposals** ⭐
- Fit Gaussian Processes
- Generate candidates
- Compute UCB scores
- Select best x* per function
- **Output:** `runs/week_XX/proposals.csv`

**Cell 5: Visualization**
- GP prediction plots (2D functions)
- Acquisition landscapes
- Convergence curves

**Cell 6: Report Generation**
- Create weekly_report.md
- Performance summary tables
- Export visualizations

---

## 💾 Data Structure

### `initial_data/function_[1-8]/`
**Initial Training Samples**
- `initial_inputs.npy`: Shape (17, d) - Initial X values
- `initial_outputs.npy`: Shape (17,) - Initial y values
- Provided at project start
- Never modified (immutable training set)

### `runs/week_XX/`
**Weekly Execution Results**

#### `proposals.csv`
```csv
function_id,x1,x2,x3,x4,x5,x6,x7,x8,x_concat,y,status,method,created_at,applied_at
1,0.689794,0.176574,,,,,,,0.689794-0.176574,4.78e-93,applied,gp_ucb_adaptive_wk10,...
```
- Submitted xi values (x1, x2, ..., xd)
- Received y values (filled after evaluation)
- Metadata: method, timestamps

#### `overrides.csv`
```csv
function_id,kappa_delta,tr_halfwidth_override,n_candidates_multiplier,notes
1,-0.2,0.10,1.5,"W9: -7.47e-12 | W10: 4.78e-93 | Strategy: gentle exploitation..."
```
- Per-function adaptive parameters
- Detailed historical notes
- Strategy rationale

#### `plots/`
- `gp_predictions_fX.png`: GP landscapes
- `acquisition_fX.png`: UCB surfaces
- `convergence.png`: Performance trajectories
- `summary_dashboard.png`: Multi-function overview

#### `weekly_report.md`
- Performance analysis
- Strategy evaluation
- Lessons learned
- Next-week recommendations

---

## 📚 Documentation (`docs/`)

### Core Documents

#### `RESULTS.md`
**Comprehensive Performance Analysis**
- Week-by-week results table
- Best values achieved per function
- Performance trends
- Success rate analysis

#### `STRATEGY_EVOLUTION.md`
**Decision Log & Rationale**
- Strategy changes per week
- Rationale for each decision
- Lessons learned
- Pattern recognition insights

#### `CHANGELOG.md`
**Week-by-Week Changes**
- Code modifications
- Strategy adjustments
- Bug fixes
- Enhancements

#### `REPOSITORY_SUMMARY.md`
**High-Level Overview**
- Project goals
- Methodology summary
- Key achievements
- Future directions

### Reflections (`docs/reflections/`)

Critical thinking documents addressing:
- Scaling laws and emergent behaviors
- Transparency and reproducibility
- Assumptions and limitations
- Pattern recognition and clustering
- LLM prompting strategies (if applicable)

---

## 🔄 Workflow

### Typical Weekly Cycle

```
1. Receive Week N results
   ↓
2. make trends N=N+1
   → Generates adaptive strategy
   ↓
3. Review & edit overrides.csv
   → Adjust if needed
   ↓
4. Open Jupyter notebook
   → Run cells 1-6
   ↓
5. make validate N=N+1
   → Pre-submission checks
   ↓
6. Submit proposals.csv
   → Evaluation portal
   ↓
7. Document & reflect
   → Update docs/
```

### Automation with Makefile

```bash
# Show help
make help

# Generate Week 12 strategy
make trends N=12

# Validate proposals
make validate N=12

# Full workflow
make all N=12
```

---

## 🛡️ Quality Assurance

### Validation Layers

1. **Bounds Checking**: All xi ∈ [0, 1]
2. **Dimension Verification**: Correct d per function
3. **Precision Formatting**: 6 decimal places
4. **No Duplicates**: Unique proposals
5. **No NaN/Inf**: Valid float values
6. **CSV Structure**: Correct columns and headers

### Testing Strategy

```bash
# Data integrity
python scripts/sanity_check.py

# Proposals format
python scripts/validate_proposals.py --week 11

# Overrides format
python scripts/validate_overrides.py --week 11

# All validations
make test
```

---

## 🎨 Code Style & Standards

### Python Style
- **PEP 8** compliant
- **Black** formatter (line-length=88)
- **Type hints** where beneficial
- **Docstrings** for all public functions

### Naming Conventions
- `snake_case` for functions and variables
- `UPPER_CASE` for constants
- Descriptive names (avoid abbreviations)

### Documentation
- Module-level docstrings
- Function docstrings with Args/Returns
- Inline comments for complex logic
- Markdown for reports and reflections

---

## 📊 Data Flow Diagram

```
initial_data/
    ├── function_1/initial_inputs.npy
    └── function_1/initial_outputs.npy
         ↓
    [Load Data] → data_io.py
         ↓
    [Fit GP] → gp_model.py
         ↓
    [Generate Candidates] → proposer.py
         ↓
    [Score with UCB] → acquisition.py
         ↓
    [Apply Strategy] → strategy.py + overrides.py
         ↓
    [Select Best] → proposer.py
         ↓
    runs/week_XX/proposals.csv
         ↓
    [Submit to Black-Box]
         ↓
    [Receive y values]
         ↓
    [Update proposals.csv]
         ↓
    [Next Week...]
```

---

## 🚀 Getting Started (Quick)

```bash
# 1. Clone and setup
git clone <repo-url>
cd aiml-capstone-project
make install

# 2. Check current state
make check-week

# 3. Generate next strategy
make trends N=12

# 4. Run notebook
jupyter notebook notebooks/01_bo_ucb_week_runner.ipynb

# 5. Validate
make validate N=12

# 6. Submit proposals.csv
```


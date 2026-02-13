# How to Run the Project

*Complete guide for running the Bayesian Optimization workflow*

---

## Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Weekly Workflow (7 Steps)](#weekly-workflow)
3. [Quick Commands](#quick-commands)
4. [Troubleshooting](#troubleshooting)
5. [Advanced Usage](#advanced-usage)

---

## First-Time Setup

Do this once when starting the project:

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Verify Setup
```bash
# Check everything is installed correctly
make test
```

### 3. Prepare Initial Data

Ensure your starting data is in place:
```
initial_data/
├── function_1/
│   ├── initial_inputs.npy
│   └── initial_outputs.npy
├── function_2/
│   ├── initial_inputs.npy
│   └── initial_outputs.npy
...
└── function_8/
    ├── initial_inputs.npy
    └── initial_outputs.npy
```

**You're ready!** Now follow the weekly workflow below.

---

## Weekly Workflow

Follow these 7 steps each week to generate new proposals:

---

### Step 1: Fill in Last Week's Results (2 min)

**When you receive results** from the evaluation portal:

1. Open `runs/week_{N-1}/proposals.csv` (e.g., `runs/week_12/proposals.csv`)
2. Fill in the `y` column with the results you received
3. Save the file

**Example:**
```csv
function_id,x_concat,y
1,"0.123456,0.234567",-4.97e-34
2,"0.789012,0.345678",0.614
3,"0.456789,0.567890,0.678901",-0.037
...
```

---

### Step 2: Update Dataset (1 min)

Apply last week's results to the main dataset:

**Option A - In Python:**
```bash
python3 << EOF
from src.data_io import apply_week_csv
apply_week_csv("runs/week_12", bounds_policy="clip")
print("✅ Data updated successfully")
EOF
```

**Option B - In Jupyter Notebook:**
```python
from src.data_io import apply_week_csv
apply_week_csv("runs/week_12", bounds_policy="clip")
```

This appends the new data to `initial_data/function_X/*.npy` files.

---

### Step 3: Set Current Week (30 sec)

Open `src/config.py` and update the week number:

```python
WEEK = 13  # ← Change this to your current week
```

---

### Step 4: Generate Strategy (Optional, 1 min)

Let the system analyze trends and recommend strategies:

```bash
make trends N=13
```

**This creates:** `runs/week_13/overrides.csv` with recommended κ, trust regions, and candidate counts.

**Skip this step if:** You want to create your strategy manually.

---

### Step 5: Review Strategy (2 min)

Open `runs/week_13/overrides.csv` and review:

```csv
function_id,kappa_delta,tr_halfwidth_override,n_candidates_multiplier,notes
5,-0.3,0.08,1.0,"Stable at 95% - gentle exploitation"
7,+0.7,0.28,2.0,"Stuck at 0.4% - emergency exploration"
```

**Edit if needed:**
- If a function just crashed, don't use exploitation (negative κ)
- If a function is doing well, protect it with gentle exploitation
- Trust the automated strategy unless you have good reason to change it

**Create manually if needed:**
```bash
# Empty overrides means use default strategy
echo "function_id,kappa_delta,tr_halfwidth_override,n_candidates_multiplier,notes" > runs/week_13/overrides.csv
```

---

### Step 6: Run Optimization (3 min)

**Option A - Jupyter Notebook (Recommended):**
```bash
jupyter notebook notebooks/01_bo_ucb_week_runner.ipynb
```

Then: **Kernel → Restart & Run All**

**Watch for:**
- ✅ All 8 functions load correctly
- ✅ GPs fit without errors
- ✅ UCB scores computed
- ✅ Proposals written to `runs/week_13/proposals.csv`

**Option B - Command Line:**
```bash
jupyter nbconvert --to notebook --execute notebooks/01_bo_ucb_week_runner.ipynb
```

---

### Step 7: Validate & Submit (1 min)

**Validate proposals:**
```bash
make validate N=13
```

**This checks:**
- ✅ All coordinates in [0, 1]
- ✅ Exactly 8 proposals (one per function)
- ✅ Correct CSV format
- ✅ No duplicate proposals

**If validation passes:**
Upload `runs/week_13/proposals.csv` to the course portal.

**If validation fails:**
Fix the issues reported and re-run the notebook.

---

### Summary: 7 Steps, ~10 Minutes Total

| Step | Task | Time | Required? |
|------|------|------|-----------|
| 1 | Fill in y values | 2 min | ✅ Yes |
| 2 | Update dataset | 1 min | ✅ Yes |
| 3 | Set week number | 30 sec | ✅ Yes |
| 4 | Generate strategy | 1 min | ⚠️ Optional |
| 5 | Review strategy | 2 min | ⚠️ Recommended |
| 6 | Run notebook | 3 min | ✅ Yes |
| 7 | Validate & submit | 1 min | ✅ Yes |
| **Total** | | **~10 min** | |

---

---

## Quick Commands Reference

### Makefile Shortcuts
```bash
make install          # Install dependencies (first-time setup)
make trends N=13      # Generate strategy for week 13
make validate N=13    # Validate proposals before submitting
make check-week       # Show current week from config.py
make test             # Run all validation checks
make clean            # Remove temporary files
```

### Manual Commands
```bash
# Generate strategy manually
python scripts/generate_week_overrides.py --week 13

# Validate proposals manually
python scripts/validate_proposals.py --week 13

# Validate overrides
python scripts/validate_overrides.py --week 13

# Data integrity check
python scripts/sanity_check.py
```

---

## File Structure

Understanding where files are and what they do:

```
Key Files for Weekly Workflow:

src/config.py                           ← Step 3: Update WEEK here

runs/
├── week_12/
│   └── proposals.csv                   ← Step 1: Fill y values here
│
└── week_13/
    ├── overrides.csv                   ← Step 4-5: Strategy (review/edit)
    ├── proposals.csv                   ← Step 6: Generated proposals (submit this!)
    ├── meta.json                       ← Auto-generated metadata
    └── plots/                          ← Auto-generated visualizations

initial_data/
└── function_X/
    ├── initial_inputs.npy              ← Step 2: Updated with new data
    └── initial_outputs.npy             ← Step 2: Updated with new data

notebooks/
└── 01_bo_ucb_week_runner.ipynb         ← Step 6: Run this
```

---

## Troubleshooting

### Common Issues and Solutions

#### "Week number mismatch"
**Symptom**: Notebook shows wrong week number  
**Solution**: Update `WEEK` in `src/config.py`

#### "File not found: runs/week_12/proposals.csv"
**Symptom**: Can't find last week's results  
**Solution**: 
- If first run: Skip Step 2 (no previous data to apply)
- Otherwise: Create the file and fill in y values from Step 1

#### "Proposal outside [0,1] bounds"
**Symptom**: Validation fails due to out-of-bounds coordinates  
**Solution**: 
- Check `overrides.csv` - trust region might be too large
- Reduce `tr_halfwidth_override` for affected function
- Current best might be near boundary (0 or 1)

#### "GP fitting failed"
**Symptom**: Gaussian Process won't fit to data  
**Solution**: 
- In `src/gp_model.py`, increase `n_restarts_optimizer` from 10 to 20
- Or widen `length_scale_bounds` to allow more flexibility
- Check data has no duplicates or NaN values

#### "All proposals look random"
**Symptom**: UCB scores are similar, no clear best point  
**Solution**: 
- GP is overconfident (σ≈0 everywhere)
- Increase κ in `overrides.csv` to add more exploration
- Or increase noise term in GP kernel

#### "Notebook kernel died"
**Symptom**: Jupyter kernel crashes during execution  
**Solution**:
- Reduce `n_candidates_multiplier` in `overrides.csv`
- Close other memory-intensive programs
- Restart kernel and try again

---

## Advanced Usage

### Running Specific Functions Only

Edit the notebook to process only certain functions:

```python
# In the main loop, filter by function ID:
for func_id in [3, 4, 7]:  # Only optimize these
    # ...existing code...
```

### Custom Strategy Creation

Create `runs/week_13/overrides.csv` manually instead of using automated generation:

```csv
function_id,kappa_delta,tr_halfwidth_override,n_candidates_multiplier,notes
1,0.0,0.15,1.0,"Neutral - balanced exploration/exploitation"
5,-0.5,0.08,1.0,"Strong exploitation - near peak"
7,+0.8,0.30,2.5,"Maximum exploration - stuck in local minimum"
```

**Parameter meanings:**
- `kappa_delta`: -0.7 to +0.8 (negative=exploit, positive=explore)
- `tr_halfwidth_override`: 0.05 to 0.30 (search radius around best)
- `n_candidates_multiplier`: 0.5 to 3.0 (adjusts candidate pool size)

### Batch Processing Multiple Weeks

Process several weeks at once (useful for catching up):

```bash
for week in 10 11 12 13; do
    echo "=== Processing Week $week ==="
    
    # Update config
    sed -i '' "s/WEEK = .*/WEEK = $week/" src/config.py
    
    # Generate strategy
    make trends N=$week
    
    # Run optimization
    jupyter nbconvert --to notebook --execute notebooks/01_bo_ucb_week_runner.ipynb
    
    # Validate
    make validate N=$week
    
    echo "✅ Week $week complete"
done
```

### Experimenting Without Affecting Main Run

Create experimental runs:

```bash
# Copy week folder
cp -r runs/week_13 runs/week_13_experiment

# Modify strategy in experimental folder
nano runs/week_13_experiment/overrides.csv

# Update notebook to use experimental folder
# Then compare results
```

---

## Tips from 13 Weeks of Optimization

**Weeks 1-3 (Early Exploration)**:
- Use broad exploration (κ=0.5-0.6)
- Don't worry about finding optima yet
- Goal: Understand the landscape

**Weeks 4-6 (Differentiation)**:
- High performers get tighter trust regions
- Volatile functions need wider search areas
- Start adapting per function

**Weeks 7-9 (Learning from Failures)**:
- Watch for crashes (>50% decline)
- Switch to emergency exploration immediately
- Don't exploit too early

**Weeks 10-13 (Refinement)**:
- Gentle exploitation (κ=-0.3) beats aggressive (κ=-0.7)
- Protect high performers in final weeks
- Don't explore on already-strong functions

---

## Need Help?

1. **Technical details**: See `docs/DEVELOPER_GUIDE.md`
2. **Weekly progress**: See `docs/WEEKLY_PROGRESS.md`
3. **Data information**: See `DATASHEET.md`
4. **Model details**: See `MODEL_CARD.md`
5. **Strategy insights**: Check `docs/archive_originals/` for reflections
6. **Questions**: Open an [Issue](../../issues) on GitHub


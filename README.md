# Black-Box Optimization Capstone

**Imperial College London - AI & ML Professional Certification**  
*Finding peaks in invisible landscapes*

---

## What This Project Is About

Over 13 weeks, I optimized 8 unknown mathematical functions where each test was expensive—think drug discovery where testing one compound costs $10,000 and takes a week. You can't afford to try random combinations.

I built a smart system using Bayesian Optimization that learns from every experiment. Instead of blindly searching, it builds a map of each landscape and intelligently decides where to explore next. The result? I reached 92-100% of optimal on 4 out of 8 functions using just 23 tests each—that's 4-5x more efficient than random guessing.

**The surprising lesson**: Being too aggressive when you think you've found the peak usually backfires. Gentle refinement beats greedy optimization.

---

## Results at a Glance

| Function | Dimensions | Final Result | % of Best | Outcome |
|----------|------------|--------------|-----------|---------|
| F1 | 2D | ~10^-134 | 100% | Perfect |
| F2 | 2D | 0.614 | 91.5% | Excellent |
| F5 | 4D | 3993 | 95.8% | Excellent |
| F8 | 8D | 9.760 | 98.0% | Excellent |
| F3 | 3D | -0.037 | - | Improving |
| F4 | 4D | 0.320 | 47.8% | Challenging |
| F6 | 5D | -0.674 | - | Difficult |
| F7 | 6D | 0.004 | 0.4% | Very difficult |

**Bottom line**: 4 out of 8 functions optimized successfully, using only 23 samples each.

---

## How It Works

The approach uses **Gaussian Process-based Bayesian Optimization**:

1. **Build a Model**: Use past experiments to create a probabilistic model of each function
2. **Smart Exploration**: Balance looking for new peaks vs. refining known good areas
3. **Adapt Per-Function**: Some functions are smooth (exploit), others are jagged (explore more)
4. **Learn from Failures**: When strategies fail, adjust—don't repeat mistakes

The math behind it:
```
UCB(x) = μ(x) + κ·σ(x)
```
- μ(x) = predicted value (go where things look good)
- κ·σ(x) = uncertainty bonus (explore the unknown)
- κ ranges from -0.5 (exploit) to +0.8 (explore aggressively)

---

## Quick Start

```bash
# Setup
pip install -r requirements.txt

# Run the main notebook
jupyter notebook notebooks/01_bo_ucb_week_runner.ipynb

# Or use Make commands
make install    # Install dependencies
make validate   # Check proposals before submitting
```

**📖 Full workflow guide**: See [docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md) for complete week-by-week instructions.

---

## Project Structure

```
├── README.md                   # You are here
├── DATASHEET.md               # Data documentation
├── MODEL_CARD.md              # Version history
├── CONTRIBUTING.md            # How to contribute
│
├── src/                       # Core code (11 modules)
│   ├── gp_model.py           # Gaussian Process
│   ├── acquisition.py        # UCB acquisition
│   ├── proposer.py           # Strategy logic
│   └── ...
│
├── scripts/                   # Utilities
│   ├── generate_week_overrides.py
│   └── validate_proposals.py
│
├── notebooks/                 # Main execution
│   └── 01_bo_ucb_week_runner.ipynb
│
├── initial_data/              # Starting samples
├── runs/                      # Weekly results (week_01 to week_13)
│
└── docs/                      # Extended documentation
    ├── DEVELOPER_GUIDE.md    # Technical details
    ├── PROJECT_STRUCTURE.md    # Week-by-week journey
    └── WEEKLY_PROGRESS.md        # Lessons learned
    └── HOW_TO_RUN.md 
```

---

## The Journey in Brief

**Weeks 1-3**: Started with uniform strategies across all functions. F2 hit its peak early (0.671) by luck, but most functions needed more sophisticated approaches.

**Weeks 4-7**: Learned that different functions need different strategies. Smooth functions (F5, F8) responded well to focused exploitation. Jagged ones (F7) needed persistent exploration. Week 7 brought a harsh lesson—F3 and F4 crashed hard when I tried to exploit too early.

**Weeks 8-10**: Built automated analysis tracking volatility and trends. Week 10 tested aggressive exploitation (κ=-0.7) near supposed peaks. Result: F3 and F4 crashed again, dropping over 70%. This was the most valuable failure—it showed that Gaussian Processes can get overconfident.

**Weeks 11-13**: Breakthrough! Hypothesized that gentler exploitation (κ=-0.3) would work better. F4 recovered spectacularly, jumping 310% to a NEW BEST of 0.669. F5 also hit NEW BEST 4166. The lesson: don't be greedy near peaks—maintain a wider search radius.

---

## Key Insights

### What Worked
- **Volatility-based strategies**: Smooth functions got tight trust regions, volatile ones got wide
- **Risk stratification**: High performers protected, strugglers gambled on
- **Hypothesis testing**: Treated failures as experiments, not accidents
- **Gentle exploitation**: κ=-0.3 beats κ=-0.7 near peaks

### What Failed
- **Dimension-based heuristics**: 6D F7 was harder than 8D F8 (smoothness matters more)
- **Premature celebration**: One good week ≠ convergence
- **Aggressive exploitation**: GP overconfidence missed nearby better solutions

### The Big Discovery
**Smoothness trumps dimensionality**. I expected 8-dimensional F8 to be hardest. Wrong. F8's smooth landscape made it easy to reach 98% optimal. Meanwhile, 6-dimensional F7's multi-modal terrain stayed frustratingly difficult. Coefficient of variation (volatility) predicted success far better than number of dimensions.

---

## Technical Details

**Algorithm**: GP-UCB (Gaussian Process Upper Confidence Bound)  
**Kernel**: ARD RBF (Automatic Relevance Determination)  
**Library**: scikit-learn (CPU-optimized, stable)  
**Candidate Generation**: 20k-45k per function per week  
**Validation**: Automated bounds checking, format verification

See `docs/DEVELOPER_GUIDE.md` for implementation details and `docs/WEEKLY_PROGRESS.md` for the full story with academic context.

---

## Requirements

- Python 3.9+
- NumPy, SciPy, scikit-learn
- pandas, matplotlib, seaborn
- Jupyter (for notebooks)

Full list in `requirements.txt`

---

## Documentation

- **[docs/WEEKLY_PROGRESS.md](docs/WEEKLY_PROGRESS.md)** - Complete week-by-week results and comparisons
- **[docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md)** - Complete week-by-week workflow guide
- **[docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Technical implementation details
- **[DATASHEET.md](DATASHEET.md)** - Complete data documentation
- **[MODEL_CARD.md](MODEL_CARD.md)** - Model specifications and limitations

---

## Contact

**Mrinmoy Mandal**  
Imperial College London | AI & ML Professional Certification

- 📧 Email: [mrinmoy838@gmail.com](mailto:mrinmoy838@gmail.com)
- 💼 LinkedIn: [linkedin.com/in/mrinmoy-mandal](https://www.linkedin.com/in/mrinmoy-mandal/)
- 🐙 GitHub: [github.com/mrinmoyece](https://github.com/mrinmoyece)

**Questions or feedback?** Open an [Issue](../../issues) or start a [Discussion](../../discussions).

---

## Citation

If you find this work useful for academic research:

```bibtex
@misc{mandal2026bbo,
  author = {Mandal, Mrinmoy},
  title = {Black-Box Optimization: Adaptive Bayesian Optimization with Gaussian Process Surrogates},
  year = {2026},
  institution = {Imperial College London},
  howpublished = {\url{https://github.com/mrinmoyece/aiml-capstone-project}}
}
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

*This project demonstrates that optimization isn't about perfect algorithms—it's about building systems that learn from mistakes and adapt their strategies based on evidence.*


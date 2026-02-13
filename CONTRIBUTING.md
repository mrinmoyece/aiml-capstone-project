# Contributing Guidelines

Thank you for your interest in this Black-Box Optimization Capstone project! While this is primarily an academic project, contributions and feedback are welcome.

---

## 🎯 Scope

This repository is:
- ✅ **Academic research project** (Imperial College London MSc)
- ✅ **Educational resource** for Bayesian Optimization
- ✅ **Open for feedback** and improvements
- ❌ Not actively seeking feature additions
- ❌ Not a production library (research code)

---

## 🤝 How to Contribute

### 1. **Report Issues**

If you find bugs, documentation errors, or have suggestions:

1. Check existing [Issues](../../issues)
2. Create a new issue with:
   - Clear title
   - Description of the problem
   - Steps to reproduce (if applicable)
   - Expected vs. actual behavior
   - Environment (Python version, OS)

### 2. **Suggest Improvements**

For enhancement suggestions:

- Open an issue with "Enhancement" label
- Describe the proposed improvement
- Explain the motivation/use case
- Discuss technical approach (optional)

### 3. **Submit Pull Requests**

If you'd like to contribute code:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/improvement`)
3. **Make** your changes following code style
4. **Test** your changes
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

---

## 📝 Code Style Guidelines

### Python Code

- **PEP 8** compliant
- **Black** formatter: `black src/ --line-length 88`
- **Type hints** where beneficial
- **Docstrings** for public functions:

```python
def ucb(gp, X_cands, kappa=2.0):
    """
    Compute Upper Confidence Bound acquisition scores.
    
    Args:
        gp: Fitted Gaussian Process model
        X_cands: Candidate points, shape (n_candidates, n_dims)
        kappa: Exploration weight (default: 2.0)
    
    Returns:
        scores: UCB values, shape (n_candidates,)
    """
    mu, sigma = gp.predict(X_cands, return_std=True)
    return mu + kappa * sigma
```

### Commit Messages

Follow conventional commits:

```
feat: Add emergency exploration mode
fix: Correct trust region calculation for boundary cases
docs: Update README with Week 11 results
refactor: Simplify candidate generation logic
test: Add validation for overrides.csv format
```

### Documentation

- **Markdown** for all documentation
- Clear section headers
- Code examples where helpful
- Keep under 80-100 character line width

---

## 🧪 Testing

Before submitting:

```bash
# Run validation tests
python scripts/sanity_check.py
python scripts/validate_proposals.py --week 11
python scripts/validate_overrides.py --week 11

# Or use Makefile
make test
```

---

## 📊 Areas Open for Contribution

### Documentation
- ✅ Clarifications or additional examples
- ✅ Typo fixes
- ✅ Translation to other languages
- ✅ Tutorial notebooks

### Code Quality
- ✅ Bug fixes
- ✅ Performance optimizations
- ✅ Code refactoring (maintain functionality)
- ✅ Additional validation checks

### Analysis Tools
- ✅ New visualization functions
- ✅ Statistical analysis utilities
- ✅ Reporting enhancements

### NOT Seeking
- ❌ Major architectural changes
- ❌ New optimization algorithms (project scope)
- ❌ Alternative ML libraries (scikit-learn required)

---

## 🔍 Code Review Process

1. **Automated Checks**: CI runs validation (if configured)
2. **Manual Review**: Maintainer reviews code quality
3. **Testing**: Verify changes don't break existing functionality
4. **Merge**: Approved PRs merged to main branch

---

## 📧 Communication

- **Issues**: Primary communication channel
- **Pull Requests**: For code contributions
- **Discussions**: For general questions or ideas

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Acknowledgments

Contributors will be acknowledged in:
- `CONTRIBUTORS.md` (if created)
- Commit history
- Release notes (if applicable)

---

## ❓ Questions?

If you're unsure about anything:

1. Check existing documentation in `docs/`
2. Review closed issues for similar questions
3. Open a new issue with your question

---

**Thank you for helping improve this project!** 🎓


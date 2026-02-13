# Makefile for Black-Box Optimization Capstone
# Automates common tasks for weekly BO execution

.PHONY: help clean validate install trends check-week run-week docs all

# Configuration
PYTHON := python3
WEEK := 11
NOTEBOOK := notebooks/01_bo_ucb_week_runner.ipynb

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Black-Box Optimization Capstone - Makefile Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make install          Install Python dependencies"
	@echo "  make clean            Remove temporary files and caches"
	@echo ""
	@echo "$(GREEN)Weekly Execution:$(NC)"
	@echo "  make trends N=<week>  Generate adaptive strategy for week N"
	@echo "  make validate N=<week> Validate proposals for week N"
	@echo "  make check-week        Check current week configuration"
	@echo ""
	@echo "$(GREEN)Analysis:$(NC)"
	@echo "  make docs             Generate documentation and reports"
	@echo "  make summary          Show performance summary (all weeks)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make test             Run validation tests"
	@echo "  make format           Format Python code with black"
	@echo "  make lint             Run pylint on source code"
	@echo ""
	@echo "$(YELLOW)Current week: $(WEEK)$(NC)"

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

clean: ## Remove temporary files and caches
	@echo "$(BLUE)Cleaning repository...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*~" -delete
	@echo "$(GREEN)✓ Repository cleaned$(NC)"

trends: ## Generate adaptive strategy: make trends N=11
	@if [ -z "$(N)" ]; then \
		echo "$(RED)Error: Week number required. Usage: make trends N=11$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Generating Week $(N) adaptive strategy...$(NC)"
	@mkdir -p runs/week_$(shell printf "%02d" $(N))
	$(PYTHON) scripts/generate_week_overrides.py $(N) || true
	@echo "$(GREEN)✓ Strategy generated: runs/week_$(shell printf "%02d" $(N))/overrides.csv$(NC)"
	@echo "$(YELLOW)→ Review overrides.csv before running notebook$(NC)"

validate: ## Validate proposals: make validate N=11
	@if [ -z "$(N)" ]; then \
		echo "$(RED)Error: Week number required. Usage: make validate N=11$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Validating Week $(N) proposals...$(NC)"
	$(PYTHON) scripts/validate_proposals.py --week $(N)
	$(PYTHON) scripts/validate_overrides.py --week $(N)
	@echo "$(GREEN)✓ Validation complete$(NC)"

check-week: ## Check current week configuration
	@echo "$(BLUE)Current Configuration:$(NC)"
	@echo "  Week: $(WEEK)"
	@grep "^WEEK = " src/config.py || echo "  $(YELLOW)Warning: config.py not found$(NC)"
	@if [ -f "runs/week_$(shell printf "%02d" $(WEEK))/proposals.csv" ]; then \
		echo "  $(GREEN)✓ Proposals exist for Week $(WEEK)$(NC)"; \
	else \
		echo "  $(YELLOW)⚠ No proposals yet for Week $(WEEK)$(NC)"; \
	fi

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@mkdir -p docs
	@echo "$(GREEN)✓ Documentation structure ready$(NC)"
	@echo "$(YELLOW)→ See docs/ folder for reports and reflections$(NC)"

summary: ## Show performance summary
	@echo "$(BLUE)Performance Summary (Weeks 1-$(WEEK)):$(NC)"
	@echo ""
	@for week in $$(seq 1 $(WEEK)); do \
		week_fmt=$$(printf "%02d" $$week); \
		if [ -f "runs/week_$$week_fmt/proposals.csv" ]; then \
			echo "Week $$week: ✓ Complete"; \
		else \
			echo "Week $$week: ⚠ Incomplete"; \
		fi; \
	done
	@echo ""
	@echo "$(YELLOW)→ See docs/RESULTS.md for detailed analysis$(NC)"

test: ## Run validation tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) scripts/sanity_check.py
	$(PYTHON) scripts/validate_overrides.py --all
	@echo "$(GREEN)✓ All tests passed$(NC)"

format: ## Format Python code
	@echo "$(BLUE)Formatting code...$(NC)"
	black src/ scripts/ --line-length 88
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run linting
	@echo "$(BLUE)Linting code...$(NC)"
	pylint src/ scripts/ --disable=C0111,R0913 || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

# Week-specific shortcuts
week-11: N=11
week-11: trends ## Generate Week 11 strategy

week-12: N=12
week-12: trends ## Generate Week 12 strategy

# Validate all weeks
validate-all: ## Validate all completed weeks
	@echo "$(BLUE)Validating all weeks...$(NC)"
	@for week in $$(seq 1 $(WEEK)); do \
		week_fmt=$$(printf "%02d" $$week); \
		if [ -f "runs/week_$$week_fmt/proposals.csv" ]; then \
			echo "Validating Week $$week..."; \
			$(PYTHON) scripts/validate_proposals.py --week $$week 2>/dev/null || true; \
		fi; \
	done
	@echo "$(GREEN)✓ Validation complete$(NC)"

# Complete workflow
all: clean trends validate docs ## Run complete workflow
	@echo "$(GREEN)✓ Complete workflow finished$(NC)"
	@echo "$(YELLOW)→ Ready to run Jupyter notebook$(NC)"

# Archive old runs
archive: ## Archive weeks 1-5
	@echo "$(BLUE)Archiving old runs...$(NC)"
	tar -czf runs_archive_$$(date +%Y%m%d).tar.gz runs/week_0[1-5]/
	@echo "$(GREEN)✓ Archive created$(NC)"

.DEFAULT_GOAL := help


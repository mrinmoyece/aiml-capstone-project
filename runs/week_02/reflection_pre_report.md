# Week 02 Reflection — Pre-Results

## Method / Principle
- **Method:** gp_ucb_week2
- Phase: **early**, κ is higher to bias exploration into uncertain regions.
- Acquisition: **UCB = μ + κ·σ**; early weeks bias exploration; near-tie candidates use a **diversity (max-min distance)** rule.

## Function-by-function (current proposal rationale)
- **function_1** — query leaned **exploration** (μ≈-0.0010, σ≈0.0022, κ·σ ratio≈0.85)
  - x: `0.051347-0.919882`
  
  ![](plots/function_1_report.png)
- **function_2** — query leaned **exploration** (μ≈0.2521, σ≈0.2253, κ·σ ratio≈0.68)
  - x: `0.104600-0.962268`
  
  ![](plots/function_2_report.png)
- **function_3** — query leaned **exploration** (μ≈-0.0720, σ≈0.0866, κ·σ ratio≈0.74)
  - x: `0.999076-0.927113-0.985076`
  
  ![](plots/function_3_report.png)
- **function_4** — query leaned **exploration** (μ≈-2.0553, σ≈1.2792, κ·σ ratio≈0.65)
  - x: `0.477097-0.434448-0.136061-0.471890`
  
  ![](plots/function_4_report.png)
- **function_5** — query leaned **exploration** (μ≈194.6156, σ≈308.2359, κ·σ ratio≈0.82)
  - x: `0.861962-0.856128-0.933518-0.866172`
  
  ![](plots/function_5_report.png)
- **function_6** — query leaned **exploration** (μ≈-0.8068, σ≈0.3614, κ·σ ratio≈0.57)
  - x: `0.450600-0.291765-0.538896-0.991996-0.106024`
  
  ![](plots/function_6_report.png)
- **function_7** — query leaned **exploitation** (μ≈1.2001, σ≈0.1981, κ·σ ratio≈0.34)
  - x: `0.112911-0.267073-0.640314-0.482888-0.421507-0.790965`
  
  ![](plots/function_7_report.png)
- **function_8** — query leaned **exploitation** (μ≈10.2683, σ≈0.1061, κ·σ ratio≈0.03)
  - x: `0.141204-0.061199-0.050907-0.027400-0.808719-0.437583-0.249977-0.080856`
  
  ![](plots/function_8_report.png)

## Challenging functions & info gaps
- Higher-dimensional functions (d ≥ 5): 6, 7, 8 — hardest due to sparse coverage and possible anisotropy.
- Helpful info: approximate noise levels/replicates, domain constraints, tighter feature bounds if known.

## Plan for the next round
- Keep κ moderately high; expand candidate pool in sparse/uncertain functions.
- Maintain near-tie diversity to avoid redundant sampling.

*Auto-generated on 2025-10-19 22:59 UTC*
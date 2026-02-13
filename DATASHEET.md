# Datasheet for Black-Box Optimization Dataset

## Motivation

**For what purpose was the dataset created?**  
This dataset came from a 13-week optimization challenge where I had to maximize 8 unknown functions using as few tests as possible. Think of it like drug discovery—each test is expensive (time, money, resources), so you can't afford to try random combinations. The challenge simulates these real-world constraints.

**Who created the dataset and on behalf of which entity?**  
Imperial College London's AI & ML program gave me 10 initial data points per function to start. I generated the remaining 13 queries per function using my Gaussian Process optimization algorithm over the course of the challenge.

**Who funded the creation of the dataset?**  
Imperial College London, as part of the AI & ML MSc Capstone Project.

## Composition

**What do the instances that comprise the dataset represent?**  
Each data point is a test-result pair:
- **Input (x)**: A point in d-dimensional space, where each coordinate is between 0 and 1, and d ranges from 2 to 8 depending on the function
- **Output (y)**: What the function returned for that input
- **Metadata**: Which function (1-8) and which week (1-13)

**How many instances of each type are there?**  
- Starting data: 10 points per function × 8 functions = 80 points
- My queries: 13 weeks × 8 functions = 104 points  
- **Total: 184 data points** (23 per function)

**Is there any missing data?**  
No. Every query I submitted got a valid response. No nulls, no missing values.

**Does the dataset contain data that might be considered confidential?**  
No. It's all synthetic math—no real people, organizations, or sensitive information involved. Just function inputs and outputs.

## Collection Process

**How was the data acquired?**  
Two phases:
1. **Starting points (80 total)**: The course gave me these using Latin Hypercube Sampling—basically a way to spread points evenly across the search space
2. **My queries (104 total)**: Each week I:
   - Trained a Gaussian Process on all data so far
   - Used UCB acquisition to pick the most promising next point
   - Submitted it and waited a week for the result

**If the data is a sample of a larger subset, what was the sampling strategy?**  
This is an incredibly sparse sample of an infinite space. Imagine 23 drops of water in an ocean. The strategy was:
- **Initial**: Latin Hypercube (spread things out evenly)
- **My additions**: Bayesian Optimization (focus on areas that look promising)

**Over what timeframe was the data collected?**  
October 2025 - January 2026 (13 weeks)  
One query per function per week, with a week turnaround each time.

## Preprocessing/Cleaning/Labelling

**Was any preprocessing/cleaning/labeling of the data done?**  
Very little:
- **Inputs**: Already normalized to [0,1] by design—no work needed
- **Outputs**: Stored exactly as received, no transformations
- **Labels**: Tagged each point with function number and week
- **That's it**: No fancy feature engineering or data massage

**Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?**  
Yes. Everything is in `initial_data/function_X/` as NumPy files:
- `initial_inputs.npy`: The x coordinates
- `initial_outputs.npy`: The y values
Weekly stuff is also saved in `runs/week_XX/proposals.csv`

## Uses

**What other tasks could the dataset be used for?**  
- **Testing different optimization algorithms**: Try Expected Improvement, Thompson Sampling, or other methods against my GP-UCB results
- **Meta-learning**: See if you can learn patterns that transfer across different function types
- **Sensitivity analysis**: Play with hyperparameters and see what breaks
- **Model comparison**: Test different kernels or even non-GP surrogates like Random Forests

**Is there anything about the composition or collection that might impact future uses?**  
Yes, a few things to watch out for:
- **Not independent samples**: Each query depends on previous ones (classic Bayesian Optimization property)
- **Only 23 points per function**: Way too small for neural networks or anything data-hungry
- **Unknown true functions**: I never learned what the actual functions were, so can't verify true optima
- **Sampling bias**: Points cluster near good regions, not spread uniformly

If you use this data:
- Stick to methods that work with small sequential data (GPs, trees)
- Don't claim you found the global optimum (can't verify)
- Think of it as an optimization path, not a random sample

**Are there tasks for which the dataset should not be used?**  
- **High dimensions**: Only goes up to 8D
- **Deep learning**: Need 1000+ samples for that
- **Proving global optimality**: Can't do it without ground truth
- **Methods assuming independence**: The sequential nature violates that assumption

## Distribution

**How has the dataset already been distributed?**  
It's on GitHub, publicly available:
- NumPy arrays in `initial_data/function_X/`
- CSV files in `runs/week_XX/proposals.csv`
- MIT License (see below)

**Is it subject to any copyright or other IP license?**  
Yes—**MIT License**. You can:
- Use it for anything (academic, commercial, whatever)
- Modify it
- Share it
- Just give credit where it's due

## Maintenance

**Who maintains the dataset?**  
Me (Mrinmoy, Imperial College London)

The challenge is done—13 weeks complete. This dataset won't change. It's here for reproducibility and anyone who wants to learn from it or test their own methods.

**Contact**: Open a GitHub Issue if you have questions


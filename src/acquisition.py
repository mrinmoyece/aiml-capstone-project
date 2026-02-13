
import numpy as np
from sklearn.metrics import pairwise_distances

def kappa_schedule(d: int, week: int) -> float:
    week = max(1, min(13, int(week)))
    if d <= 3: start, end = 2.5, 1.8
    elif d <= 5: start, end = 3.0, 2.4
    else: start, end = 3.2, 2.8
    t = (week - 1) / 12.0
    print("base kappa for dimension:", d,  start + (end - start) * t)
    return float(start + (end - start) * t)

def tr_halfwidth(week: int) -> float:
    week = max(1, min(13, int(week)))
    start, end = 0.18, 0.08
    t = (week - 1) / 12.0
    return float(start + (end - start) * t)

def diversity_tiebreak(cands: np.ndarray, X_hist: np.ndarray, idxs: np.ndarray) -> int:
    D = pairwise_distances(cands[idxs], X_hist)
    return int(idxs[int(np.argmax(D.min(axis=1)))])

def ensure_min_distance(x_star: np.ndarray, X_hist: np.ndarray, eps: float = None) -> np.ndarray:
    d = X_hist.shape[1] if X_hist.ndim == 2 else len(x_star)
    if eps is None: eps = 0.01 * np.sqrt(d)
    if X_hist.size == 0: return np.clip(x_star, 0.0, 1.0)
    dists = np.linalg.norm(X_hist - x_star.reshape(1, -1), axis=1)
    if np.min(dists) >= eps: return np.clip(x_star, 0.0, 1.0)
    rng = np.random.default_rng(1234567)
    for _ in range(100):
        x_try = x_star + rng.normal(scale=eps/4.0, size=d)
        x_try = np.clip(x_try, 0.0, 1.0)
        dists = np.linalg.norm(X_hist - x_try.reshape(1, -1), axis=1)
        if np.min(dists) >= eps: return x_try
    return np.clip(x_star, 0.0, 1.0)

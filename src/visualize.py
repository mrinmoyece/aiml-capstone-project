
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .config import INITIAL_DATA_ROOT, PLOT_DPI
from .data_io import load_xy

def plot_function_snapshot(func_id: int, save_dir: Path | None = None):
    fdir = INITIAL_DATA_ROOT / f"function_{func_id}"
    if not fdir.exists(): return
    X, y = load_xy(fdir)
    plt.figure(figsize=(5,4))
    if X.shape[1] == 1:
        plt.scatter(X[:,0], y); plt.xlabel("x1"); plt.ylabel("y")
    elif X.shape[1] == 2:
        sc = plt.scatter(X[:,0], X[:,1], c=y); cbar = plt.colorbar(sc); cbar.set_label("y")
        plt.xlabel("x1"); plt.ylabel("x2")
    else:
        plt.plot(y, "o"); plt.xlabel("sample"); plt.ylabel("y")
    plt.title(f"function_{func_id} ({X.shape[1]}D) — n={len(y)}"); plt.tight_layout()
    if save_dir:
        out = save_dir / f"function_{func_id}_snapshot.png"; plt.savefig(out, dpi=PLOT_DPI)
    plt.close()


def plot_pca_scatter(func_id: int, save_dir: Path | None = None):
    from sklearn.decomposition import PCA
    fdir = INITIAL_DATA_ROOT / f"function_{func_id}"
    if not fdir.exists(): return
    X, y = load_xy(fdir)
    d = X.shape[1]
    if d < 3:
        return
    pca = PCA(n_components=2, random_state=0).fit(X)
    Z = pca.transform(X)
    plt.figure(figsize=(5,4))
    sc = plt.scatter(Z[:,0], Z[:,1], c=y)
    plt.colorbar(sc, label="y")
    plt.xlabel("PC1"); plt.ylabel("PC2"); plt.title(f"function_{func_id}: PCA(2D) — n={len(y)}")
    plt.tight_layout()
    if save_dir:
        out = save_dir / f"function_{func_id}_pca2.png"
        plt.savefig(out, dpi=PLOT_DPI)
    plt.close()

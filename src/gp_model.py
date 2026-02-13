import warnings
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as Ck

# Suppress GP convergence warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn.gaussian_process')


def fit_gp(X, y):
    d = X.shape[1]
    kernel = Ck(1.0, (1e-3, 1e3)) * RBF(
        length_scale=np.ones(d),
        length_scale_bounds=(1e-3, 50.0)
    ) + WhiteKernel(
        noise_level=1e-5,
        noise_level_bounds=(1e-10, 1.0)
    )
    gp = GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        n_restarts_optimizer=3,
        random_state=0
    )
    gp.fit(X, y)
    return gp


def bounds_from_data(X):
    lo = X.min(axis=0)
    hi = X.max(axis=0)
    return lo, hi

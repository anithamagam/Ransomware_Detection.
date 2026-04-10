"""Numerosity balancing utilities.

Imbalanced-learn imports are performed inside functions so the module can be
imported even when `imblearn` is not installed. Each function falls back to a
pure NumPy/scikit-learn implementation if `imblearn` is missing or
incompatible.
"""

from collections import Counter
import numpy as np
from sklearn.utils import resample


def random_undersampling(x, y):
    """Perform random undersampling.

    Tries `imblearn.under_sampling.RandomUnderSampler` when available and falls
    back to reducing each class to the size of the smallest class.
    """
    try:
        from imblearn.under_sampling import RandomUnderSampler

        x_res, y_res = RandomUnderSampler(random_state=42).fit_resample(x, y)
        return x_res, y_res
    except Exception:
        y = np.asarray(y)
        x = np.asarray(x)
        counts = Counter(y)
        min_count = min(counts.values())
        indices = []
        for cls in counts:
            cls_idx = np.where(y == cls)[0]
            if len(cls_idx) > min_count:
                chosen = resample(
                    cls_idx, replace=False, n_samples=min_count, random_state=42
                )
            else:
                chosen = cls_idx
            indices.extend(chosen.tolist())
        indices = np.array(indices)
        return x[indices], y[indices]


def random_oversampling(x, y):
    """Perform random oversampling.

    Tries `imblearn.over_sampling.RandomOverSampler` when available and falls
    back to upsampling minority classes with replacement to the majority size.
    """
    try:
        from imblearn.over_sampling import RandomOverSampler

        x_res, y_res = RandomOverSampler(random_state=42).fit_resample(x, y)
        return x_res, y_res
    except Exception:
        y = np.asarray(y)
        x = np.asarray(x)
        counts = Counter(y)
        max_count = max(counts.values())
        indices = []
        for cls in counts:
            cls_idx = np.where(y == cls)[0]
            if len(cls_idx) < max_count:
                chosen = resample(
                    cls_idx, replace=True, n_samples=max_count, random_state=42
                )
            else:
                chosen = cls_idx
            indices.extend(chosen.tolist())
        indices = np.array(indices)
        return x[indices], y[indices]


def smote(x, y):
    """Perform SMOTE oversampling.

    If `imblearn` is unavailable or incompatible, falls back to
    ``random_oversampling`` as a degraded alternative.
    """
    try:
        from imblearn.over_sampling import SMOTE

        x_res, y_res = SMOTE(sampling_strategy="minority", random_state=42).fit_resample(
            x, y
        )
        return x_res, y_res
    except Exception:
        return random_oversampling(x, y)

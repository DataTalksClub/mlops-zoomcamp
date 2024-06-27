"""Cramer-Von-mises test of two samples.

Name: "cramer_von_mises"

Import:

    >>> from evidently.calculations.stattests import cramer_von_mises

Properties:
- only for numerical features
- returns p-value

Example:
    Using by object:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> from evidently.calculations.stattests import cramer_von_mises
    >>> options = DataDriftOptions(all_features_stattest=cramer_von_mises)

    Using by name:

    >>> from evidently.options.data_drift import DataDriftOptions
    >>> options = DataDriftOptions(all_features_stattest="cramer_von_mises")
"""

import math
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.special import gammaln
from scipy.special import kv
from scipy.stats import rankdata

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType


class CramerVonMisesResult:
    def __init__(self, statistic, pvalue):
        self.statistic = statistic
        self.pvalue = pvalue

    def __repr__(self):
        return f"{self.__class__.__name__}(statistic={self.statistic}, " f"pvalue={self.pvalue})"


def _pval_cvm_2samp_exact(s, m, n):
    """
    Compute the exact p-value of the Cramer-von Mises two-sample test
    for a given value s of the test statistic.
    m and n are the sizes of the samples.
    [1] Y. Xiao, A. Gordon, and A. Yakovlev, "A C++ Program for
        the Cramér-Von Mises Two-Sample Test", J. Stat. Soft.,
        vol. 17, no. 8, pp. 1-15, Dec. 2006.
    [2] T. W. Anderson "On the Distribution of the Two-Sample Cramer-von Mises
        Criterion," The Annals of Mathematical Statistics, Ann. Math. Statist.
        33(3), 1148-1159, (September, 1962)
    """

    # [1, p. 3]
    lcm = np.lcm(m, n)
    # [1, p. 4], below eq. 3
    a = lcm // m
    b = lcm // n
    # Combine Eq. 9 in [2] with Eq. 2 in [1] and solve for $\zeta$
    # Hint: `s` is $U$ in [2], and $T_2$ in [1] is $T$ in [2]
    mn = m * n
    zeta = lcm**2 * (m + n) * (6 * s - mn * (4 * mn - 1)) // (6 * mn**2)

    # bound maximum value that may appear in `gs` (remember both rows!)
    zeta_bound = lcm**2 * (m + n)  # bound elements in row 1
    combinations = math.factorial(m + n) / (math.factorial(m) * math.factorial(n))
    max_gs = max(zeta_bound, combinations)
    dtype = np.min_scalar_type(max_gs)

    # the frequency table of $g_{u, v}^+$ defined in [1, p. 6]
    gs = [np.array([[0], [1]], dtype=dtype)] + [np.empty((2, 0), dtype=dtype) for _ in range(m)]
    for u in range(n + 1):
        next_gs = []
        tmp = np.empty((2, 0), dtype=dtype)
        for v, g in enumerate(gs):
            # Calculate g recursively with eq. 11 in [1]. Even though it
            # doesn't look like it, this also does 12/13 (all of Algorithm 1).
            vi, i0, i1 = np.intersect1d(tmp[0], g[0], return_indices=True)
            tmp = np.concatenate([np.stack([vi, tmp[1, i0] + g[1, i1]]), np.delete(tmp, i0, 1), np.delete(g, i1, 1)], 1)
            tmp[0] += (a * v - b * u) ** 2
            next_gs.append(tmp)
        gs = next_gs
    value, freq = gs[m]
    return np.float64(np.sum(freq[value >= zeta]) / combinations)


def _cdf_cvm_inf(x):
    """
    Calculate the cdf of the Cramér-von Mises statistic (infinite sample size).
    See equation 1.2 in Csörgő, S. and Faraway, J. (1996).
    Implementation based on MAPLE code of Julian Faraway and R code of the
    function pCvM in the package goftest (v1.1.1), permission granted
    by Adrian Baddeley. Main difference in the implementation: the code
    here keeps adding terms of the series until the terms are small enough.
    The function is not expected to be accurate for large values of x, say
    x > 4, when the cdf is very close to 1.
    """
    x = np.asarray(x)

    def term(x, k):
        # this expression can be found in [2], second line of (1.3)
        u = np.exp(gammaln(k + 0.5) - gammaln(k + 1)) / (np.pi**1.5 * np.sqrt(x))
        y = 4 * k + 1
        q = y**2 / (16 * x)
        b = kv(0.25, q)
        return u * np.sqrt(y) * np.exp(-q) * b

    tot = np.zeros_like(x, dtype="float")
    cond = np.ones_like(x, dtype="bool")
    k = 0
    while np.any(cond):
        z = term(x[cond], k)
        tot[cond] = tot[cond] + z
        cond[cond] = np.abs(z) >= 1e-7
        k += 1

    return tot


def _cvm_2samp(x: np.ndarray, y: np.ndarray, method: str = "auto") -> CramerVonMisesResult:
    """Perform the two-sample Cramér-von Mises test
    Args:
        x : array_like
        y : array_like
        method : {'auto', 'asymptotic', 'exact'}, optional
    Returns:
        res : object with attributes
        statistic : Cramér-von Mises statistic.
        pvalue : float
    """
    xa = np.sort(np.asarray(x))
    ya = np.sort(np.asarray(y))

    if xa.size <= 1 or ya.size <= 1:
        raise ValueError("x and y must contain at least two observations.")
    if xa.ndim > 1 or ya.ndim > 1:
        raise ValueError("The samples must be one-dimensional.")
    if method not in ["auto", "exact", "asymptotic"]:
        raise ValueError("method must be either auto, exact or asymptotic.")

    nx = len(xa)
    ny = len(ya)

    if method == "auto":
        if max(nx, ny) > 20:
            method = "asymptotic"
        else:
            method = "exact"

    # get ranks of x and y in the pooled sample
    z = np.concatenate([xa, ya])
    # in case of ties, use midrank (see [1])
    r = rankdata(z, method="average")
    rx = r[:nx]
    ry = r[nx:]

    # compute U (eq. 10 in [2])
    u = nx * np.sum((rx - np.arange(1, nx + 1)) ** 2)
    u += ny * np.sum((ry - np.arange(1, ny + 1)) ** 2)

    # compute T (eq. 9 in [2])
    k, N = nx * ny, nx + ny
    t = u / (k * N) - (4 * k - 1) / (6 * N)

    if method == "exact":
        p = _pval_cvm_2samp_exact(u, nx, ny)
    else:
        # compute expected value and variance of T (eq. 11 and 14 in [2])
        et = (1 + 1 / N) / 6
        vt = (N + 1.0) * (4 * k * N - 3 * (nx**2 + ny**2) - 2 * k)
        vt = vt / (45 * N**2 * 4 * k)

        # computed the normalized statistic (eq. 15 in [2])
        tn = 1 / 6 + (t - et) / np.sqrt(45 * vt)

        # approximate distribution of tn with limiting distribution
        # of the one-sample test statistic
        # if tn < 0.003, the _cdf_cvm_inf(tn) < 1.28*1e-18, return 1.0 directly
        if tn < 0.003:
            p = 1.0
        else:
            p = max(0, 1.0 - _cdf_cvm_inf(tn))

    return CramerVonMisesResult(statistic=t, pvalue=p)


def _cramer_von_mises(
    reference_data: pd.Series,
    current_data: pd.Series,
    feature_type: ColumnType,
    threshold: float,
) -> Tuple[float, bool]:
    """Run the two-sample Cramer-Von-mises test of two samples.
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: level of significance
    Returns:
        p_value: p-value
        test_result: whether the drift is detected
    """
    res = _cvm_2samp(reference_data.values, current_data.values)
    return res.pvalue, res.pvalue <= threshold


cramer_von_mises = StatTest(
    name="cramer_von_mises",
    display_name="Cramer-von Mises",
    allowed_feature_types=[ColumnType.Numerical],
    default_threshold=0.1,
)

register_stattest(cramer_von_mises, default_impl=_cramer_von_mises)

from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd

from evidently.calculations.stattests.registry import StatTest
from evidently.calculations.stattests.registry import register_stattest
from evidently.core import ColumnType


def squared_paired_dist(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Calculates the squared euclidean pairwise distance
    Args:
        x:reference data
        y:current data
    Returns:
        dist: squared euclidean pairwise distance between x and y
    """
    dotx = x**2
    doty = y**2
    dist = doty.T - 2 * np.dot(x, y.T) + dotx
    return dist


def sigma_median(dist: np.ndarray) -> float:
    """Calculate the median sigma
    Args:
        dist: pairwise distance result
    Returns:
        sigma: the median sigma
    """
    sigma = (
        0.5
        * np.percentile(
            # error: No overload variant of "percentile" matches argument types
            # "ndarray[Any, Any]", "int", "str"  [call-overload]
            a=dist.flatten(),
            q=50,
            interpolation="nearest",  # type: ignore[call-overload]
        )
    ) ** 0.5
    if sigma == 0:
        return (0.5 * 1) ** 0.5
    return sigma


def rbf(x: np.ndarray, y: np.ndarray, pass_sigma: Optional[float]) -> Tuple[np.ndarray, float]:
    """compute the RBF kernel
    Args:
        x:reference data
        y:current data
        pass_sigma: override median sigma calculation (i.e provide custom sigma value)
    Returns:
        kernel: the computed kernel between reference and current
    """
    dist = squared_paired_dist(x, y)
    sigma = sigma_median(dist)
    if pass_sigma:
        sigma = pass_sigma
    gamma = 1.0 / (2.0 * sigma**2)
    return np.exp(-gamma * dist), sigma


def kernel_matrix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute the kernel matrices(i.e. xx, xy and yy)
    Args:
        x: reference data
        y: current data
    Returns:
        kernel_matrix: the concatenated kernel matrix
    """
    kxx, kxxsigma = rbf(x, x, pass_sigma=None)
    kxy, tmp = rbf(x, y, pass_sigma=kxxsigma)
    kyy, tmp = rbf(y, y, pass_sigma=kxxsigma)
    kernel_matrix = np.concatenate((np.concatenate((kxx, kxy), axis=1), np.concatenate((kxy.T, kyy), axis=1)), axis=0)
    return kernel_matrix


def mmd_2samp(kernel_matrix: np.ndarray, no_y_values: int, permute: bool = False) -> float:
    """Perform the mmd test without permutation
    Args:
        kernel_matrix: the concatenated similarity matrix(i.e. xx,xy and yy)
        no_y_values: number of values in y
        permute: whether to shuffle the kernel matrix or not
    Returns:
        mmd: mmd distance without permutation
    """
    no_x_values = kernel_matrix.shape[0] - no_y_values
    if permute:
        index = np.random.permutation(kernel_matrix.shape[0])
        kernel_matrix = kernel_matrix[index][:, index]

    Kxx = kernel_matrix[:-no_y_values, :-no_y_values]
    Kyy = kernel_matrix[-no_y_values:, -no_y_values:]
    Kxy = kernel_matrix[-no_y_values:, :-no_y_values]
    A = 1 / (no_x_values * (no_x_values - 1))
    B = 1 / (no_y_values * (no_y_values - 1))
    mmd = A * Kxx.sum() + B * Kyy.sum() - 2.0 * Kxy.mean()
    return mmd


def mmd_pval(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """Run the mmd test with permutations
    Args:
        x:reference data as numpy array
        y:current data as numpy array
    Returns:
        p_value:p_value
        mmd:mmd distance between x and y
    """
    kernel_mat = kernel_matrix(x, y)
    kernel_mat = kernel_mat - np.diag(np.diagonal(kernel_mat))

    mmd = mmd_2samp(kernel_mat, y.shape[0], permute=False)
    mmd_permuted = np.array([mmd_2samp(kernel_mat, y.shape[0], permute=True) for _ in range(100)])

    p_val = (mmd <= mmd_permuted).mean()

    return p_val, mmd


def _mmd_stattest(
    reference_data: pd.Series,
    current_data: pd.Series,
    feature_type: ColumnType,
    threshold: float,
) -> Tuple[float, bool]:
    """Run the  emperical maximum mean discrepancy test.
    Args:
        reference_data: reference data
        current_data: current data
        feature_type: feature type
        threshold: level of significance
    Returns:
        p_value: p-value
        test_result: whether the drift is detected
    """
    reference_data = reference_data.values.reshape(-1, 1)
    current_data = current_data.values.reshape(-1, 1)

    p_value, mmd = mmd_pval(reference_data, current_data)

    return p_value, p_value < threshold


emperical_mmd = StatTest(
    name="emperical_mmd",
    display_name="emperical_mmd",
    allowed_feature_types=[ColumnType.Numerical],
    default_threshold=0.1,
)

register_stattest(emperical_mmd, _mmd_stattest)

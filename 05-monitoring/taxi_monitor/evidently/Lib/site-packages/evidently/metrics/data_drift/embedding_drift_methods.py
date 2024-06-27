import abc
from typing import Callable
from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.spatial.distance import chebyshev
from scipy.spatial.distance import cityblock
from scipy.spatial.distance import cosine
from scipy.spatial.distance import euclidean
from sklearn.decomposition import PCA
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import pairwise_distances
from sklearn.metrics import pairwise_kernels
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from evidently.calculations.stattests import get_stattest
from evidently.core import ColumnType
from evidently.pydantic_utils import EvidentlyBaseModel

DISTANCE_DICT = {
    "euclidean": euclidean,
    "cosine": cosine,
    "cityblock": cityblock,
    "chebyshev": chebyshev,
}
N_BOOTSTRAP = 100


def get_pca_df(
    reference_emb: pd.DataFrame, current_emb: pd.DataFrame, n_comp: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Takes two dataframes and reduces their dimensionality using the PCA method
    Args:
        reference_emb: reference embeddings data
        current_emb: current embeddings data
        n_comp: number of components to keep
    Returns:
        reference_emb_new: transformed reference_emb
        current_emb_new: transformed current_emb
    """
    pca = PCA(n_components=n_comp, random_state=0)
    return pd.DataFrame(pca.fit_transform(reference_emb)), pd.DataFrame(pca.transform(current_emb))


class DriftMethod(EvidentlyBaseModel):
    @abc.abstractmethod
    def __call__(self, current_emb: pd.DataFrame, reference_emb: pd.DataFrame) -> Tuple[float, bool, str]:
        raise NotImplementedError


class DistanceDriftMethod(DriftMethod):
    dist: str = "euclidean"
    threshold: float = 0.2
    bootstrap: Optional[bool] = None
    quantile_probability: float = 0.95
    pca_components: Optional[int] = None

    def __call__(self, current_emb: pd.DataFrame, reference_emb: pd.DataFrame) -> Tuple[float, bool, str]:
        if self.pca_components:
            reference_emb, current_emb = get_pca_df(reference_emb, current_emb, self.pca_components)
        res = DISTANCE_DICT[self.dist](reference_emb.mean(axis=0), current_emb.mean(axis=0))
        if self.bootstrap:
            bstrp_res = []
            b_ref_size = int(reference_emb.shape[0] ** 2 / (reference_emb.shape[0] + current_emb.shape[0]))
            b_curr_size = int(
                current_emb.shape[0] * reference_emb.shape[0] / (reference_emb.shape[0] + current_emb.shape[0])
            )
            for i in range(N_BOOTSTRAP):
                np.random.seed(i)
                b_ref_idx = np.random.choice(reference_emb.shape[0], b_ref_size)
                b_curr_idx = np.random.choice(reference_emb.shape[0], b_curr_size)
                bstrp_res.append(
                    DISTANCE_DICT[self.dist](
                        reference_emb.iloc[b_ref_idx, :].mean(axis=0), reference_emb.iloc[b_curr_idx, :].mean(axis=0)
                    )
                )
            perc = np.percentile(bstrp_res, 100 * self.quantile_probability)
            return res, res > perc, "distance"
        return res, res > self.threshold, "distance"


def distance(
    dist: str = "euclidean",
    threshold: float = 0.2,
    bootstrap: Optional[bool] = None,
    quantile_probability: float = 0.95,
    pca_components: Optional[int] = None,
) -> Callable:
    """Returns a function for calculating drift on embeddings using the average distance method with specified parameters
    Args:
        dist: "euclidean", "cosine", "cityblock" or "chebyshev"
        threshold: all values above this threshold means data drift. Applies when bootstrap != True
        bootstrap: boolean parameter to determine whether to apply statistical hypothesis testing
        quantile_probability: applies when bootstrap == True
        pca_components: number of components to keep
    Returns:
        func: a function for calculating drift, which takes in reference and current embeddings data
        and returns a tuple: drift score, whether there is drift, and the name of the drift calculation method.
    """

    return DistanceDriftMethod(
        dist=dist,
        threshold=threshold,
        bootstrap=bootstrap,
        quantile_probability=quantile_probability,
        pca_components=pca_components,
    )


def calc_roc_auc_random(y_test, i):
    np.random.seed(i)
    y_random_pred = np.random.rand(
        len(y_test),
    )
    roc_auc_random = roc_auc_score(y_test, y_random_pred)
    return roc_auc_random


class ModelDriftMethod(DriftMethod):
    threshold: float = 0.55
    bootstrap: Optional[bool] = None
    quantile_probability: float = 0.95
    pca_components: Optional[int] = None

    def __call__(self, current_emb: pd.DataFrame, reference_emb: pd.DataFrame) -> Tuple[float, bool, str]:
        if self.pca_components:
            reference_emb, current_emb = get_pca_df(reference_emb, current_emb, self.pca_components)
        reference_emb["target"] = [1] * reference_emb.shape[0]
        current_emb["target"] = [0] * current_emb.shape[0]
        data = pd.concat((reference_emb, current_emb))

        X_train, X_test, y_train, y_test = train_test_split(
            data.drop("target", axis=1), data["target"], test_size=0.5, random_state=42, shuffle=True
        )
        try:
            clf = SGDClassifier(loss="log_loss", random_state=42)
            clf.fit(X_train, y_train)
        except ValueError:
            clf = SGDClassifier(loss="log", random_state=42)
            clf.fit(X_train, y_train)
        y_pred_proba = clf.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        if self.bootstrap:
            roc_auc_values = [calc_roc_auc_random(y_test, i) for i in range(100)]
            rand_roc_auc = np.percentile(roc_auc_values, 100 * self.quantile_probability)
            return roc_auc, roc_auc > rand_roc_auc, "model"
        return roc_auc, roc_auc > self.threshold, "model"


def model(
    threshold: float = 0.55,
    bootstrap: Optional[bool] = None,
    quantile_probability: float = 0.95,
    pca_components: Optional[int] = None,
) -> DriftMethod:
    """Returns a function for calculating drift on embeddings using the classifier method with specified parameters
    Args:
        threshold: all values above this threshold means data drift. Applies when bootstrap != True
        bootstrap: boolean parameter to determine whether to apply statistical hypothesis testing
        quantile_probability: applies when bootstrap == True
        pca_components: number of components to keep
    Returns:
        func: a function for calculating drift, which takes in reference and current embeddings data
        and returns a tuple: drift score, whether there is drift, and the name of the drift calculation method.
    """
    return ModelDriftMethod(
        threshold=threshold,
        bootstrap=bootstrap,
        quantile_probability=quantile_probability,
        pca_components=pca_components,
    )


class RatioDriftMethod(DriftMethod):
    component_stattest: str = "wasserstein"
    component_stattest_threshold: float = 0.1
    threshold: float = 0.2
    pca_components: Optional[int] = None

    def __call__(self, current_emb: pd.DataFrame, reference_emb: pd.DataFrame) -> Tuple[float, bool, str]:
        if self.pca_components:
            reference_emb, current_emb = get_pca_df(reference_emb, current_emb, self.pca_components)
        stattest_func = get_stattest(
            reference_emb.iloc[:, 0], current_emb.iloc[:, 0], ColumnType.Numerical, self.component_stattest
        )
        n_drifted = 0
        for i in range(reference_emb.shape[1]):
            drift_result = stattest_func(
                reference_emb.iloc[:, i],
                current_emb.iloc[:, i],
                feature_type=ColumnType.Numerical,
                threshold=self.component_stattest_threshold,
            )
            if drift_result.drifted:
                n_drifted += 1
        return n_drifted / reference_emb.shape[1], n_drifted / reference_emb.shape[1] > self.threshold, "ratio"


def ratio(
    component_stattest: str = "wasserstein",
    component_stattest_threshold: float = 0.1,
    threshold: float = 0.2,
    pca_components: Optional[int] = None,
) -> DriftMethod:
    """Returns a function for calculating drift on embeddings using the ratio of drifted embeddings method
    with specified parameters
    Args:
        component_stattest: method for testing drift in a single embedding. Any drift detection method
        for a numerical feature implemented in evidently
        component_stattest_threshold: threshold for testing drift in a single embedding
        threshold: all values above this threshold means data drift
        pca_components: number of components to keep
    Returns:
        func: a function for calculating drift, which takes in reference and current embeddings data
        and returns a tuple: drift score, whether there is drift, and the name of the drift calculation method.
    """
    return RatioDriftMethod(
        component_stattest=component_stattest,
        component_stattest_threshold=component_stattest_threshold,
        threshold=threshold,
        pca_components=pca_components,
    )


def MMD2u(K, m, n):
    """The MMD^2_u unbiased statistic."""
    Kx = K[:m, :m]
    Ky = K[m:, m:]
    Kxy = K[:m, m:]
    return (
        1.0 / (m * (m - 1.0)) * (Kx.sum() - Kx.diagonal().sum())
        + 1.0 / (n * (n - 1.0)) * (Ky.sum() - Ky.diagonal().sum())
        - 2.0 / (m * n) * Kxy.sum()
    )


def MMD2u_bstrp(K, m, n, x_idx, y_idx):
    """The MMD^2_u unbiased statistic for bootstrap subsample."""
    Kx = K[[[idx] for idx in x_idx], x_idx]
    Ky = K[[[idx] for idx in y_idx], y_idx]
    Kxy = K[[[idx] for idx in x_idx], y_idx]
    return (
        1.0 / (m * (m - 1.0)) * (Kx.sum() - Kx.diagonal().sum())
        + 1.0 / (n * (n - 1.0)) * (Ky.sum() - Ky.diagonal().sum())
        - 2.0 / (m * n) * Kxy.sum()
    )


class MMDDriftMethod(DriftMethod):
    threshold: float = 0.015
    bootstrap: Optional[bool] = None
    quantile_probability: float = 0.05
    pca_components: Optional[int] = None

    def __call__(self, current_emb: pd.DataFrame, reference_emb: pd.DataFrame) -> Tuple[float, bool, str]:
        if self.pca_components:
            reference_emb, current_emb = get_pca_df(reference_emb, current_emb, self.pca_components)
        x = reference_emb
        y = current_emb
        m = len(x)
        n = len(y)

        pair_dists = pairwise_distances(
            x.sample(min(m, 1000), random_state=0),
            y.sample(min(n, 1000), random_state=0),
            metric="euclidean",
            n_jobs=-1,
        )
        sigma2 = np.median(pair_dists) ** 2
        xy = np.vstack([x, y])
        K = pairwise_kernels(xy, metric="rbf", gamma=1.0 / sigma2)
        mmd2u = MMD2u(K, m, n)
        if self.bootstrap:
            pair_dists_bstrp = pairwise_distances(x.sample(min(m, 1000), random_state=0), metric="euclidean", n_jobs=-1)
            sigma2_x = np.median(pair_dists_bstrp) ** 2
            gamma_x = 1.0 / sigma2_x
            K = pairwise_kernels(x, metric="rbf", gamma=gamma_x)
            x_size = max(int(m * m / (m + n)), 1)
            y_size = max(int(m * n / (m + n)), 1)
            bstrp_res = []
            for i in range(N_BOOTSTRAP):
                np.random.seed(i)
                x_idxs = np.random.choice(m, x_size)
                y_idxs = np.random.choice(m, y_size)
                bstrp_res.append(MMD2u_bstrp(K, x_size, y_size, x_idxs, y_idxs))
                perc = np.percentile(bstrp_res, 100 * self.quantile_probability)
            return max(mmd2u, 0), mmd2u > perc, "mmd"
        else:
            return max(mmd2u, 0), mmd2u > self.threshold, "mmd"


def mmd(
    threshold: float = 0.015,
    bootstrap: Optional[bool] = None,
    quantile_probability: float = 0.05,
    pca_components: Optional[int] = None,
) -> DriftMethod:
    """Returns a function for calculating drift on embeddings using the mmd method with specified parameters
    Args:
        threshold: all values above this threshold means data drift. Applies when bootstrap != True
        bootstrap: boolean parameter to determine whether to apply statistical hypothesis testing
        quantile_probability: applies when bootstrap == True
        pca_components: number of components to keep
    Returns:
        func: a function for calculating drift, which takes in reference and current embeddings data
        and returns a tuple: drift score, whether there is drift, and the name of the drift calculation method.
    """
    return MMDDriftMethod(
        threshold=threshold,
        bootstrap=bootstrap,
        quantile_probability=quantile_probability,
        pca_components=pca_components,
    )

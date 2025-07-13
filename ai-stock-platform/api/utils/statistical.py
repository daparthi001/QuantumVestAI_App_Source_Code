"""
Statistical Analysis Utilities
Created: 2025-05-20 05:05:14
Author: daparthi001
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import stats


class StatisticalAnalyzer:
    """Statistical analysis utility class."""

    def calculate_basic_stats(
        self,
        data: np.ndarray
    ) -> Dict[str, float]:
        """Calculate basic statistical measures."""
        return {
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "std": float(np.std(data)),
            "skewness": float(stats.skew(data)),
            "kurtosis": float(stats.kurtosis(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data))
        }

    def calculate_percentiles(
        self,
        data: np.ndarray,
        percentiles: List[float] = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    ) -> Dict[str, float]:
        """Calculate data percentiles."""
        return {
            f"p{int(p*100)}": float(np.percentile(data, p*100))
            for p in percentiles
        }

    def calculate_correlation_matrix(
        self,
        data: np.ndarray,
        method: str = "pearson"
    ) -> np.ndarray:
        """Calculate correlation matrix."""
        if method == "pearson":
            return np.corrcoef(data.T)
        elif method == "spearman":
            return stats.spearmanr(data)[0]
        elif method == "kendall":
            return stats.kendalltau(data)[0]
        else:
            raise ValueError(f"Unknown correlation method: {method}")

    def run_hypothesis_test(
        self,
        data1: np.ndarray,
        data2: np.ndarray,
        test_type: str = "t-test"
    ) -> Dict[str, Any]:
        """Run statistical hypothesis test."""
        if test_type == "t-test":
            stat, pvalue = stats.ttest_ind(data1, data2)
        elif test_type == "ks-test":
            stat, pvalue = stats.ks_2samp(data1, data2)
        elif test_type == "mann-whitney":
            stat, pvalue = stats.mannwhitneyu(data1, data2)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

        return {
            "test_type": test_type,
            "statistic": float(stat),
            "p_value": float(pvalue),
            "significant": bool(pvalue < 0.05)
        }

    def detect_outliers(
        self,
        data: np.ndarray,
        method: str = "zscore",
        threshold: float = 3.0
    ) -> Dict[str, Any]:
        """Detect outliers in data."""
        if method == "zscore":
            z_scores = np.abs(stats.zscore(data))
            outliers = np.where(z_scores > threshold)[0]
        elif method == "iqr":
            q1, q3 = np.percentile(data, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            outliers = np.where((data < lower_bound) | (data > upper_bound))[0]
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")

        return {
            "method": method,
            "threshold": threshold,
            "outlier_indices": outliers.tolist(),
            "outlier_values": data[outliers].tolist(),
            "outlier_count": len(outliers)
        }

    def calculate_rolling_statistics(
        self,
        data: np.ndarray,
        window: int = 20
    ) -> Dict[str, np.ndarray]:
        """Calculate rolling statistics."""
        return {
            "mean": np.convolve(data, np.ones(window)/window, mode='valid'),
            "std": np.array([np.std(data[i:i+window]) for i in range(len(data)-window+1)]),
            "min": np.array([np.min(data[i:i+window]) for i in range(len(data)-window+1)]),
            "max": np.array([np.max(data[i:i+window]) for i in range(len(data)-window+1)])
        }

    def analyze_distribution(
        self,
        data: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze data distribution."""
        # Test for normality
        shapiro_stat, shapiro_p = stats.shapiro(data)
        
        # Fit normal distribution
        mu, sigma = stats.norm.fit(data)
        
        # Calculate histogram
        hist, bins = np.histogram(data, bins='auto', density=True)
        
        return {
            "distribution_type": "normal" if shapiro_p > 0.05 else "non-normal",
            "shapiro_test": {
                "statistic": float(shapiro_stat),
                "p_value": float(shapiro_p)
            },
            "fitted_params": {
                "mu": float(mu),
                "sigma": float(sigma)
            },
            "histogram": {
                "counts": hist.tolist(),
                "bins": bins.tolist()
            }
        }

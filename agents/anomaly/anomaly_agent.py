"""
Anomaly Detection Agent - ML-based anomaly detection using multiple algorithms
Provides intelligent outlier detection beyond simple statistical methods
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import EllipticEnvelope


@dataclass
class AnomalyReport:
    """Report from anomaly detection analysis"""
    method: str
    anomaly_count: int
    anomaly_percentage: float
    anomaly_indices: List[int]
    feature_importance: Dict[str, float]
    anomaly_scores: np.ndarray
    recommendations: List[str]
    timestamp: str


class AnomalyDetectionAgent:
    """
    ML-based Anomaly Detection Agent
    Uses multiple algorithms to detect anomalies intelligently
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configuration
        self.methods = config.get('methods', ['isolation_forest', 'lof'])
        self.contamination = config.get('contamination', 'auto')
        self.ensemble_voting = config.get('ensemble_voting', 'majority')

    def detect_anomalies(self, data: pd.DataFrame) -> AnomalyReport:
        """
        Detect anomalies using ensemble of ML methods
        """
        self.logger.info(f"🔍 Starting anomaly detection with methods: {self.methods}")

        # Prepare numeric data only
        numeric_data = data.select_dtypes(include=[np.number])

        if numeric_data.empty or len(numeric_data) < 10:
            self.logger.warning("Insufficient numeric data for anomaly detection")
            return self._empty_report()

        # Scale the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_data.fillna(numeric_data.median()))

        # Run multiple detection methods
        anomaly_predictions = {}
        anomaly_scores_dict = {}

        if 'isolation_forest' in self.methods:
            preds, scores = self._isolation_forest(scaled_data)
            anomaly_predictions['isolation_forest'] = preds
            anomaly_scores_dict['isolation_forest'] = scores

        if 'lof' in self.methods:
            preds, scores = self._local_outlier_factor(scaled_data)
            anomaly_predictions['lof'] = preds
            anomaly_scores_dict['lof'] = scores

        if 'elliptic_envelope' in self.methods:
            preds, scores = self._elliptic_envelope(scaled_data)
            anomaly_predictions['elliptic_envelope'] = preds
            anomaly_scores_dict['elliptic_envelope'] = scores

        # Ensemble voting
        final_anomalies = self._ensemble_vote(anomaly_predictions)

        # Calculate feature importance (which columns contribute most to anomalies)
        feature_importance = self._calculate_feature_importance(
            numeric_data, final_anomalies
        )

        # Get anomaly scores (use average of all methods)
        avg_scores = np.mean([scores for scores in anomaly_scores_dict.values()], axis=0)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            final_anomalies, feature_importance, len(data)
        )

        anomaly_count = int(final_anomalies.sum())
        anomaly_percentage = (anomaly_count / len(data)) * 100

        self.logger.info(
            f"✅ Detected {anomaly_count} anomalies ({anomaly_percentage:.2f}%) "
            f"using {len(self.methods)} methods"
        )

        return AnomalyReport(
            method=f"Ensemble({', '.join(self.methods)})",
            anomaly_count=anomaly_count,
            anomaly_percentage=round(anomaly_percentage, 2),
            anomaly_indices=np.where(final_anomalies)[0].tolist(),
            feature_importance=feature_importance,
            anomaly_scores=avg_scores,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )

    def _isolation_forest(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Isolation Forest - effective for high-dimensional data"""
        clf = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        predictions = clf.fit_predict(data)
        scores = clf.score_samples(data)
        # -1 for anomalies, 1 for normal
        return (predictions == -1), -scores  # Invert scores for consistency

    def _local_outlier_factor(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Local Outlier Factor - detects local density deviations"""
        clf = LocalOutlierFactor(
            contamination=self.contamination if self.contamination != 'auto' else 0.1,
            novelty=False
        )
        predictions = clf.fit_predict(data)
        scores = -clf.negative_outlier_factor_
        return (predictions == -1), scores

    def _elliptic_envelope(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Elliptic Envelope - assumes Gaussian distribution"""
        try:
            clf = EllipticEnvelope(
                contamination=self.contamination if self.contamination != 'auto' else 0.1,
                random_state=42
            )
            predictions = clf.fit_predict(data)
            scores = clf.decision_function(data)
            return (predictions == -1), -scores
        except Exception as e:
            self.logger.warning(f"Elliptic Envelope failed: {e}")
            return np.zeros(len(data), dtype=bool), np.zeros(len(data))

    def _ensemble_vote(self, predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """Combine predictions from multiple methods"""
        if not predictions:
            return np.array([])

        # Stack all predictions
        stacked = np.vstack(list(predictions.values()))

        if self.ensemble_voting == 'majority':
            # Majority voting: anomaly if majority of methods agree
            votes = stacked.sum(axis=0)
            threshold = len(predictions) / 2
            return votes > threshold

        elif self.ensemble_voting == 'unanimous':
            # Unanimous: anomaly only if ALL methods agree
            return stacked.all(axis=0)

        elif self.ensemble_voting == 'any':
            # Any: anomaly if ANY method detects it
            return stacked.any(axis=0)

        else:
            # Default to majority
            votes = stacked.sum(axis=0)
            return votes > (len(predictions) / 2)

    def _calculate_feature_importance(
        self, data: pd.DataFrame, anomalies: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate which features contribute most to anomalies
        Uses variance and mean difference
        """
        if anomalies.sum() == 0:
            return {col: 0.0 for col in data.columns}

        importance = {}
        normal_data = data[~anomalies]
        anomaly_data = data[anomalies]

        for col in data.columns:
            # Calculate normalized difference in means
            normal_mean = normal_data[col].mean()
            anomaly_mean = anomaly_data[col].mean()
            std = data[col].std()

            if std > 0:
                # Z-score of difference
                importance[col] = abs(anomaly_mean - normal_mean) / std
            else:
                importance[col] = 0.0

        # Normalize to 0-1
        max_imp = max(importance.values()) if importance else 1.0
        if max_imp > 0:
            importance = {k: round(v / max_imp, 3) for k, v in importance.items()}

        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        return importance

    def _generate_recommendations(
        self, anomalies: np.ndarray, feature_importance: Dict[str, float], total_rows: int
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        anomaly_count = int(anomalies.sum())
        anomaly_pct = (anomaly_count / total_rows) * 100

        if anomaly_pct < 1:
            recommendations.append(
                f"✓ Low anomaly rate ({anomaly_pct:.1f}%) - data quality is good"
            )
        elif anomaly_pct < 5:
            recommendations.append(
                f"⚠️ Moderate anomaly rate ({anomaly_pct:.1f}%) - review flagged records"
            )
        else:
            recommendations.append(
                f"🔴 High anomaly rate ({anomaly_pct:.1f}%) - investigate data collection process"
            )

        # Top contributing features
        top_features = list(feature_importance.items())[:3]
        if top_features and top_features[0][1] > 0:
            feature_names = ", ".join([f"{name} ({score:.2f})" for name, score in top_features])
            recommendations.append(
                f"Key anomaly indicators: {feature_names}"
            )

        if anomaly_count > 0:
            recommendations.append(
                f"Consider: Remove {anomaly_count} anomalous rows or investigate further"
            )
            recommendations.append(
                "Use anomaly_indices from report to examine specific records"
            )

        return recommendations

    def _empty_report(self) -> AnomalyReport:
        """Return empty report when detection not possible"""
        return AnomalyReport(
            method="none",
            anomaly_count=0,
            anomaly_percentage=0.0,
            anomaly_indices=[],
            feature_importance={},
            anomaly_scores=np.array([]),
            recommendations=["Insufficient numeric data for anomaly detection"],
            timestamp=datetime.now().isoformat()
        )

    def mark_anomalies(self, data: pd.DataFrame, report: AnomalyReport) -> pd.DataFrame:
        """Add anomaly flag column to dataframe"""
        df = data.copy()
        df['is_anomaly'] = False
        if len(report.anomaly_indices) > 0:
            df.loc[report.anomaly_indices, 'is_anomaly'] = True
        return df

    def remove_anomalies(self, data: pd.DataFrame, report: AnomalyReport) -> pd.DataFrame:
        """Remove anomalous rows from dataframe"""
        if len(report.anomaly_indices) == 0:
            return data
        return data.drop(index=report.anomaly_indices).reset_index(drop=True)

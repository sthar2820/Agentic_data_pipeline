"""
Feature Engineering Agent - Automated feature generation and transformation
Intelligently creates new features based on data characteristics
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype


@dataclass
class FeatureEngineeringReport:
    """Report from feature engineering process"""
    original_features: int
    new_features: int
    total_features: int
    features_created: List[Dict[str, str]]
    transformations_applied: List[str]
    recommendations: List[str]
    timestamp: str


class FeatureEngineeringAgent:
    """
    Automated Feature Engineering Agent
    Intelligently creates features based on data types and patterns
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configuration
        self.enable_datetime_features = config.get('datetime_features', True)
        self.enable_numeric_features = config.get('numeric_features', True)
        self.enable_categorical_features = config.get('categorical_features', True)
        self.enable_interaction_features = config.get('interaction_features', False)
        self.enable_polynomial_features = config.get('polynomial_features', False)
        self.max_categorical_unique = config.get('max_categorical_unique', 50)

    def engineer_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, FeatureEngineeringReport]:
        """
        Automatically generate new features based on data characteristics
        """
        self.logger.info("🔧 Starting automated feature engineering...")

        df = data.copy()
        original_features = len(df.columns)
        features_created = []
        transformations = []

        # 1. DateTime feature extraction
        if self.enable_datetime_features:
            df, dt_features = self._extract_datetime_features(df)
            features_created.extend(dt_features)
            if dt_features:
                transformations.append(f"Extracted {len(dt_features)} datetime features")

        # 2. Numeric feature transformations
        if self.enable_numeric_features:
            df, num_features = self._create_numeric_features(df)
            features_created.extend(num_features)
            if num_features:
                transformations.append(f"Created {len(num_features)} numeric transformations")

        # 3. Categorical encoding
        if self.enable_categorical_features:
            df, cat_features = self._encode_categorical_features(df)
            features_created.extend(cat_features)
            if cat_features:
                transformations.append(f"Encoded {len(cat_features)} categorical features")

        # 4. Interaction features (if enabled)
        if self.enable_interaction_features:
            df, int_features = self._create_interaction_features(df)
            features_created.extend(int_features)
            if int_features:
                transformations.append(f"Created {len(int_features)} interaction features")

        # 5. Polynomial features (if enabled)
        if self.enable_polynomial_features:
            df, poly_features = self._create_polynomial_features(df)
            features_created.extend(poly_features)
            if poly_features:
                transformations.append(f"Created {len(poly_features)} polynomial features")

        new_features = len(df.columns) - original_features
        total_features = len(df.columns)

        recommendations = self._generate_recommendations(
            original_features, new_features, features_created
        )

        self.logger.info(
            f"✅ Feature engineering complete: {original_features} → {total_features} features "
            f"(+{new_features} new)"
        )

        report = FeatureEngineeringReport(
            original_features=original_features,
            new_features=new_features,
            total_features=total_features,
            features_created=features_created,
            transformations_applied=transformations,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )

        return df, report

    def _extract_datetime_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
        """Extract features from datetime columns"""
        features_created = []

        for col in df.columns:
            if is_datetime64_any_dtype(df[col]):
                # Extract common datetime components
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_dayofweek'] = df[col].dt.dayofweek
                df[f'{col}_quarter'] = df[col].dt.quarter
                df[f'{col}_is_weekend'] = df[col].dt.dayofweek.isin([5, 6]).astype(int)

                features_created.extend([
                    {'name': f'{col}_year', 'type': 'datetime_component', 'source': col},
                    {'name': f'{col}_month', 'type': 'datetime_component', 'source': col},
                    {'name': f'{col}_day', 'type': 'datetime_component', 'source': col},
                    {'name': f'{col}_dayofweek', 'type': 'datetime_component', 'source': col},
                    {'name': f'{col}_quarter', 'type': 'datetime_component', 'source': col},
                    {'name': f'{col}_is_weekend', 'type': 'datetime_flag', 'source': col},
                ])

                self.logger.info(f"  ✓ Extracted 6 datetime features from '{col}'")

        return df, features_created

    def _create_numeric_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
        """Create transformations of numeric features"""
        features_created = []
        numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]

        for col in numeric_cols[:10]:  # Limit to avoid explosion
            # Skip if column has negative values for log transform
            if (df[col] > 0).all():
                df[f'{col}_log'] = np.log1p(df[col])
                features_created.append({
                    'name': f'{col}_log',
                    'type': 'log_transform',
                    'source': col
                })

            # Square root (for non-negative)
            if (df[col] >= 0).all():
                df[f'{col}_sqrt'] = np.sqrt(df[col])
                features_created.append({
                    'name': f'{col}_sqrt',
                    'type': 'sqrt_transform',
                    'source': col
                })

            # Binning (discretization)
            if df[col].nunique() > 10:
                df[f'{col}_binned'] = pd.qcut(df[col], q=5, labels=False, duplicates='drop')
                features_created.append({
                    'name': f'{col}_binned',
                    'type': 'binning',
                    'source': col
                })

        if features_created:
            self.logger.info(f"  ✓ Created {len(features_created)} numeric transformations")

        return df, features_created

    def _encode_categorical_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
        """Encode categorical features intelligently"""
        features_created = []
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        for col in categorical_cols:
            unique_count = df[col].nunique()

            if unique_count <= self.max_categorical_unique:
                # One-hot encoding for low cardinality
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)

                for dummy_col in dummies.columns:
                    features_created.append({
                        'name': dummy_col,
                        'type': 'one_hot_encoding',
                        'source': col
                    })

                self.logger.info(
                    f"  ✓ One-hot encoded '{col}' into {len(dummies.columns)} features"
                )
            else:
                # Frequency encoding for high cardinality
                freq_map = df[col].value_counts(normalize=True).to_dict()
                df[f'{col}_frequency'] = df[col].map(freq_map)
                features_created.append({
                    'name': f'{col}_frequency',
                    'type': 'frequency_encoding',
                    'source': col
                })

                self.logger.info(
                    f"  ✓ Frequency encoded '{col}' (high cardinality: {unique_count} unique)"
                )

        return df, features_created

    def _create_interaction_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
        """Create interaction features between numeric columns"""
        features_created = []
        numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]

        # Limit to top numeric columns by variance (most informative)
        if len(numeric_cols) > 5:
            variances = df[numeric_cols].var().sort_values(ascending=False)
            numeric_cols = variances.head(5).index.tolist()

        # Create pairwise interactions
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                # Multiplication
                df[f'{col1}_x_{col2}'] = df[col1] * df[col2]
                features_created.append({
                    'name': f'{col1}_x_{col2}',
                    'type': 'interaction_multiply',
                    'source': f'{col1}, {col2}'
                })

                # Division (with protection)
                denominator = df[col2].replace(0, np.nan)
                df[f'{col1}_div_{col2}'] = (df[col1] / denominator).fillna(0)
                features_created.append({
                    'name': f'{col1}_div_{col2}',
                    'type': 'interaction_divide',
                    'source': f'{col1}, {col2}'
                })

        if features_created:
            self.logger.info(f"  ✓ Created {len(features_created)} interaction features")

        return df, features_created

    def _create_polynomial_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
        """Create polynomial features (squared, cubed)"""
        features_created = []
        numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]

        # Only for top 3 most variable numeric columns
        if len(numeric_cols) > 3:
            variances = df[numeric_cols].var().sort_values(ascending=False)
            numeric_cols = variances.head(3).index.tolist()

        for col in numeric_cols:
            # Squared
            df[f'{col}_squared'] = df[col] ** 2
            features_created.append({
                'name': f'{col}_squared',
                'type': 'polynomial_2',
                'source': col
            })

            # Cubed (for smaller datasets)
            if len(df) < 1000:
                df[f'{col}_cubed'] = df[col] ** 3
                features_created.append({
                    'name': f'{col}_cubed',
                    'type': 'polynomial_3',
                    'source': col
                })

        if features_created:
            self.logger.info(f"  ✓ Created {len(features_created)} polynomial features")

        return df, features_created

    def _generate_recommendations(
        self, original: int, new: int, features: List[Dict[str, str]]
    ) -> List[str]:
        """Generate recommendations for feature usage"""
        recommendations = []

        if new == 0:
            recommendations.append("ℹ️ No new features created - consider enabling more feature types")
        elif new < 10:
            recommendations.append(f"✓ Created {new} new features - good balance")
        elif new < 50:
            recommendations.append(
                f"⚠️ Created {new} new features - consider feature selection for ML models"
            )
        else:
            recommendations.append(
                f"🔴 Created {new} new features - high dimensionality, use feature selection/PCA"
            )

        # Type-specific recommendations
        feature_types = [f['type'] for f in features]
        if 'one_hot_encoding' in feature_types:
            recommendations.append(
                "One-hot encoded features created - these are ready for ML models"
            )

        if 'interaction_multiply' in feature_types or 'interaction_divide' in feature_types:
            recommendations.append(
                "Interaction features may improve model performance for non-linear relationships"
            )

        if 'datetime_component' in feature_types:
            recommendations.append(
                "Datetime features extracted - useful for time-series analysis"
            )

        return recommendations

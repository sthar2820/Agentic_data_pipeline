"""
Enhanced Refiner Agent - Intelligent Autonomous Data Cleaning
Uses Inspector's recommendations for adaptive cleaning strategies
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

from orchestrator.types import CleaningReport, DataQualityReport


class CleanerAgent:
    """
    Intelligently cleans data based on Inspector's quality assessment.
    Now truly agentic - makes autonomous decisions based on recommendations.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.missing_threshold = config.get('missing_threshold', 0.8)
        self.outlier_method = config.get('outlier_method', 'clip')
        self.actions: List[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def clean_data(self, data: pd.DataFrame, quality_report: Optional[DataQualityReport] = None) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Intelligently clean data using Inspector's proposed actions
        Falls back to heuristic cleaning if no quality report provided
        """
        self.actions = []
        df = data.copy()
        original_shape = df.shape
        original_rows = len(df)
        dropped_cols = []
        missing_handled = {}

        if quality_report and quality_report.proposed_actions:
            # AGENTIC MODE: Use Inspector's recommendations
            self.logger.info(f"🤖 Using {len(quality_report.proposed_actions)} proposed actions from Inspector")
            df, dropped_cols, missing_handled = self._execute_proposed_actions(
                df, quality_report.proposed_actions
            )
        else:
            # FALLBACK MODE: Use heuristic cleaning
            self.logger.info("⚠️ No quality report provided, using heuristic cleaning")
            df = self._remove_duplicates(df)
            df, cols = self._drop_bad_columns(df)
            dropped_cols.extend(cols)
            df, missing_handled = self._impute_missing(df)

        # Always apply these universal cleaning steps
        df = self._handle_outliers(df, quality_report)
        df = self._optimize_dtypes(df)

        rows_removed = original_rows - len(df)
        cleaned_shape = df.shape

        cleaning_report = CleaningReport(
            original_shape=original_shape,
            cleaned_shape=cleaned_shape,
            actions_taken=self.actions,
            columns_dropped=dropped_cols,
            rows_removed=rows_removed,
            missing_values_handled=missing_handled,
            timestamp=datetime.now().isoformat()
        )

        self.logger.info(f"✅ Cleaning complete: {original_shape} → {cleaned_shape}, {len(self.actions)} actions taken")
        return df, cleaning_report

    def _execute_proposed_actions(self, df: pd.DataFrame, proposed_actions: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, List[str], Dict[str, str]]:
        """
        Execute Inspector's proposed actions autonomously
        This is the key to making the agent truly intelligent
        """
        dropped_cols = []
        missing_handled = {}

        # Group actions by type for efficient execution
        actions_by_type = {}
        for action in proposed_actions:
            action_type = action.get('action', 'unknown')
            if action_type not in actions_by_type:
                actions_by_type[action_type] = []
            actions_by_type[action_type].append(action)

        # Execute actions in optimal order
        # 1. Drop columns first (reduces data to process)
        if 'drop_column' in actions_by_type:
            for action in actions_by_type['drop_column']:
                col = action['column']
                if col in df.columns:
                    df = df.drop(columns=[col])
                    dropped_cols.append(col)
                    reason = action.get('reason', 'proposed by Inspector')
                    self.actions.append(f"Dropped column '{col}' ({reason})")
                    self.logger.info(f"  ✓ Dropped column '{col}' - {reason}")

        # 2. Type conversions
        if 'cast_numeric' in actions_by_type:
            for action in actions_by_type['cast_numeric']:
                col = action['column']
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    self.actions.append(f"Converted '{col}' to numeric")
                    self.logger.info(f"  ✓ Converted '{col}' to numeric")

        if 'parse_datetime' in actions_by_type:
            for action in actions_by_type['parse_datetime']:
                col = action['column']
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    self.actions.append(f"Parsed '{col}' as datetime")
                    self.logger.info(f"  ✓ Parsed '{col}' as datetime")

        # 3. String cleaning
        if 'trim_whitespace' in actions_by_type:
            for action in actions_by_type['trim_whitespace']:
                col = action['column']
                if col in df.columns and df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
                    self.actions.append(f"Trimmed whitespace in '{col}'")
                    self.logger.info(f"  ✓ Trimmed whitespace in '{col}'")

        if 'standardize_case' in actions_by_type:
            for action in actions_by_type['standardize_case']:
                col = action['column']
                mode = action.get('mode', 'lower')
                if col in df.columns and df[col].dtype == 'object':
                    if mode == 'lower':
                        df[col] = df[col].str.lower()
                    elif mode == 'upper':
                        df[col] = df[col].str.upper()
                    self.actions.append(f"Standardized case in '{col}' to {mode}")
                    self.logger.info(f"  ✓ Standardized case in '{col}' to {mode}")

        # 4. Handle missing values with adaptive strategies
        if 'impute' in actions_by_type:
            for action in actions_by_type['impute']:
                col = action['column']
                strategy = action.get('strategy', 'simple')
                if col in df.columns:
                    count = df[col].isna().sum()
                    if count > 0:
                        if strategy == 'advanced':
                            # Use more sophisticated imputation for 30-70% missing
                            df[col] = self._advanced_impute(df, col)
                            missing_handled[col] = f'advanced imputation ({count} values)'
                        else:
                            # Simple imputation for 10-30% missing
                            df[col] = self._simple_impute(df, col)
                            missing_handled[col] = f'simple imputation ({count} values)'
                        self.actions.append(f"Imputed missing values in '{col}' using {strategy} strategy")
                        self.logger.info(f"  ✓ Imputed '{col}' - {strategy} strategy")

        # 5. Flag ID columns (don't drop, just log)
        if 'flag_id' in actions_by_type:
            for action in actions_by_type['flag_id']:
                col = action['column']
                if col in df.columns:
                    self.actions.append(f"Identified '{col}' as potential ID column (unique values)")
                    self.logger.info(f"  ℹ️ Flagged '{col}' as ID column")

        return df, dropped_cols, missing_handled

    def _simple_impute(self, df: pd.DataFrame, col: str) -> pd.Series:
        """Simple imputation strategy for low-medium missing data"""
        if pd.api.types.is_numeric_dtype(df[col]):
            return df[col].fillna(df[col].median())
        else:
            mode_val = df[col].mode()
            fill_val = mode_val.iloc[0] if len(mode_val) > 0 else 'Unknown'
            return df[col].fillna(fill_val)

    def _advanced_impute(self, df: pd.DataFrame, col: str) -> pd.Series:
        """Advanced imputation for high missing data (30-70%)"""
        if pd.api.types.is_numeric_dtype(df[col]):
            # Use forward fill + backward fill + median as last resort
            filled = df[col].fillna(method='ffill').fillna(method='bfill')
            return filled.fillna(df[col].median())
        else:
            # Use most frequent value or create 'Missing' category
            return df[col].fillna('Missing_Category')

    def clean_data_legacy(self, data: pd.DataFrame, report: Any = None) -> Tuple[pd.DataFrame, CleaningReport]:
        """Legacy method for backward compatibility"""
        return self.clean_data(data, report)
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicate rows"""
        initial_rows = len(df)
        df_clean = df.drop_duplicates()
        removed = initial_rows - len(df_clean)
        if removed > 0:
            self.actions.append(f'Removed {removed} duplicate rows')
        return df_clean
    
    def _drop_bad_columns(self, df: pd.DataFrame):
        """Drop columns with >80% missing data"""
        dropped_cols = []
        for col in df.columns:
            missing_pct = df[col].isnull().sum() / len(df)
            if missing_pct > self.missing_threshold:
                dropped_cols.append(col)
        if dropped_cols:
            self.actions.append(f'Dropped {len(dropped_cols)} columns with >{self.missing_threshold*100}% missing')
            df = df.drop(columns=dropped_cols)
        return df, dropped_cols
    
    def _impute_missing(self, df: pd.DataFrame):
        """Impute missing values"""
        missing_handled = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count == 0:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                missing_handled[col] = f'median ({missing_count} values)'
            else:
                df[col] = df[col].fillna('Unknown')
                missing_handled[col] = f'constant ({missing_count} values)'
        if missing_handled:
            self.actions.append(f'Imputed {len(missing_handled)} columns')
        return df, missing_handled
    
    def _handle_outliers(self, df: pd.DataFrame, quality_report: Optional[DataQualityReport] = None) -> pd.DataFrame:
        """Handle outliers using IQR method with Inspector's outlier details"""
        outlier_count = 0

        # Use Inspector's outlier details if available
        if quality_report and quality_report.outlier_details:
            outlier_details = quality_report.outlier_details
            for col, details in outlier_details.items():
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    lower_bound = details['lower_bound']
                    upper_bound = details['upper_bound']
                    outliers_before = details['count']

                    if self.outlier_method == 'clip':
                        df[col] = df[col].clip(lower_bound, upper_bound)
                        outlier_count += outliers_before
                        self.logger.info(f"  ✓ Clipped {outliers_before} outliers in '{col}'")
                    elif self.outlier_method == 'remove':
                        mask = (df[col] >= lower_bound) & (df[col] <= upper_bound)
                        df = df[mask]
                        outlier_count += outliers_before
                        self.logger.info(f"  ✓ Removed {outliers_before} outlier rows via '{col}'")
        else:
            # Fallback to heuristic method
            for col in df.select_dtypes(include=[np.number]).columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                    if outliers > 0:
                        df[col] = df[col].clip(lower_bound, upper_bound)
                        outlier_count += outliers

        if outlier_count > 0:
            self.actions.append(f'Handled {outlier_count} outliers using {self.outlier_method} method')
        return df
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types"""
        return df

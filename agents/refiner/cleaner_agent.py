"""
Refiner Agent - Automatic Data Cleaning
"""
import pandas as pd
import numpy as np
<<<<<<< Updated upstream
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

=======
from typing import Dict, List, Any
from datetime import datetime
>>>>>>> Stashed changes
from orchestrator.types import CleaningReport


class CleanerAgent:
    """Automatically cleans data based on quality assessment"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.missing_threshold = config.get('missing_threshold', 0.8)
        self.outlier_method = config.get('outlier_method', 'clip')
        self.actions: List[str] = []
    
    def clean_data(self, data: pd.DataFrame, report: Any = None):
        """Automatically clean data and return cleaned data with report"""
        self.actions = []
        df = data.copy()
        original_shape = df.shape
        original_rows = len(df)
        dropped_cols = []
        missing_handled = {}
        
<<<<<<< Updated upstream
    def clean_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Clean and preprocess the input data
        """
        self.logger.info("Starting data cleaning process...")
=======
        df = self._remove_duplicates(df)
        df, cols = self._drop_bad_columns(df)
        dropped_cols.extend(cols)
        df, missing_handled = self._impute_missing(df)
        df = self._handle_outliers(df)
        df = self._optimize_dtypes(df)
>>>>>>> Stashed changes
        
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
        
        return df, cleaning_report
    
<<<<<<< Updated upstream
    def _handle_missing_values(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Handle missing values based on configuration"""
        actions = []
        handle_method = self.config.get('handle_missing', 'auto')
        
        for col in data.columns:
            missing_count = data[col].isnull().sum()
=======
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
>>>>>>> Stashed changes
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
    
<<<<<<< Updated upstream
    def _handle_outliers(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Handle outliers based on configuration"""
        actions = []
        treatment = self.config.get('outlier_treatment', 'ignore')
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
=======
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using IQR method"""
        outlier_count = 0
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
>>>>>>> Stashed changes
            IQR = Q3 - Q1
            if IQR > 0:
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                if outliers > 0:
                    df[col] = df[col].clip(lower_bound, upper_bound)
                    outlier_count += outliers
        if outlier_count > 0:
            self.actions.append(f'Handled {outlier_count} outliers')
        return df
    
<<<<<<< Updated upstream
    def _identify_high_missing_columns(self, data: pd.DataFrame, threshold: float = 0.8) -> List[str]:
        """Identify columns with high percentage of missing values"""
        missing_pct = data.isnull().sum() / len(data)
        return missing_pct[missing_pct > threshold].index.tolist()
    
    def _optimize_data_types(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Optimize data types for better memory usage"""
        actions = []
        allow_object_to_numeric = self.config.get("cast_object_to_numeric", True)
        
        for col in data.columns:
            if data[col].dtype == 'object' and allow_object_to_numeric:
                # Try to convert to numeric
                try:
                    converted = pd.to_numeric(data[col], errors='coerce')
                    # Only convert if we don't lose everything
                    if not converted.isna().all() and converted.notna().mean() > 0.5:
                        data[col] = converted
                        actions.append(f"Converted '{col}' to numeric")
                except Exception:
                    pass
            
            elif data[col].dtype == 'int64':
                # Downcast integers
                if data[col].min() >= 0:
                    if data[col].max() < 255:
                        data[col] = data[col].astype('uint8')
                        actions.append(f"Optimized '{col}' to uint8")
                    elif data[col].max() < 65535:
                        data[col] = data[col].astype('uint16')
                        actions.append(f"Optimized '{col}' to uint16")
            
            elif data[col].dtype == 'float64':
                # Downcast floats
                data[col] = pd.to_numeric(data[col], downcast='float')
                if data[col].dtype != 'float64':
                    actions.append(f"Optimized '{col}' to {data[col].dtype}")
        
        return data, actions
    
    def _get_missing_value_summary(self, original: pd.DataFrame, cleaned: pd.DataFrame) -> Dict[str, str]:
        """Get summary of how missing values were handled"""
        summary = {}
        
        for col in original.columns:
            orig_missing = original[col].isnull().sum()
            if orig_missing > 0:
                if col in cleaned.columns:
                    new_missing = cleaned[col].isnull().sum()
                    if new_missing == 0:
                        summary[col] = "Filled all missing values"
                    elif new_missing < orig_missing:
                        summary[col] = f"Reduced missing values from {orig_missing} to {new_missing}"
                    else:
                        summary[col] = f"No change ({orig_missing} missing values)"
                else:
                    summary[col] = "Column dropped"
        
        return summary
=======
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types"""
        return df
>>>>>>> Stashed changes

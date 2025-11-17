import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

from orchestrator.types import CleaningReport


class CleanerAgent:
    """
    Data Refiner Agent - Cleans and preprocesses data
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def clean_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Clean and preprocess the input data
        """
        self.logger.info("Starting data cleaning process...")
        
        original_shape = data.shape
        actions_taken = []
        columns_dropped = []
        missing_values_handled = {}
        
        # Create a copy to avoid modifying original data
        cleaned_data = data.copy()
        
        # Remove duplicates
        if self.config.get('remove_duplicates', True):
            before_dup = len(cleaned_data)
            cleaned_data = cleaned_data.drop_duplicates()
            after_dup = len(cleaned_data)
            if before_dup != after_dup:
                actions_taken.append(f"Removed {before_dup - after_dup} duplicate rows")
        
        # Handle missing values
        cleaned_data, missing_actions = self._handle_missing_values(cleaned_data)
        actions_taken.extend(missing_actions)
        missing_values_handled = self._get_missing_value_summary(data, cleaned_data)
        
        # Handle outliers
        if self.config.get('outlier_treatment', 'ignore') != 'ignore':
            cleaned_data, outlier_actions = self._handle_outliers(cleaned_data)
            actions_taken.extend(outlier_actions)
        
        # Drop columns with too many missing values
        high_missing_cols = self._identify_high_missing_columns(data)
        if high_missing_cols:
            cleaned_data = cleaned_data.drop(columns=high_missing_cols)
            columns_dropped.extend(high_missing_cols)
            actions_taken.append(f"Dropped columns with >80% missing values: {high_missing_cols}")
        
        # Fix data types
        cleaned_data, type_actions = self._optimize_data_types(cleaned_data)
        actions_taken.extend(type_actions)
        
        rows_removed = original_shape[0] - cleaned_data.shape[0]
        
        report = CleaningReport(
            original_shape=original_shape,
            cleaned_shape=cleaned_data.shape,
            actions_taken=actions_taken,
            columns_dropped=columns_dropped,
            rows_removed=rows_removed,
            missing_values_handled=missing_values_handled,
            timestamp=datetime.now().isoformat()
        )
        
        self.logger.info(f"Data cleaning completed. Shape: {original_shape} -> {cleaned_data.shape}")
        return cleaned_data, report
    
    def _handle_missing_values(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Handle missing values based on configuration"""
        actions = []
        handle_method = self.config.get('handle_missing', 'auto')
        
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            if missing_count == 0:
                continue
                
            missing_pct = (missing_count / len(data)) * 100
            
            if handle_method == 'auto':
                if missing_pct > 80:
                    # Will be handled in column dropping
                    continue
                elif data[col].dtype in ['int64', 'float64']:
                    # Fill numeric columns with median
                    data[col] = data[col].fillna(data[col].median())
                    actions.append(f"Filled missing values in '{col}' with median")
                else:
                    # Fill categorical columns with mode
                    mode_value = data[col].mode()[0] if not data[col].mode().empty else 'Unknown'
                    data[col] = data[col].fillna(mode_value)
                    actions.append(f"Filled missing values in '{col}' with mode")
            
            elif handle_method == 'drop':
                data = data.dropna(subset=[col])
                actions.append(f"Dropped rows with missing values in '{col}'")
            
            elif handle_method == 'fill':
                if data[col].dtype in ['int64', 'float64']:
                    data[col] = data[col].fillna(0)
                    actions.append(f"Filled missing values in '{col}' with 0")
                else:
                    data[col] = data[col].fillna('Unknown')
                    actions.append(f"Filled missing values in '{col}' with 'Unknown'")
        
        return data, actions
    
    def _handle_outliers(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Handle outliers based on configuration"""
        actions = []
        treatment = self.config.get('outlier_treatment', 'ignore')
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                if treatment == 'remove':
                    data = data[~outlier_mask]
                    actions.append(f"Removed {outlier_count} outliers from '{col}'")
                elif treatment == 'clip':
                    data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)
                    actions.append(f"Clipped {outlier_count} outliers in '{col}'")
        
        return data, actions
    
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

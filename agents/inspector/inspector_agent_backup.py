import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import re

from orchestrator.types import DataQualityReport, DataQuality


class InspectorAgent:
    """Enhanced Data Inspector Agent - Comprehensive data quality profiling"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.outlier_method = config.get('outlier_method', 'row')
        
    def analyze_data(self, data: pd.DataFrame) -> DataQualityReport:
        """Perform comprehensive data quality analysis"""
        self.logger.info(f"Starting enhanced analysis: {data.shape[0]} rows × {data.shape[1]} cols")
        
        # Core analysis
        missing_values = self._analyze_missing_values(data)
        data_types = self._analyze_data_types(data)
        duplicate_count = self._count_duplicates(data)
        outlier_count, outlier_details = self._detect_outliers(data)
        column_stats = self._calculate_column_statistics(data)
        
        # Enhanced analysis
        cardinality_analysis = self._analyze_cardinality(data)
        skewness_analysis = self._analyze_skewness(data)
        pattern_analysis = self._analyze_patterns(data)
        consistency_issues = self._check_consistency(data)
        column_quality_scores = self._calculate_column_quality_scores(
            data, missing_values, cardinality_analysis, consistency_issues
        )
        
        # Enrich column stats
        for col in column_stats:
            if col in cardinality_analysis:
                column_stats[col]['cardinality'] = cardinality_analysis[col]
            if col in skewness_analysis:
                column_stats[col]['skewness'] = skewness_analysis[col]
            if col in pattern_analysis:
                column_stats[col]['patterns'] = pattern_analysis[col]
            if col in column_quality_scores:
                column_stats[col]['quality_score'] = column_quality_scores[col]
            if col in outlier_details:
                column_stats[col]['outliers'] = outlier_details[col]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            missing_values, duplicate_count, outlier_count, data_types,
            cardinality_analysis, consistency_issues, column_quality_scores,
            pattern_analysis
        )
        
        # Assess overall quality
        overall_quality = self._assess_overall_quality(
            missing_values, duplicate_count, outlier_count, 
            column_quality_scores, len(data)
        )
        
        report = DataQualityReport(
            overall_quality=overall_quality,
            missing_values=missing_values,
            data_types=data_types,
            duplicate_count=duplicate_count,
            outlier_count=outlier_count,
            column_stats=column_stats,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            cardinality_analysis=cardinality_analysis,
            skewness_analysis=skewness_analysis,
            pattern_analysis=pattern_analysis,
            consistency_issues=consistency_issues,
            column_quality_scores=column_quality_scores,
            outlier_details=outlier_details
        )
        
        self.logger.info(f"✓ Analysis complete. Quality: {overall_quality.value.upper()}")
        self.logger.info(f"✓ Generated {len(recommendations)} recommendations")
        return report
    
    def _analyze_missing_values(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate percentage of missing values for each column"""
        missing_pct = (data.isnull().sum() / len(data) * 100).to_dict()
        return {col: round(pct, 2) for col, pct in missing_pct.items()}
    
    def _analyze_data_types(self, data: pd.DataFrame) -> Dict[str, str]:
        """Get data types for each column"""
        return {col: str(dtype) for col, dtype in data.dtypes.items()}
    
    def _count_duplicates(self, data: pd.DataFrame) -> int:
        """Count duplicate rows"""
        return int(data.duplicated().sum())
    
    def _detect_outliers(self, data: pd.DataFrame) -> Tuple[int, Dict[str, Dict[str, Any]]]:
        """Detect outliers using IQR method"""
        outlier_details = {}
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if self.outlier_method == 'cell':
            total_outliers = 0
            for col in numeric_cols:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                total_outliers += outlier_count
                
                if outlier_count > 0:
                    outlier_details[col] = {
                        'count': int(outlier_count),
                        'percentage': round(outlier_count / len(data) * 100, 2),
                        'lower_bound': round(lower_bound, 2),
                        'upper_bound': round(upper_bound, 2)
                    }
            return total_outliers, outlier_details
        else:
            outlier_rows = set()
            for col in numeric_cols:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    outlier_details[col] = {
                        'count': int(outlier_count),
                        'percentage': round(outlier_count / len(data) * 100, 2),
                        'lower_bound': round(lower_bound, 2),
                        'upper_bound': round(upper_bound, 2)
                    }
                    outlier_rows.update(data[outlier_mask].index.tolist())
            return len(outlier_rows), outlier_details
    
    def _calculate_column_statistics(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Calculate basic statistics for each column"""
        stats = {}
        for col in data.columns:
            col_stats = {
                'dtype': str(data[col].dtype),
                'non_null_count': int(data[col].count()),
                'null_count': int(data[col].isnull().sum()),
                'unique_count': int(data[col].nunique())
            }
            
            if pd.api.types.is_numeric_dtype(data[col]):
                col_stats.update({
                    'mean': round(data[col].mean(), 2) if not data[col].isnull().all() else None,
                    'std': round(data[col].std(), 2) if not data[col].isnull().all() else None,
                    'min': round(data[col].min(), 2) if not data[col].isnull().all() else None,
                    'max': round(data[col].max(), 2) if not data[col].isnull().all() else None
                })
            
            stats[col] = col_stats
        return stats
    
    def _analyze_cardinality(self, data: pd.DataFrame) -> Dict[str, str]:
        """Analyze cardinality: constant, low, medium, high, unique"""
        cardinality = {}
        total_rows = len(data)
        
        for col in data.columns:
            unique_count = data[col].nunique()
            non_null_count = data[col].count()
            
            if unique_count == 1:
                cardinality[col] = "constant"
            elif unique_count == non_null_count and non_null_count > 1:
                cardinality[col] = "unique"
            elif unique_count <= 10:
                cardinality[col] = "low"
            elif unique_count / total_rows < 0.5:
                cardinality[col] = "medium"
            else:
                cardinality[col] = "high"
        
        return cardinality
    
    def _analyze_skewness(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate skewness for numeric columns"""
        skewness = {}
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if data[col].count() > 0:
                skew_value = data[col].skew()
                if not np.isnan(skew_value):
                    skewness[col] = round(skew_value, 2)
        
        return skewness
    
    def _analyze_patterns(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze patterns in text columns"""
        pattern_analysis = {}
        text_cols = data.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            non_null_values = data[col].dropna()
            if len(non_null_values) == 0:
                continue
                
            patterns = non_null_values.apply(self._generate_pattern_mask)
            pattern_counts = patterns.value_counts()
            
            top_patterns = pattern_counts.head(5).to_dict()
            consistency_pct = round(pattern_counts.iloc[0] / len(non_null_values) * 100, 2) if len(pattern_counts) > 0 else 0
            
            pattern_analysis[col] = {
                'top_patterns': top_patterns,
                'consistency_pct': consistency_pct,
                'pattern_diversity': len(pattern_counts)
            }
        
        return pattern_analysis
    
    def _generate_pattern_mask(self, value: str) -> str:
        """Generate pattern mask: A=letter, #=digit, S=symbol, W=whitespace"""
        if pd.isna(value) or not isinstance(value, str):
            return "NULL"
        
        mask = []
        for char in str(value):
            if char.isalpha():
                mask.append('A')
            elif char.isdigit():
                mask.append('#')
            elif char.isspace():
                mask.append('W')
            else:
                mask.append('S')
        
        # Compress consecutive characters
        compressed = []
        for char in mask:
            if not compressed or compressed[-1] != char:
                compressed.append(char)
        
        return ''.join(compressed)
    
    def _check_consistency(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """Check for consistency issues in data"""
        consistency_issues = {}
        
        for col in data.columns:
            issues = []
            non_null = data[col].dropna()
            
            if len(non_null) == 0:
                continue
            
            if data[col].dtype == 'object':
                # Check if numeric-like
                numeric_like = non_null.apply(lambda x: str(x).replace('.', '', 1).replace('-', '', 1).isdigit()).sum()
                numeric_like_pct = numeric_like / len(non_null)
                
                if numeric_like_pct > 0.7:
                    issues.append(f"Numeric-like text ({numeric_like_pct*100:.1f}% could be numbers)")
                elif 0.1 < numeric_like_pct < 0.7:
                    issues.append(f"Mixed content ({numeric_like_pct*100:.1f}% numeric-like)")
                
                # Check for whitespace issues
                has_leading = non_null.astype(str).str.startswith(' ').sum()
                has_trailing = non_null.astype(str).str.endswith(' ').sum()
                if has_leading > 0 or has_trailing > 0:
                    issues.append(f"Whitespace issues (leading: {has_leading}, trailing: {has_trailing})")
                
                # Check for case inconsistencies
                unique_lower = non_null.astype(str).str.lower().nunique()
                unique_original = non_null.nunique()
                if unique_lower < unique_original:
                    issues.append(f"Case inconsistencies ({unique_original - unique_lower} duplicates when lowercased)")
            
            if issues:
                consistency_issues[col] = issues
        
        return consistency_issues
    
    def _calculate_column_quality_scores(
        self, 
        data: pd.DataFrame,
        missing_values: Dict[str, float],
        cardinality_analysis: Dict[str, str],
        consistency_issues: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """Calculate quality score (0-1) for each column"""
        scores = {}
        
        for col in data.columns:
            score = 1.0
            
            # Completeness (40% weight)
            completeness_penalty = (missing_values.get(col, 0) / 100) * 0.4
            score -= completeness_penalty
            
            # Cardinality (25% weight)
            cardinality = cardinality_analysis.get(col, "medium")
            if cardinality == "constant":
                score -= 0.25
            elif cardinality == "unique" and col.lower() not in ['id', 'identifier', 'key']:
                score -= 0.1
            
            # Type consistency (20% weight)
            if col in consistency_issues:
                num_issues = len(consistency_issues[col])
                score -= min(num_issues * 0.05, 0.2)
            
            # Pattern consistency (15% weight)
            if data[col].dtype == 'object':
                non_null = data[col].dropna()
                if len(non_null) > 0:
                    patterns = non_null.apply(self._generate_pattern_mask)
                    top_pattern_pct = patterns.value_counts().iloc[0] / len(patterns) if len(patterns) > 0 else 1
                    pattern_penalty = (1 - top_pattern_pct) * 0.15
                    score -= pattern_penalty
            
            scores[col] = max(0.0, min(1.0, round(score, 3)))
        
        return scores
    
    def _generate_recommendations(
        self,
        missing_values: Dict[str, float],
        duplicate_count: int,
        outlier_count: int,
        data_types: Dict[str, str],
        cardinality_analysis: Dict[str, str],
        consistency_issues: Dict[str, List[str]],
        column_quality_scores: Dict[str, float],
        pattern_analysis: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # CRITICAL: High missing values
        high_missing = {col: pct for col, pct in missing_values.items() if pct > 50}
        if high_missing:
            recommendations.append(
                f"🚨 CRITICAL: {len(high_missing)} columns have >50% missing values: {', '.join(list(high_missing.keys())[:3])}"
            )
        
        # CRITICAL: Constant columns
        constant_cols = [col for col, card in cardinality_analysis.items() if card == "constant"]
        if constant_cols:
            recommendations.append(
                f"🚨 CRITICAL: {len(constant_cols)} constant columns: {', '.join(constant_cols[:3])}"
            )
        
        # HIGH: Duplicates
        if duplicate_count > 0:
            recommendations.append(
                f"⚠️ HIGH: Found {duplicate_count} duplicate rows - consider deduplication"
            )
        
        # HIGH: Low quality columns
        low_quality = {col: score for col, score in column_quality_scores.items() if score < 0.5}
        if low_quality:
            top_3 = sorted(low_quality.items(), key=lambda x: x[1])[:3]
            recommendations.append(
                f"⚠️ HIGH: {len(low_quality)} columns with quality <0.5. Worst: {', '.join([f'{col}({score:.2f})' for col, score in top_3])}"
            )
        
        # HIGH: Consistency issues
        if consistency_issues:
            for col, issues in list(consistency_issues.items())[:2]:
                recommendations.append(f"⚠️ HIGH: '{col}' - {'; '.join(issues)}")
        
        # MEDIUM: Outliers
        if outlier_count > 0:
            recommendations.append(
                f"📊 MEDIUM: Detected {outlier_count} outliers"
            )
        
        # MEDIUM: Moderate missing values
        medium_missing = {col: pct for col, pct in missing_values.items() if 10 < pct <= 50}
        if medium_missing:
            recommendations.append(
                f"📊 MEDIUM: {len(medium_missing)} columns have 10-50% missing values"
            )
        
        # INFO: Pattern insights
        for col, analysis in list(pattern_analysis.items())[:2]:
            if analysis['consistency_pct'] < 70:
                recommendations.append(
                    f"�� INFO: '{col}' has low pattern consistency ({analysis['consistency_pct']}%)"
                )
        
        return recommendations
    
    def _assess_overall_quality(
        self,
        missing_values: Dict[str, float],
        duplicate_count: int,
        outlier_count: int,
        column_quality_scores: Dict[str, float],
        total_rows: int
    ) -> DataQuality:
        """Assess overall quality: EXCELLENT/GOOD/FAIR/POOR"""
        avg_missing = sum(missing_values.values()) / len(missing_values) if missing_values else 0
        dup_pct = (duplicate_count / total_rows * 100) if total_rows > 0 else 0
        outlier_pct = (outlier_count / total_rows * 100) if total_rows > 0 else 0
        avg_quality = sum(column_quality_scores.values()) / len(column_quality_scores) if column_quality_scores else 1.0
        
        score = 100
        score -= avg_missing * 0.5
        score -= min(dup_pct * 2, 20)
        score -= min(outlier_pct, 10)
        score -= (1 - avg_quality) * 30
        
        if score >= 85:
            return DataQuality.EXCELLENT
        elif score >= 70:
            return DataQuality.GOOD
        elif score >= 50:
            return DataQuality.FAIR
        else:
            return DataQuality.POOR

# filepath: agents/inspector/inspector_agent.py
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
        self.logger.info(f"Starting enhanced data quality analysis on {data.shape[0]} rows × {data.shape[1]} columns...")
        
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
        
        self.logger.info(f"Analysis complete. Quality: {overall_quality.value.upper()}")
        return report

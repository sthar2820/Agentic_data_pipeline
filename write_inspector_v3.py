#!/usr/bin/env python3
"""Write the improved InspectorAgent v3 with agentic capabilities."""

INSPECTOR_CONTENT = '''# filepath: /Users/roh/Documents/GitHub/Agentic_data_pipeline/agents/inspector/inspector_agent.py
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_numeric_dtype,
    is_string_dtype,
    is_categorical_dtype,
)

from orchestrator.types import DataQuality, DataQualityReport
from orchestrator.serialize import save_json


_DEFAULTS: Dict[str, Any] = {
    "dataset_name": "dataset",
    "artifacts_dir": "data/artifacts",
    "outlier_method": "row",
    "sample_size": 500,
    "thresholds": {
        "missing_drop": 0.70,
        "missing_high": 0.30,
        "missing_medium": 0.10,
        "cardinality_low_ratio": 0.05,
        "cardinality_high_ratio": 0.95,
    },
    "modules": {
        "patterns": True,
        "consistency": True,
        "skewness": True
    }
}


class InspectorAgent:
    """
    Enhanced Data Inspector Agent - comprehensive data quality profiling with
    agentic outputs (human-readable recommendations + machine-readable actions).
    """

    def __init__(self, config: Dict[str, Any] = None):
        cfg = config or {}
        thresholds = {**_DEFAULTS["thresholds"], **cfg.get("thresholds", {})}
        modules = {**_DEFAULTS["modules"], **cfg.get("modules", {})}
        self.config = {**_DEFAULTS, **cfg, "thresholds": thresholds, "modules": modules}
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_data(self, data: pd.DataFrame) -> DataQualityReport:
        """Main analysis method with agentic outputs."""
        self.logger.info(f"Starting analysis: {data.shape[0]} rows × {data.shape[1]} cols")
        
        # Core metrics
        missing_values = self._analyze_missing_values(data)
        data_types = self._analyze_data_types(data)
        duplicate_count = self._count_duplicates(data)
        outlier_count, outlier_details = self._detect_outliers(data)
        column_stats = self._calculate_column_statistics(data)
        
        # Enhanced metrics (if enabled)
        cardinality = self._analyze_cardinality(data)
        skewness = self._analyze_skewness(data) if self.config["modules"]["skewness"] else {}
        patterns = self._analyze_patterns(data) if self.config["modules"]["patterns"] else {}
        consistency = self._check_consistency(data) if self.config["modules"]["consistency"] else {}
        
        # Column quality scoring
        col_quality = self._calculate_column_quality_scores(data, missing_values, cardinality, consistency)
        
        # Enrich column stats
        for col in column_stats:
            column_stats[col]["cardinality"] = cardinality.get(col, {})
            if skewness:
                column_stats[col]["skewness"] = skewness.get(col)
            if patterns:
                column_stats[col]["patterns"] = patterns.get(col, {})
            column_stats[col]["quality_score"] = col_quality.get(col, 0.0)
            if col in outlier_details:
                column_stats[col]["outliers"] = outlier_details[col]
        
        # Generate human recommendations
        recommendations = self._generate_recommendations(
            missing_values, duplicate_count, outlier_count, data_types,
            cardinality, consistency, col_quality, patterns
        )
        
        # Generate machine actions
        proposed_actions = self._propose_actions(missing_values, consistency, cardinality)
        
        # Overall quality rating
        overall_quality = self._assess_overall_quality(
            missing_values, duplicate_count, outlier_count, data.shape[0], col_quality
        )
        
        report = DataQualityReport(
            timestamp=datetime.now(),
            dataset_name=self.config["dataset_name"],
            row_count=data.shape[0],
            column_count=data.shape[1],
            missing_values=missing_values,
            duplicate_count=duplicate_count,
            outlier_count=outlier_count,
            data_types=data_types,
            column_statistics=column_stats,
            recommendations=recommendations,
            overall_quality=overall_quality,
            proposed_actions=proposed_actions
        )
        
        self._save_artifacts(report, proposed_actions)
        return report

    def _analyze_missing_values(self, data: pd.DataFrame) -> Dict[str, float]:
        return {col: float(data[col].isna().sum() / len(data) * 100) for col in data.columns}

    def _analyze_data_types(self, data: pd.DataFrame) -> Dict[str, str]:
        return {col: str(data[col].dtype) for col in data.columns}

    def _count_duplicates(self, data: pd.DataFrame) -> int:
        return int(data.duplicated().sum())

    def _detect_outliers(self, data: pd.DataFrame) -> Tuple[int, Dict[str, int]]:
        """Detect outliers using IQR method."""
        outlier_details = {}
        total = 0
        
        for col in data.select_dtypes(include=[np.number]).columns:
            q1 = data[col].quantile(0.25)
            q3 = data[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = ((data[col] < lower) | (data[col] > upper)).sum()
            outlier_details[col] = int(outliers)
            total += outliers
            
        return total, outlier_details

    def _calculate_column_statistics(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Calculate basic statistics for each column."""
        stats = {}
        for col in data.columns:
            col_stats = {
                "missing_count": int(data[col].isna().sum()),
                "missing_pct": float(data[col].isna().sum() / len(data) * 100),
                "unique_count": int(data[col].nunique()),
                "dtype": str(data[col].dtype)
            }
            
            if is_numeric_dtype(data[col]):
                col_stats.update({
                    "mean": float(data[col].mean()) if not data[col].isna().all() else None,
                    "std": float(data[col].std()) if not data[col].isna().all() else None,
                    "min": float(data[col].min()) if not data[col].isna().all() else None,
                    "max": float(data[col].max()) if not data[col].isna().all() else None
                })
            
            stats[col] = col_stats
        return stats

    def _analyze_cardinality(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze cardinality (constant/low/medium/high/unique)."""
        result = {}
        thresholds = self.config["thresholds"]
        
        for col in data.columns:
            unique = data[col].nunique()
            total = len(data)
            ratio = unique / total if total > 0 else 0
            
            if unique == 1:
                category = "constant"
            elif ratio < thresholds["cardinality_low_ratio"]:
                category = "low"
            elif ratio > thresholds["cardinality_high_ratio"]:
                category = "unique"
            elif ratio > 0.5:
                category = "high"
            else:
                category = "medium"
            
            result[col] = {
                "unique": unique,
                "total": total,
                "ratio": round(ratio, 4),
                "category": category
            }
        return result

    def _analyze_skewness(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze skewness for numeric columns."""
        result = {}
        for col in data.select_dtypes(include=[np.number]).columns:
            if data[col].nunique() > 1:
                result[col] = round(float(data[col].skew()), 4)
        return result

    def _analyze_patterns(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Pattern profiling with special detections."""
        result = {}
        sample_size = min(self.config["sample_size"], len(data))
        
        for col in data.select_dtypes(include=[object, 'string']).columns:
            sample = data[col].dropna().head(sample_size).astype(str)
            if len(sample) == 0:
                continue
            
            # Pattern masks: A=letter, #=digit, S=symbol, W=whitespace
            def make_mask(s):
                return "".join(
                    "A" if c.isalpha() else
                    "#" if c.isdigit() else
                    "W" if c.isspace() else
                    "S"
                    for c in str(s)
                )
            
            masks = sample.apply(make_mask)
            top_patterns = masks.value_counts().head(5).to_dict()
            
            result[col] = {
                "top_patterns": {k: int(v) for k, v in top_patterns.items()},
                "contains_email": bool(sample.str.contains("@", regex=False).any()),
                "contains_url": bool(sample.str.contains("http", regex=False).any()),
                "contains_phone": bool(sample.str.match(r".*\\d{3}[-.]?\\d{3}[-.]?\\d{4}.*").any()),
                "contains_currency": bool(sample.str.match(r"^\\$?[\\d,]+\\.?\\d*$").any()),
                "is_date_like": self._is_date_like(sample)
            }
        return result

    def _is_date_like(self, series: pd.Series) -> bool:
        """Check if series contains date-like strings."""
        try:
            pd.to_datetime(series.head(20), errors='coerce')
            return series.head(20).apply(lambda x: pd.to_datetime(x, errors='coerce')).notna().mean() > 0.5
        except:
            return False

    def _check_consistency(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Consistency checks for text columns."""
        result = {}
        
        for col in data.select_dtypes(include=[object, 'string']).columns:
            sample = data[col].dropna().astype(str).head(self.config["sample_size"])
            if len(sample) == 0:
                continue
            
            issues = {
                "numeric_like": int(sample.str.match(r"^\\d+\\.?\\d*$").sum()),
                "has_leading_ws": int(sample.str.match(r"^\\s+.*").sum()),
                "has_trailing_ws": int(sample.str.match(r".*\\s+$").sum()),
                "mixed_case": int((sample != sample.str.lower()) & (sample != sample.str.upper())).sum()
            }
            
            if any(issues.values()):
                result[col] = issues
        return result

    def _calculate_column_quality_scores(
        self, data: pd.DataFrame, missing: Dict[str, float],
        cardinality: Dict[str, Dict], consistency: Dict[str, Dict]
    ) -> Dict[str, float]:
        """Score each column 0-1 based on quality."""
        scores = {}
        for col in data.columns:
            score = 1.0
            
            # Missing penalty
            miss_pct = missing.get(col, 0)
            score -= min(miss_pct / 100, 0.5)
            
            # Cardinality penalty
            card = cardinality.get(col, {})
            if card.get("category") == "constant":
                score -= 0.3
            
            # Consistency penalty
            if col in consistency:
                total_issues = sum(consistency[col].values())
                score -= min(total_issues / len(data) * 0.2, 0.2)
            
            scores[col] = max(0.0, round(score, 4))
        return scores

    def _generate_recommendations(
        self, missing: Dict[str, float], dup_count: int, outlier_count: int,
        dtypes: Dict[str, str], cardinality: Dict, consistency: Dict,
        col_quality: Dict[str, float], patterns: Dict
    ) -> List[str]:
        """Generate human-readable recommendations."""
        recs = []
        thresholds = self.config["thresholds"]
        
        # Missing values
        high_missing = [col for col, pct in missing.items() if pct > thresholds["missing_drop"] * 100]
        if high_missing:
            recs.append(f"🚨 CRITICAL: Drop {len(high_missing)} columns with >{thresholds['missing_drop']*100:.0f}% missing: {high_missing[:3]}")
        
        medium_missing = [col for col, pct in missing.items() 
                         if thresholds["missing_medium"] * 100 < pct <= thresholds["missing_high"] * 100]
        if medium_missing:
            recs.append(f"⚠️ HIGH: Impute {len(medium_missing)} columns with 10-30% missing")
        
        # Duplicates
        if dup_count > 0:
            recs.append(f"⚠️ HIGH: Remove {dup_count} duplicate rows")
        
        # Outliers
        if outlier_count > 0:
            recs.append(f"📊 MEDIUM: Review {outlier_count} outliers (may be valid)")
        
        # Consistency issues
        if consistency:
            for col, issues in list(consistency.items())[:3]:
                if issues.get("numeric_like", 0) > 0:
                    recs.append(f"📊 MEDIUM: Column '{col}' has {issues['numeric_like']} numeric-like strings - consider type conversion")
        
        # Cardinality
        constant_cols = [col for col, info in cardinality.items() if info["category"] == "constant"]
        if constant_cols:
            recs.append(f"💡 INFO: Consider dropping {len(constant_cols)} constant columns")
        
        # Low quality columns
        low_quality = [col for col, score in col_quality.items() if score < 0.5]
        if low_quality:
            recs.append(f"⚠️ HIGH: {len(low_quality)} columns have quality score <0.5 - review carefully")
        
        return recs

    def _propose_actions(
        self, missing: Dict[str, float], consistency: Dict, cardinality: Dict
    ) -> List[Dict[str, Any]]:
        """Generate machine-readable proposed actions."""
        actions = []
        thresholds = self.config["thresholds"]
        
        for col, pct in missing.items():
            if pct > thresholds["missing_drop"] * 100:
                actions.append({
                    "column": col,
                    "action": "drop_column",
                    "reason": f"missing>{thresholds['missing_drop']*100:.0f}%",
                    "priority": "high"
                })
            elif pct > thresholds["missing_medium"] * 100:
                actions.append({
                    "column": col,
                    "action": "impute",
                    "strategy": "advanced",
                    "reason": f"missing={pct:.1f}%",
                    "priority": "medium"
                })
        
        for col, issues in consistency.items():
            if issues.get("numeric_like", 0) > 5:
                actions.append({
                    "column": col,
                    "action": "cast_numeric",
                    "coerce": True,
                    "reason": "contains numeric-like strings",
                    "priority": "medium"
                })
        
        for col, info in cardinality.items():
            if info["category"] == "constant":
                actions.append({
                    "column": col,
                    "action": "drop_column",
                    "reason": "constant_value",
                    "priority": "low"
                })
        
        return actions

    def _assess_overall_quality(
        self, missing: Dict[str, float], dup_count: int, outlier_count: int,
        total_rows: int, col_quality: Dict[str, float]
    ) -> DataQuality:
        """Assess overall quality rating."""
        avg_missing = sum(missing.values()) / len(missing) if missing else 0
        dup_pct = (dup_count / total_rows * 100) if total_rows > 0 else 0
        outlier_pct = (outlier_count / total_rows * 100) if total_rows > 0 else 0
        avg_quality = sum(col_quality.values()) / len(col_quality) if col_quality else 0
        
        score = 100
        score -= avg_missing * 0.5
        score -= min(dup_pct * 2, 20)
        score -= min(outlier_pct, 10)
        score -= (1 - avg_quality) * 30
        
        self.logger.info(f"Quality score: {score:.2f}/100 "
                        f"(missing={avg_missing:.1f}%, dups={dup_pct:.1f}%, "
                        f"outliers={outlier_pct:.1f}%, col_quality={avg_quality:.3f})")
        
        if score >= 85:
            return DataQuality.EXCELLENT
        elif score >= 70:
            return DataQuality.GOOD
        elif score >= 50:
            return DataQuality.FAIR
        else:
            return DataQuality.POOR

    def _save_artifacts(self, report: DataQualityReport, proposed_actions: List[Dict[str, Any]]):
        """Save JSON artifacts."""
        artifacts_dir = Path(self.config["artifacts_dir"])
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        dataset_name = self.config["dataset_name"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = artifacts_dir / f"{dataset_name}_{timestamp}"
        
        save_json(report, f"{base}_dq_report.json")
        save_json(proposed_actions, f"{base}_clean_plan.json")
        
        self.logger.info(f"Artifacts saved: {base}_*.json")
'''

if __name__ == "__main__":
    output_path = "agents/inspector/inspector_agent.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(INSPECTOR_CONTENT)
    print(f"✅ Written {len(INSPECTOR_CONTENT)} characters to {output_path}")

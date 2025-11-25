from __future__ import annotations

from dataclasses import dataclass
<<<<<<< Updated upstream
=======
from typing import Dict, List, Any, Optional, Tuple
>>>>>>> Stashed changes
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class DataQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DataQualityReport:
    """Enhanced Report from the Inspector Agent"""
    overall_quality: DataQuality
    missing_values: Dict[str, float]
    data_types: Dict[str, str]
    duplicate_count: int
    outlier_count: int
    column_stats: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    timestamp: str

    # Enhanced fields – these now match InspectorAgent exactly
    cardinality_analysis: Dict[str, Dict[str, Any]]
    skewness_analysis: Dict[str, float]
    pattern_analysis: Dict[str, Dict[str, Any]]
    consistency_issues: Dict[str, Dict[str, Any]]
    column_quality_scores: Dict[str, float]
    outlier_details: Dict[str, int]
    proposed_actions: List[Dict[str, Any]]  # agentic: machine-readable actions


@dataclass
class CleaningReport:
    """Report from the Refiner Agent"""
    original_shape: Tuple[int, int]
    cleaned_shape: Tuple[int, int]
    actions_taken: List[str]
    columns_dropped: List[str]
    rows_removed: int
    missing_values_handled: Dict[str, str]
    timestamp: str


@dataclass
class InsightReport:
    """Report from the Insight Agent"""
    summary_statistics: Dict[str, Any]
    correlations: Optional[pd.DataFrame]
    plots_generated: List[str]
    key_insights: List[str]
    recommendations: List[str]
    timestamp: str


@dataclass
class PipelineResult:
    """Overall pipeline execution result"""
    status: AgentStatus
    input_file: str
    output_file: Optional[str]
    quality_report: Optional[DataQualityReport]
    cleaning_report: Optional[CleaningReport]
    insight_report: Optional[InsightReport]
    execution_time: float
    errors: List[str]

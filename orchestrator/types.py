from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
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
    # Enhanced fields
    cardinality_analysis: Optional[Dict[str, str]] = None
    skewness_analysis: Optional[Dict[str, float]] = None
    pattern_analysis: Optional[Dict[str, Dict[str, Any]]] = None
    consistency_issues: Optional[Dict[str, List[str]]] = None
    column_quality_scores: Optional[Dict[str, float]] = None
    outlier_details: Optional[Dict[str, Dict[str, Any]]] = None
    proposed_actions: Optional[List[Dict[str, Any]]] = None  # Agentic: machine-readable actions


@dataclass
class CleaningReport:
    """Report from the Refiner Agent"""
    original_shape: tuple
    cleaned_shape: tuple
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

"""
Utility functions for Streamlit UI
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


def save_uploaded_file(uploaded_file, target_dir: str) -> str:
    """
    Save uploaded file to target directory

    Args:
        uploaded_file: Streamlit UploadedFile object
        target_dir: Directory to save file

    Returns:
        Path to saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(target_dir, uploaded_file.name)

    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def load_pipeline_results(artifacts_dir: str = "data/artifacts") -> Optional[Dict[str, Any]]:
    """
    Load the latest pipeline results from artifacts directory

    Args:
        artifacts_dir: Directory containing artifacts

    Returns:
        Dictionary with pipeline results or None
    """
    artifacts_path = Path(artifacts_dir)

    if not artifacts_path.exists():
        return None

    results = {}

    # Load data quality report
    dq_files = list(artifacts_path.glob("*_dq_report.json"))
    if dq_files:
        latest_dq = max(dq_files, key=os.path.getctime)
        with open(latest_dq, 'r') as f:
            results['quality_report'] = json.load(f)

    # Load cleaning plan
    clean_files = list(artifacts_path.glob("*_clean_plan.json"))
    if clean_files:
        latest_clean = max(clean_files, key=os.path.getctime)
        with open(latest_clean, 'r') as f:
            results['clean_plan'] = json.load(f)

    # Get visualization files
    viz_files = list(artifacts_path.glob("*.png")) + list(artifacts_path.glob("*.html"))
    results['visualizations'] = [str(f) for f in viz_files]

    return results if results else None


def get_available_visualizations(artifacts_dir: str = "data/artifacts") -> List[str]:
    """
    Get list of available visualization files

    Args:
        artifacts_dir: Directory containing artifacts

    Returns:
        List of visualization file paths
    """
    artifacts_path = Path(artifacts_dir)

    if not artifacts_path.exists():
        return []

    viz_files = []

    # Get image files
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        viz_files.extend(artifacts_path.glob(ext))

    # Sort by creation time
    viz_files.sort(key=os.path.getctime, reverse=True)

    return [str(f) for f in viz_files]


def create_custom_visualization(
    data: pd.DataFrame,
    chart_type: str,
    params: Dict[str, Any]
) -> Optional[Any]:
    """
    Create custom visualization based on parameters

    Args:
        data: DataFrame to visualize
        chart_type: Type of chart (scatter, bar, line, etc.)
        params: Chart parameters

    Returns:
        Plotly figure or None
    """
    import plotly.express as px

    try:
        if chart_type == 'scatter':
            fig = px.scatter(
                data,
                x=params.get('x'),
                y=params.get('y'),
                color=params.get('color'),
                title=params.get('title', 'Scatter Plot')
            )
        elif chart_type == 'bar':
            fig = px.bar(
                data,
                x=params.get('x'),
                y=params.get('y'),
                title=params.get('title', 'Bar Chart')
            )
        elif chart_type == 'line':
            fig = px.line(
                data,
                x=params.get('x'),
                y=params.get('y'),
                title=params.get('title', 'Line Chart')
            )
        elif chart_type == 'histogram':
            fig = px.histogram(
                data,
                x=params.get('x'),
                nbins=params.get('bins', 30),
                title=params.get('title', 'Histogram')
            )
        elif chart_type == 'box':
            fig = px.box(
                data,
                x=params.get('x'),
                y=params.get('y'),
                title=params.get('title', 'Box Plot')
            )
        else:
            return None

        return fig

    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_column_info(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Get detailed information about DataFrame columns

    Args:
        data: DataFrame to analyze

    Returns:
        Dictionary with column information
    """
    info = {
        'total_columns': len(data.columns),
        'numeric_columns': data.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': data.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime_columns': data.select_dtypes(include=['datetime']).columns.tolist(),
        'column_types': data.dtypes.to_dict(),
        'missing_counts': data.isnull().sum().to_dict(),
        'unique_counts': data.nunique().to_dict()
    }

    return info


def create_summary_stats(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create summary statistics DataFrame

    Args:
        data: DataFrame to summarize

    Returns:
        Summary statistics DataFrame
    """
    numeric_data = data.select_dtypes(include=['number'])

    if numeric_data.empty:
        return pd.DataFrame()

    summary = numeric_data.describe().T
    summary['missing'] = data[numeric_data.columns].isnull().sum()
    summary['missing_pct'] = (summary['missing'] / len(data) * 100).round(2)

    return summary


def export_to_excel(data: pd.DataFrame, filename: str) -> str:
    """
    Export DataFrame to Excel file

    Args:
        data: DataFrame to export
        filename: Output filename

    Returns:
        Path to exported file
    """
    output_dir = "data/exports"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"{filename}_{timestamp}.xlsx")

    data.to_excel(output_path, index=False)

    return output_path


def get_data_quality_summary(quality_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key metrics from quality report

    Args:
        quality_report: Quality report dictionary

    Returns:
        Summary dictionary
    """
    if not quality_report:
        return {}

    summary = {
        'overall_quality': quality_report.get('overall_quality', 'unknown'),
        'total_missing': sum(quality_report.get('missing_values', {}).values()),
        'duplicate_count': quality_report.get('duplicate_count', 0),
        'outlier_count': quality_report.get('outlier_count', 0),
        'columns_with_issues': len([
            k for k, v in quality_report.get('missing_values', {}).items() if v > 0
        ])
    }

    return summary


def parse_cleaning_actions(actions: List[str]) -> Dict[str, int]:
    """
    Parse cleaning actions into categories

    Args:
        actions: List of action strings

    Returns:
        Dictionary with action counts
    """
    action_counts = {
        'dropped_columns': 0,
        'imputed': 0,
        'removed_duplicates': 0,
        'handled_outliers': 0,
        'converted_types': 0
    }

    for action in actions:
        action_lower = action.lower()

        if 'drop' in action_lower and 'column' in action_lower:
            action_counts['dropped_columns'] += 1
        elif 'impute' in action_lower or 'fill' in action_lower:
            action_counts['imputed'] += 1
        elif 'duplicate' in action_lower:
            action_counts['removed_duplicates'] += 1
        elif 'outlier' in action_lower:
            action_counts['handled_outliers'] += 1
        elif 'convert' in action_lower or 'type' in action_lower:
            action_counts['converted_types'] += 1

    return action_counts


def generate_recommendations(quality_report: Dict[str, Any], cleaning_report: Dict[str, Any]) -> List[str]:
    """
    Generate recommendations based on pipeline results

    Args:
        quality_report: Quality assessment report
        cleaning_report: Cleaning report

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Quality-based recommendations
    if quality_report:
        quality = quality_report.get('overall_quality', '').lower()

        if quality == 'poor':
            recommendations.append("⚠️ Data quality is poor. Consider additional manual review.")
        elif quality == 'fair':
            recommendations.append("ℹ️ Data quality is fair. Some issues remain that may need attention.")

        missing_pct = sum(quality_report.get('missing_values', {}).values()) / (
            len(quality_report.get('missing_values', {})) + 1
        )

        if missing_pct > 0.3:
            recommendations.append("📊 High missing data percentage. Consider data collection improvements.")

        if quality_report.get('duplicate_count', 0) > 0:
            recommendations.append("🔄 Duplicates found. Review for data entry issues.")

    # Cleaning-based recommendations
    if cleaning_report:
        if cleaning_report.get('columns_dropped', 0) > 0:
            recommendations.append(f"📉 {cleaning_report['columns_dropped']} columns were dropped. Review if needed.")

        if cleaning_report.get('rows_removed', 0) > 0:
            recommendations.append(f"🗑️ {cleaning_report['rows_removed']} rows were removed. Verify data loss is acceptable.")

    # General recommendations
    if not recommendations:
        recommendations.append("✅ Data appears to be in good condition. Proceed with analysis.")

    return recommendations

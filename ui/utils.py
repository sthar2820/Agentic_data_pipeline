"""
Utility functions for Streamlit UI
Handles file operations, data loading, and visualization management
"""

import os
import pandas as pd
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px


def save_uploaded_file(uploaded_file, destination_folder: str = "data/raw") -> str:
    """
    Save uploaded file to the specified folder

    Args:
        uploaded_file: Streamlit UploadedFile object
        destination_folder: Folder path to save the file

    Returns:
        str: Full path to the saved file
    """
    # Create destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    # Create file path
    file_path = os.path.join(destination_folder, uploaded_file.name)

    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def load_pipeline_results(artifacts_dir: str = "data/artifacts") -> Optional[Dict[str, Any]]:
    """
    Load the most recent pipeline results from artifacts directory

    Args:
        artifacts_dir: Directory containing pipeline artifacts

    Returns:
        Dict containing pipeline results or None if not found
    """
    try:
        artifacts_path = Path(artifacts_dir)

        # Find the most recent quality report
        report_files = list(artifacts_path.glob("*_dq_report.json"))
        if not report_files:
            return None

        latest_report = max(report_files, key=os.path.getctime)

        with open(latest_report, 'r') as f:
            results = json.load(f)

        return results
    except Exception as e:
        print(f"Error loading pipeline results: {e}")
        return None


def get_available_visualizations(artifacts_dir: str = "data/artifacts") -> List[str]:
    """
    Get list of available visualization files

    Args:
        artifacts_dir: Directory containing visualization artifacts

    Returns:
        List of visualization file paths
    """
    try:
        artifacts_path = Path(artifacts_dir)

        # Find all PNG visualization files
        viz_files = list(artifacts_path.glob("*.png"))

        # Sort by creation time (newest first)
        viz_files.sort(key=os.path.getctime, reverse=True)

        return [str(f) for f in viz_files]
    except Exception as e:
        print(f"Error getting visualizations: {e}")
        return []


def create_custom_visualization(
    data: pd.DataFrame,
    viz_type: str,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    color_col: Optional[str] = None,
    **kwargs
) -> Optional[go.Figure]:
    """
    Create a custom Plotly visualization

    Args:
        data: DataFrame to visualize
        viz_type: Type of visualization (scatter, line, bar, histogram, box, etc.)
        x_col: Column for x-axis
        y_col: Column for y-axis
        color_col: Column for color grouping
        **kwargs: Additional parameters for Plotly

    Returns:
        Plotly Figure object or None if error
    """
    try:
        if viz_type == "scatter":
            fig = px.scatter(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{x_col} vs {y_col}" if x_col and y_col else "Scatter Plot",
                template="plotly_white",
                **kwargs
            )
        elif viz_type == "line":
            fig = px.line(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{y_col} over {x_col}" if x_col and y_col else "Line Chart",
                template="plotly_white",
                **kwargs
            )
        elif viz_type == "bar":
            fig = px.bar(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{x_col} Bar Chart" if x_col else "Bar Chart",
                template="plotly_white",
                **kwargs
            )
        elif viz_type == "histogram":
            fig = px.histogram(
                data,
                x=x_col,
                color=color_col,
                title=f"Distribution of {x_col}" if x_col else "Histogram",
                template="plotly_white",
                **kwargs
            )
        elif viz_type == "box":
            fig = px.box(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"Box Plot of {y_col}" if y_col else "Box Plot",
                template="plotly_white",
                **kwargs
            )
        elif viz_type == "violin":
            fig = px.violin(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"Violin Plot of {y_col}" if y_col else "Violin Plot",
                template="plotly_white",
                box=True,
                **kwargs
            )
        elif viz_type == "heatmap":
            # For heatmap, use correlation matrix of numeric columns
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) < 2:
                return None

            corr_matrix = data[numeric_cols].corr()
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                aspect='auto',
                title="Correlation Heatmap",
                template="plotly_white",
                color_continuous_scale='RdBu_r',
                **kwargs
            )
        elif viz_type == "pie":
            if not x_col:
                return None

            value_counts = data[x_col].value_counts().head(10)
            fig = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=f"Distribution of {x_col}",
                template="plotly_white",
                **kwargs
            )
        else:
            return None

        # Update layout for better appearance
        fig.update_layout(
            font=dict(size=12),
            hovermode='closest',
            showlegend=True
        )

        return fig

    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None


def load_cleaned_data(cleaned_dir: str = "data/cleaned") -> Optional[pd.DataFrame]:
    """
    Load the most recent cleaned data file

    Args:
        cleaned_dir: Directory containing cleaned data files

    Returns:
        DataFrame or None if not found
    """
    try:
        cleaned_path = Path(cleaned_dir)

        # Find the most recent cleaned CSV file
        csv_files = list(cleaned_path.glob("*.csv"))
        if not csv_files:
            return None

        latest_csv = max(csv_files, key=os.path.getctime)

        return pd.read_csv(latest_csv)

    except Exception as e:
        print(f"Error loading cleaned data: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_column_info(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Get detailed information about DataFrame columns

    Args:
        data: DataFrame to analyze

    Returns:
        Dict with column information
    """
    info = {
        'total_columns': len(data.columns),
        'numeric_columns': data.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': data.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime_columns': data.select_dtypes(include=['datetime']).columns.tolist(),
        'missing_values': data.isnull().sum().to_dict(),
        'dtypes': data.dtypes.astype(str).to_dict()
    }
    return info


def export_visualization(fig: go.Figure, filename: str, format: str = 'png') -> bool:
    """
    Export Plotly figure to file

    Args:
        fig: Plotly Figure object
        filename: Output filename
        format: Export format ('png', 'html', 'svg')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if format == 'html':
            fig.write_html(filename)
        elif format == 'png':
            fig.write_image(filename)
        elif format == 'svg':
            fig.write_image(filename, format='svg')
        else:
            return False
        return True
    except Exception as e:
        print(f"Error exporting visualization: {e}")
        return False

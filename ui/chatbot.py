"""
RAG-based Visualization Chatbot
Uses pattern matching and data analysis to generate appropriate visualizations
based on user queries
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from typing import Dict, Any, Optional, List
import numpy as np


class VisualizationChatbot:
    """
    Intelligent chatbot for generating visualizations based on natural language queries
    Uses RAG-like pattern matching to understand user intent
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        self.categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
        self.all_columns = data.columns.tolist()

        # Knowledge base for visualization patterns
        self.visualization_patterns = {
            'scatter': {
                'keywords': ['scatter', 'scatter plot', 'relationship', 'correlation', 'vs'],
                'requires': ['x', 'y'],
                'function': self.create_scatter_plot
            },
            'line': {
                'keywords': ['line', 'line chart', 'trend', 'over time', 'time series'],
                'requires': ['x', 'y'],
                'function': self.create_line_chart
            },
            'bar': {
                'keywords': ['bar', 'bar chart', 'compare', 'comparison', 'top'],
                'requires': ['x'],
                'function': self.create_bar_chart
            },
            'histogram': {
                'keywords': ['histogram', 'distribution', 'frequency'],
                'requires': ['x'],
                'function': self.create_histogram
            },
            'box': {
                'keywords': ['box plot', 'box', 'outliers', 'quartile'],
                'requires': ['y'],
                'function': self.create_box_plot
            },
            'heatmap': {
                'keywords': ['heatmap', 'correlation', 'heat map'],
                'requires': [],
                'function': self.create_heatmap
            },
            'pie': {
                'keywords': ['pie', 'pie chart', 'proportion', 'percentage'],
                'requires': ['values'],
                'function': self.create_pie_chart
            },
            'violin': {
                'keywords': ['violin', 'violin plot', 'density'],
                'requires': ['y'],
                'function': self.create_violin_plot
            }
        }

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query and generate appropriate visualization

        Returns:
            Dict with 'message' and optionally 'figure'
        """
        query_lower = query.lower()

        # Detect visualization type
        viz_type = self._detect_visualization_type(query_lower)

        if not viz_type:
            return {
                'message': "I'm not sure what visualization you want. Try asking for: scatter plot, bar chart, histogram, box plot, or heatmap.",
                'figure': None
            }

        # Extract column names from query
        columns = self._extract_columns(query_lower)

        # Generate visualization
        try:
            viz_func = self.visualization_patterns[viz_type]['function']
            figure = viz_func(columns, query)

            return {
                'message': f"Here's your {viz_type} chart!",
                'figure': figure
            }
        except Exception as e:
            return {
                'message': f"I couldn't create that visualization. Error: {str(e)}. Try being more specific about which columns to use.",
                'figure': None
            }

    def _detect_visualization_type(self, query: str) -> Optional[str]:
        """Detect which visualization type the user wants"""

        for viz_type, pattern in self.visualization_patterns.items():
            for keyword in pattern['keywords']:
                if keyword in query:
                    return viz_type

        return None

    def _extract_columns(self, query: str) -> List[str]:
        """Extract column names mentioned in the query"""

        mentioned_columns = []

        for col in self.all_columns:
            # Match exact column name or variations
            col_lower = col.lower().replace('_', ' ').replace('-', ' ')

            if col_lower in query or col.lower() in query:
                mentioned_columns.append(col)

        return mentioned_columns

    def _get_top_n_categories(self, column: str, n: int = 10) -> pd.DataFrame:
        """Get top N categories from a column"""
        return self.data[column].value_counts().head(n)

    def create_scatter_plot(self, columns: List[str], query: str) -> go.Figure:
        """Create scatter plot"""

        # Extract x and y from columns or use first two numeric
        if len(columns) >= 2:
            x_col, y_col = columns[0], columns[1]
        elif len(self.numeric_columns) >= 2:
            x_col, y_col = self.numeric_columns[0], self.numeric_columns[1]
        else:
            raise ValueError("Need at least 2 numeric columns for scatter plot")

        # Check for color grouping
        color_col = None
        if len(columns) > 2:
            color_col = columns[2]

        fig = px.scatter(
            self.data,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"{x_col} vs {y_col}",
            template="plotly_white",
            opacity=0.7
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black"),
            hovermode='closest'
        )

        return fig

    def create_line_chart(self, columns: List[str], query: str) -> go.Figure:
        """Create line chart"""

        if len(columns) >= 2:
            x_col, y_col = columns[0], columns[1]
        elif len(self.numeric_columns) >= 2:
            x_col, y_col = self.numeric_columns[0], self.numeric_columns[1]
        else:
            raise ValueError("Need at least 2 columns for line chart")

        fig = px.line(
            self.data,
            x=x_col,
            y=y_col,
            title=f"{y_col} over {x_col}",
            template="plotly_white"
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black")
        )

        return fig

    def create_bar_chart(self, columns: List[str], query: str) -> go.Figure:
        """Create bar chart"""

        # Check for "top N" pattern
        top_n = 10
        match = re.search(r'top\s+(\d+)', query)
        if match:
            top_n = int(match.group(1))

        if columns:
            col = columns[0]
        elif self.categorical_columns:
            col = self.categorical_columns[0]
        else:
            col = self.all_columns[0]

        # Get value counts
        value_counts = self.data[col].value_counts().head(top_n)

        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"Top {top_n} {col}",
            labels={'x': col, 'y': 'Count'},
            template="plotly_white"
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black"),
            xaxis_tickangle=-45
        )

        return fig

    def create_histogram(self, columns: List[str], query: str) -> go.Figure:
        """Create histogram"""

        if columns:
            col = columns[0]
        elif self.numeric_columns:
            col = self.numeric_columns[0]
        else:
            raise ValueError("Need a numeric column for histogram")

        fig = px.histogram(
            self.data,
            x=col,
            title=f"Distribution of {col}",
            template="plotly_white",
            nbins=30
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black")
        )

        return fig

    def create_box_plot(self, columns: List[str], query: str) -> go.Figure:
        """Create box plot"""

        if columns:
            y_col = columns[0]
        elif self.numeric_columns:
            y_col = self.numeric_columns[0]
        else:
            raise ValueError("Need a numeric column for box plot")

        # Check if we should group by a category
        x_col = None
        if len(columns) > 1:
            x_col = columns[1]

        fig = px.box(
            self.data,
            x=x_col,
            y=y_col,
            title=f"Box Plot of {y_col}",
            template="plotly_white"
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black")
        )

        return fig

    def create_heatmap(self, columns: List[str], query: str) -> go.Figure:
        """Create correlation heatmap"""

        # Use specified columns or all numeric columns
        if columns:
            numeric_cols = [c for c in columns if c in self.numeric_columns]
        else:
            numeric_cols = self.numeric_columns

        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for heatmap")

        # Calculate correlation
        corr_matrix = self.data[numeric_cols].corr()

        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect='auto',
            title="Correlation Heatmap",
            template="plotly_white",
            color_continuous_scale='RdBu_r'
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black")
        )

        return fig

    def create_pie_chart(self, columns: List[str], query: str) -> go.Figure:
        """Create pie chart"""

        if columns:
            col = columns[0]
        elif self.categorical_columns:
            col = self.categorical_columns[0]
        else:
            col = self.all_columns[0]

        # Get top categories
        value_counts = self.data[col].value_counts().head(10)

        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"Distribution of {col}",
            template="plotly_white"
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black")
        )

        return fig

    def create_violin_plot(self, columns: List[str], query: str) -> go.Figure:
        """Create violin plot"""

        if columns:
            y_col = columns[0]
        elif self.numeric_columns:
            y_col = self.numeric_columns[0]
        else:
            raise ValueError("Need a numeric column for violin plot")

        # Check for grouping
        x_col = None
        if len(columns) > 1:
            x_col = columns[1]

        fig = px.violin(
            self.data,
            x=x_col,
            y=y_col,
            title=f"Violin Plot of {y_col}",
            template="plotly_white",
            box=True
        )

        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16, family="Arial Black")
        )

        return fig

    def get_suggestions(self) -> List[str]:
        """Get suggestion queries based on available data"""

        suggestions = []

        if len(self.numeric_columns) >= 2:
            suggestions.append(f"Create a scatter plot of {self.numeric_columns[0]} vs {self.numeric_columns[1]}")
            suggestions.append(f"Show correlation heatmap")

        if self.categorical_columns:
            suggestions.append(f"Show bar chart of top 10 {self.categorical_columns[0]}")

        if self.numeric_columns:
            suggestions.append(f"Create histogram of {self.numeric_columns[0]}")
            suggestions.append(f"Show box plot of {self.numeric_columns[0]}")

        return suggestions

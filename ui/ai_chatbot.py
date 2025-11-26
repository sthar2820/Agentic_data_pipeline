"""
AI-Powered Visualization Chatbot using Google Gemini
Advanced natural language understanding for intelligent visualization generation
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import json
import re
from typing import Dict, Any, Optional, List
import numpy as np


class AIVisualizationChatbot:
    """
    AI-powered chatbot for generating visualizations using Google Gemini
    Provides advanced natural language understanding and intelligent chart recommendations
    """

    def __init__(self, data: pd.DataFrame, api_key: str):
        self.data = data
        self.numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        self.categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
        self.all_columns = data.columns.tolist()

        # Configure Gemini AI
        genai.configure(api_key=api_key)
        # Use Gemini 2.5 Pro for advanced generation
        self.model = genai.GenerativeModel('gemini-2.5-pro')

        # Initialize conversation history
        self.conversation_history = []

        # Build data context for AI
        self.data_context = self._build_data_context()

    def _build_data_context(self) -> str:
        """Build comprehensive data context for AI"""
        context = f"""
Dataset Information:
- Total Rows: {len(self.data):,}
- Total Columns: {len(self.data.columns)}

Numeric Columns ({len(self.numeric_columns)}):
{', '.join(self.numeric_columns) if self.numeric_columns else 'None'}

Categorical Columns ({len(self.categorical_columns)}):
{', '.join(self.categorical_columns) if self.categorical_columns else 'None'}

All Columns:
{', '.join(self.all_columns)}

Sample Data Statistics:
{self.data.describe().to_string() if not self.data.select_dtypes(include=['number']).empty else 'No numeric data'}
"""
        return context

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query using Gemini AI to understand intent and generate visualization

        Args:
            user_query: Natural language query from user

        Returns:
            Dict with 'message' and optionally 'figure'
        """
        try:
            # Create AI prompt for visualization understanding
            prompt = self._create_visualization_prompt(user_query)

            # Get AI response
            response = self.model.generate_content(prompt)

            # Parse AI response
            viz_config = self._parse_ai_response(response.text)

            if not viz_config:
                return {
                    'message': "I couldn't understand what visualization you want. Could you be more specific?",
                    'figure': None
                }

            # Generate visualization based on AI recommendation
            figure = self._generate_visualization(viz_config)

            # Store in conversation history
            self.conversation_history.append({
                'user': user_query,
                'config': viz_config,
                'success': figure is not None
            })

            if figure:
                return {
                    'message': f"Here's your {viz_config['type']} visualization! {viz_config.get('explanation', '')}",
                    'figure': figure
                }
            else:
                return {
                    'message': "I understood your request but couldn't create the visualization. Try being more specific about the columns.",
                    'figure': None
                }

        except Exception as e:
            return {
                'message': f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your request.",
                'figure': None
            }

    def _create_visualization_prompt(self, user_query: str) -> str:
        """Create detailed prompt for Gemini AI"""

        prompt = f"""You are an expert data visualization assistant. Analyze the user's request and recommend the best visualization.

{self.data_context}

User Request: "{user_query}"

Your task:
1. Understand what the user wants to visualize
2. Recommend the best chart type from: scatter, line, bar, histogram, box, violin, heatmap, pie
3. Identify which columns should be used (must be from the available columns above)
4. Provide a brief explanation of why this visualization is appropriate

Respond ONLY with a JSON object in this exact format:
{{
    "type": "chart_type",
    "columns": {{
        "x": "column_name_or_null",
        "y": "column_name_or_null",
        "color": "column_name_or_null"
    }},
    "explanation": "Brief explanation of the visualization",
    "parameters": {{
        "bins": 30,
        "top_n": 10
    }}
}}

Rules:
- Column names MUST exactly match those in the available columns list
- For histograms, only 'x' is needed
- For bar charts, 'x' is the category, 'y' can be null for count
- For heatmaps, columns can be null (will use all numeric columns)
- Keep explanation under 50 words
- Only respond with valid JSON, no other text

Example responses:

User: "scatter plot of price vs discount"
Response:
{{
    "type": "scatter",
    "columns": {{"x": "price", "y": "discount", "color": null}},
    "explanation": "Scatter plot shows the relationship between price and discount, revealing potential correlations.",
    "parameters": {{}}
}}

User: "top 10 products"
Response:
{{
    "type": "bar",
    "columns": {{"x": "goods-title-link", "y": null, "color": null}},
    "explanation": "Bar chart displaying the frequency of top 10 products.",
    "parameters": {{"top_n": 10}}
}}

Now analyze: "{user_query}"
"""
        return prompt

    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from Gemini AI"""
        try:
            # Extract JSON from response (handle potential markdown formatting)
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                config = json.loads(json_str)
                return config
            return None
        except json.JSONDecodeError:
            return None

    def _generate_visualization(self, config: Dict[str, Any]) -> Optional[go.Figure]:
        """Generate visualization based on AI-recommended configuration"""

        viz_type = config.get('type', '').lower()
        columns = config.get('columns', {})
        params = config.get('parameters', {})

        try:
            if viz_type == 'scatter':
                return self._create_scatter(columns, params)
            elif viz_type == 'line':
                return self._create_line(columns, params)
            elif viz_type == 'bar':
                return self._create_bar(columns, params)
            elif viz_type == 'histogram':
                return self._create_histogram(columns, params)
            elif viz_type == 'box':
                return self._create_box(columns, params)
            elif viz_type == 'violin':
                return self._create_violin(columns, params)
            elif viz_type == 'heatmap':
                return self._create_heatmap(columns, params)
            elif viz_type == 'pie':
                return self._create_pie(columns, params)
            else:
                return None
        except Exception as e:
            print(f"Visualization error: {e}")
            return None

    def _create_scatter(self, columns: Dict, params: Dict) -> go.Figure:
        """Create scatter plot"""
        x_col = columns.get('x')
        y_col = columns.get('y')
        color_col = columns.get('color')

        if not x_col or not y_col:
            # Use first two numeric columns
            if len(self.numeric_columns) >= 2:
                x_col = self.numeric_columns[0]
                y_col = self.numeric_columns[1]
            else:
                return None

        fig = px.scatter(
            self.data,
            x=x_col,
            y=y_col,
            color=color_col if color_col else None,
            title=f"{x_col} vs {y_col}",
            template="plotly_white",
            opacity=0.7
        )
        fig.update_layout(font=dict(size=12), hovermode='closest')
        return fig

    def _create_line(self, columns: Dict, params: Dict) -> go.Figure:
        """Create line chart"""
        x_col = columns.get('x') or (self.all_columns[0] if self.all_columns else None)
        y_col = columns.get('y') or (self.numeric_columns[0] if self.numeric_columns else None)

        if not x_col or not y_col:
            return None

        fig = px.line(
            self.data,
            x=x_col,
            y=y_col,
            title=f"{y_col} over {x_col}",
            template="plotly_white"
        )
        return fig

    def _create_bar(self, columns: Dict, params: Dict) -> go.Figure:
        """Create bar chart"""
        x_col = columns.get('x') or (self.categorical_columns[0] if self.categorical_columns else self.all_columns[0])
        top_n = params.get('top_n', 10)

        if not x_col:
            return None

        value_counts = self.data[x_col].value_counts().head(top_n)

        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"Top {top_n} {x_col}",
            labels={'x': x_col, 'y': 'Count'},
            template="plotly_white"
        )
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def _create_histogram(self, columns: Dict, params: Dict) -> go.Figure:
        """Create histogram"""
        x_col = columns.get('x') or (self.numeric_columns[0] if self.numeric_columns else None)
        bins = params.get('bins', 30)

        if not x_col:
            return None

        fig = px.histogram(
            self.data,
            x=x_col,
            title=f"Distribution of {x_col}",
            template="plotly_white",
            nbins=bins
        )
        return fig

    def _create_box(self, columns: Dict, params: Dict) -> go.Figure:
        """Create box plot"""
        y_col = columns.get('y') or columns.get('x') or (self.numeric_columns[0] if self.numeric_columns else None)
        x_col = columns.get('color')

        if not y_col:
            return None

        fig = px.box(
            self.data,
            x=x_col if x_col else None,
            y=y_col,
            title=f"Box Plot of {y_col}",
            template="plotly_white"
        )
        return fig

    def _create_violin(self, columns: Dict, params: Dict) -> go.Figure:
        """Create violin plot"""
        y_col = columns.get('y') or columns.get('x') or (self.numeric_columns[0] if self.numeric_columns else None)
        x_col = columns.get('color')

        if not y_col:
            return None

        fig = px.violin(
            self.data,
            x=x_col if x_col else None,
            y=y_col,
            title=f"Violin Plot of {y_col}",
            template="plotly_white",
            box=True
        )
        return fig

    def _create_heatmap(self, columns: Dict, params: Dict) -> go.Figure:
        """Create correlation heatmap"""
        numeric_cols = self.numeric_columns

        if len(numeric_cols) < 2:
            return None

        corr_matrix = self.data[numeric_cols].corr()

        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect='auto',
            title="Correlation Heatmap",
            template="plotly_white",
            color_continuous_scale='RdBu_r'
        )
        return fig

    def _create_pie(self, columns: Dict, params: Dict) -> go.Figure:
        """Create pie chart"""
        x_col = columns.get('x') or (self.categorical_columns[0] if self.categorical_columns else self.all_columns[0])
        top_n = params.get('top_n', 10)

        if not x_col:
            return None

        value_counts = self.data[x_col].value_counts().head(top_n)

        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"Distribution of {x_col}",
            template="plotly_white"
        )
        return fig

    def get_smart_suggestions(self) -> List[str]:
        """Get AI-powered suggestions based on data"""
        try:
            prompt = f"""Given this dataset information, suggest 5 interesting visualizations to explore:

{self.data_context}

Provide 5 natural language queries that would create insightful visualizations.
Respond with only the queries, one per line, no numbering or explanation.

Example format:
Show correlation heatmap of all numeric columns
Create scatter plot of X vs Y colored by category
Display top 10 products by frequency
"""

            response = self.model.generate_content(prompt)
            suggestions = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            return suggestions[:5]
        except:
            return [
                "Show me the correlation between all numeric columns",
                f"Create a scatter plot of {self.numeric_columns[0]} vs {self.numeric_columns[1]}" if len(self.numeric_columns) >= 2 else "Show data distribution",
                f"Display top 10 {self.categorical_columns[0]}" if self.categorical_columns else "Show data overview",
                f"Create histogram of {self.numeric_columns[0]}" if self.numeric_columns else "Visualize data",
                "Show me interesting patterns in the data"
            ]

    def get_conversation_summary(self) -> str:
        """Get summary of conversation history"""
        if not self.conversation_history:
            return "No visualizations created yet."

        total = len(self.conversation_history)
        successful = sum(1 for item in self.conversation_history if item['success'])

        return f"Created {successful} out of {total} requested visualizations."

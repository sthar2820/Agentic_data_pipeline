#!/usr/bin/env python3
"""
Streamlit Dashboard for Agentic Data Pipeline
Features:
- File upload and processing
- Real-time pipeline execution
- RAG-based chatbot for visualization requests
- Interactive visualization display
"""

import streamlit as st
import pandas as pd
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.pipeline import DataPipeline
from ui.chatbot import VisualizationChatbot
from ui.ai_chatbot import AIVisualizationChatbot
from ui.utils import (
    save_uploaded_file,
    load_pipeline_results,
    get_available_visualizations,
    create_custom_visualization
)

# Page configuration
st.set_page_config(
    page_title="Agentic Data Pipeline",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_result' not in st.session_state:
    st.session_state.pipeline_result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'use_ai_chatbot' not in st.session_state:
    st.session_state.use_ai_chatbot = True  # Use AI by default
if 'show_chatbot_modal' not in st.session_state:
    st.session_state.show_chatbot_modal = False
if 'custom_visualizations' not in st.session_state:
    st.session_state.custom_visualizations = []
if 'show_sections' not in st.session_state:
    st.session_state.show_sections = {
        'executive_summary': True,
        'health_scorecard': True,
        'business_metrics': True,
        'feature_relationships': True,
        'statistical_summary': True,
        'interactive_explorer': True,
        'pipeline_insights': True
    }


def main():
    """Main application entry point"""

    # Header
    st.markdown('<h1 class="main-header">🤖 Agentic Data Pipeline</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 1.2rem;">'
        'AI-Powered Data Cleaning, Feature Engineering & Visualization'
        '</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/artificial-intelligence.png", width=150)
        st.markdown("## 📊 Pipeline Controls")

        # Agent configuration
        st.markdown("### Agent Configuration")
        enable_anomaly = st.checkbox("🔍 Anomaly Detection", value=True)
        enable_feature_eng = st.checkbox("⚙️ Feature Engineering", value=True)
        enable_reporter = st.checkbox("📊 Report Generation", value=True)

        st.markdown("---")

        # Pipeline status
        st.markdown("### 📈 Pipeline Status")
        if st.session_state.pipeline_result:
            result = st.session_state.pipeline_result
            st.success(f"✅ Status: {result.status.value.upper()}")
            st.info(f"⏱️ Time: {result.execution_time:.2f}s")
            if result.quality_report:
                quality = result.quality_report.overall_quality.value
                st.metric("Quality", quality.upper())
        else:
            st.info("No data processed yet")

        st.markdown("---")

        # Documentation
        st.markdown("### 📚 Documentation")
        st.markdown("[Quick Start Guide](QUICK_START.md)")
        st.markdown("[Improvements](IMPROVEMENTS.md)")
        st.markdown("[Test Results](TEST_RESULTS.md)")

    # Main content - Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload & Process",
        "📊 Results Dashboard",
        "💬 Visualization Chatbot",
        "📈 Custom Analytics"
    ])

    # Tab 1: Upload & Process
    with tab1:
        st.markdown("## 📤 Upload Your Data")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload a CSV file to process through the agentic pipeline"
            )

            if uploaded_file is not None:
                # Display file info
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
                st.markdown('</div>', unsafe_allow_html=True)

                # Preview data
                try:
                    df_preview = pd.read_csv(uploaded_file, nrows=5)
                    st.markdown("### 👀 Data Preview")
                    st.dataframe(df_preview, use_container_width=True)
                    st.info(f"Showing first 5 rows of {len(df_preview.columns)} columns")

                    # Reset file pointer
                    uploaded_file.seek(0)
                except Exception as e:
                    st.error(f"Error previewing file: {str(e)}")

        with col2:
            st.markdown("### 🎯 Pipeline Settings")
            st.info(
                f"**Enabled Agents:**\n\n"
                f"✅ Inspector\n\n"
                f"{'✅' if enable_anomaly else '❌'} Anomaly Detection\n\n"
                f"✅ Refiner\n\n"
                f"{'✅' if enable_feature_eng else '❌'} Feature Engineering\n\n"
                f"✅ Insight\n\n"
                f"{'✅' if enable_reporter else '❌'} Reporter"
            )

        # Process button
        if uploaded_file is not None:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
                    run_pipeline(uploaded_file, enable_anomaly, enable_feature_eng, enable_reporter)

    # Tab 2: Results Dashboard
    with tab2:
        display_results_dashboard()

    # Tab 3: Visualization Chatbot
    with tab3:
        display_chatbot_interface()

    # Tab 4: Custom Analytics
    with tab4:
        display_custom_analytics()


def run_pipeline(uploaded_file, enable_anomaly: bool, enable_feature_eng: bool, enable_reporter: bool):
    """Run the data pipeline on uploaded file"""

    with st.spinner("🤖 Pipeline running... This may take a few moments"):
        try:
            # Save uploaded file
            input_path = save_uploaded_file(uploaded_file, "data/raw")

            # Update configuration dynamically
            import yaml
            with open("configs/pipeline.yaml", 'r') as f:
                config = yaml.safe_load(f)

            config['agents']['anomaly_detector']['enabled'] = enable_anomaly
            config['agents']['feature_engineer']['enabled'] = enable_feature_eng
            config['agents']['reporter']['enabled'] = enable_reporter

            # Save updated config
            with open("configs/pipeline.yaml", 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            # Run pipeline
            pipeline = DataPipeline("configs/pipeline.yaml")

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Step 1/6: Running Inspector Agent...")
            progress_bar.progress(16)
            time.sleep(0.3)

            status_text.text("Step 2/6: Running Anomaly Detection...")
            progress_bar.progress(33)
            time.sleep(0.3)

            status_text.text("Step 3/6: Running Refiner Agent...")
            progress_bar.progress(50)

            result = pipeline.run_pipeline(input_path)

            status_text.text("Step 4/6: Running Feature Engineering...")
            progress_bar.progress(66)
            time.sleep(0.3)

            status_text.text("Step 5/6: Generating Insights...")
            progress_bar.progress(83)
            time.sleep(0.3)

            status_text.text("Step 6/6: Creating Report...")
            progress_bar.progress(100)

            # Store results
            st.session_state.pipeline_result = result

            # Load processed data
            if result.output_file and os.path.exists(result.output_file):
                st.session_state.processed_data = pd.read_csv(result.output_file)

            # Initialize chatbot with processed data
            if st.session_state.processed_data is not None:
                # Use AI chatbot if API key is available
                try:
                    if 'gemini' in st.secrets and st.secrets['gemini']['api_key']:
                        st.session_state.chatbot = AIVisualizationChatbot(
                            st.session_state.processed_data,
                            st.secrets['gemini']['api_key']
                        )
                        st.session_state.use_ai_chatbot = True
                    else:
                        st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)
                        st.session_state.use_ai_chatbot = False
                except:
                    # Fallback to pattern-based chatbot
                    st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)
                    st.session_state.use_ai_chatbot = False

            progress_bar.empty()
            status_text.empty()

            # Success message
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success(f"✅ Pipeline completed successfully in {result.execution_time:.2f} seconds!")
            st.markdown('</div>', unsafe_allow_html=True)

            # Show quick stats
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if result.quality_report:
                    st.metric("Data Quality", result.quality_report.overall_quality.value.upper())

            with col2:
                if result.cleaning_report:
                    st.metric("Rows Processed", f"{result.cleaning_report.cleaned_shape[0]:,}")

            with col3:
                if result.cleaning_report:
                    st.metric("Actions Taken", len(result.cleaning_report.actions_taken))

            with col4:
                if result.insight_report:
                    st.metric("Visualizations", len(result.insight_report.plots_generated))

            st.balloons()

        except Exception as e:
            st.error(f"❌ Pipeline failed: {str(e)}")
            import traceback
            with st.expander("Show error details"):
                st.code(traceback.format_exc())


def generate_executive_summary(df: pd.DataFrame, result: Any) -> str:
    """
    Generate a professional executive summary report for business stakeholders

    Args:
        df: Processed DataFrame
        result: Pipeline result object

    Returns:
        Formatted text summary
    """
    summary = []
    summary.append("="*80)
    summary.append("EXECUTIVE ANALYSIS SUMMARY")
    summary.append("Agentic Data Pipeline - Business Intelligence Report")
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("="*80)
    summary.append("")

    # === OVERVIEW SECTION ===
    summary.append("1. DATA OVERVIEW")
    summary.append("-" * 80)
    summary.append(f"   Total Records: {len(df):,}")
    summary.append(f"   Total Features: {len(df.columns)}")
    summary.append(f"   Processing Time: {result.execution_time:.2f} seconds")

    if result.cleaning_report:
        original_rows, original_cols = result.cleaning_report.original_shape
        summary.append(f"   Original Dataset: {original_rows:,} rows × {original_cols} columns")
        rows_change = len(df) - original_rows
        cols_change = len(df.columns) - original_cols
        summary.append(f"   Data Changes: {rows_change:+,} rows, {cols_change:+} features")
    summary.append("")

    # === DATA QUALITY SECTION ===
    summary.append("2. DATA QUALITY ASSESSMENT")
    summary.append("-" * 80)

    if result.quality_report:
        qr = result.quality_report
        quality = qr.overall_quality.value.upper()
        summary.append(f"   Overall Quality: {quality}")
        summary.append(f"   Duplicate Records: {qr.duplicate_count:,}")
        summary.append(f"   Outliers Detected: {qr.outlier_count:,}")

    # Missing values
    missing_total = df.isnull().sum().sum()
    missing_pct = (missing_total / (len(df) * len(df.columns))) * 100
    summary.append(f"   Missing Values: {missing_total:,} ({missing_pct:.2f}%)")

    # Completeness score
    completeness = 100 - missing_pct
    summary.append(f"   Data Completeness: {completeness:.1f}%")
    summary.append("")

    # === FEATURE ANALYSIS ===
    summary.append("3. FEATURE ANALYSIS")
    summary.append("-" * 80)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    summary.append(f"   Numeric Features: {len(numeric_cols)}")
    summary.append(f"   Categorical Features: {len(categorical_cols)}")

    if result.cleaning_report and result.cleaning_report.original_shape[1] < len(df.columns):
        new_features = len(df.columns) - result.cleaning_report.original_shape[1]
        summary.append(f"   Engineered Features: {new_features} created")
    summary.append("")

    # === KEY METRICS ===
    if numeric_cols:
        summary.append("4. KEY BUSINESS METRICS")
        summary.append("-" * 80)

        # Find primary metric
        key_metric = numeric_cols[0]
        for col in numeric_cols:
            if any(keyword in col.lower() for keyword in ['price', 'revenue', 'sales', 'amount', 'value', 'cost']):
                key_metric = col
                break

        summary.append(f"   Primary Metric: {key_metric.replace('_', ' ').title()}")
        summary.append(f"      Mean: {df[key_metric].mean():.2f}")
        summary.append(f"      Median: {df[key_metric].median():.2f}")
        summary.append(f"      Std Dev: {df[key_metric].std():.2f}")
        summary.append(f"      Range: {df[key_metric].min():.2f} - {df[key_metric].max():.2f}")

        # Variability assessment
        cv = df[key_metric].std() / df[key_metric].mean()
        if cv > 0.5:
            summary.append(f"      Variability: HIGH (CV={cv:.2f}) - Data shows significant spread")
        else:
            summary.append(f"      Variability: LOW (CV={cv:.2f}) - Data is relatively consistent")
        summary.append("")

    # === CORRELATIONS ===
    if len(numeric_cols) >= 2:
        summary.append("5. FEATURE RELATIONSHIPS")
        summary.append("-" * 80)

        corr_matrix = df[numeric_cols].corr()

        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corr.append({
                        'feat1': corr_matrix.columns[i],
                        'feat2': corr_matrix.columns[j],
                        'corr': corr_val
                    })

        if strong_corr:
            summary.append(f"   Strong Correlations Found: {len(strong_corr)}")
            for sc in strong_corr[:5]:  # Top 5
                direction = "Positive" if sc['corr'] > 0 else "Negative"
                summary.append(f"      • {sc['feat1']} ↔ {sc['feat2']}: {sc['corr']:.3f} ({direction})")
        else:
            summary.append("   No strong correlations detected (threshold: |r| > 0.7)")
        summary.append("")

    # === CATEGORICAL INSIGHTS ===
    if categorical_cols:
        summary.append("6. CATEGORICAL DATA INSIGHTS")
        summary.append("-" * 80)

        key_category = categorical_cols[0]
        value_counts = df[key_category].value_counts()

        summary.append(f"   Primary Category: {key_category.replace('_', ' ').title()}")
        summary.append(f"      Unique Values: {len(value_counts):,}")
        summary.append(f"      Top Category: {value_counts.index[0]} ({value_counts.iloc[0]:,} records, {value_counts.iloc[0]/len(df)*100:.1f}%)")

        # Diversity check
        if len(value_counts) > 20:
            summary.append(f"      Diversity: HIGH - {len(value_counts):,} unique categories")
        elif len(value_counts) < 5:
            summary.append(f"      Diversity: LOW - Only {len(value_counts)} unique categories")

        # Class balance
        top_pct = (value_counts.iloc[0] / len(df)) * 100
        if top_pct > 50:
            summary.append(f"      ⚠ Class Imbalance: Top category dominates at {top_pct:.1f}%")
        summary.append("")

    # === RECOMMENDATIONS ===
    summary.append("7. RECOMMENDATIONS")
    summary.append("-" * 80)

    recommendations = []

    if missing_pct > 10:
        recommendations.append("   • Consider imputation strategies for missing values")

    if result.quality_report and result.quality_report.outlier_count > len(df) * 0.05:
        recommendations.append("   • High outlier count detected - review data collection process")

    if categorical_cols and any((df[cat].value_counts().iloc[0] / len(df)) > 0.5 for cat in categorical_cols):
        recommendations.append("   • Class imbalance detected - consider resampling techniques for modeling")

    if len(strong_corr if 'strong_corr' in locals() else []) > 3:
        recommendations.append("   • Multiple strong correlations found - may indicate feature redundancy")

    if completeness > 95:
        recommendations.append("   • Excellent data completeness - dataset ready for analysis")

    if not recommendations:
        recommendations.append("   • Dataset appears healthy - proceed with modeling and analysis")

    summary.extend(recommendations)
    summary.append("")

    # === FOOTER ===
    summary.append("="*80)
    summary.append("END OF REPORT")
    summary.append("For detailed visualizations and interactive analysis, see the dashboard.")
    summary.append("="*80)

    return "\n".join(summary)


@st.dialog("💬 AI Visualization Chatbot", width="large")
def chatbot_modal():
    """Modal dialog for AI chatbot interaction"""

    # Show AI status badge
    if st.session_state.get('use_ai_chatbot', False):
        st.markdown("🤖 **Powered by Google Gemini 2.5 Pro** | Advanced AI with superior reasoning & generation")
    else:
        st.markdown("🔧 **Pattern-based mode** | Using keyword matching")

    st.markdown("Ask me to create custom visualizations from your processed data!")

    # Initialize chatbot if not already done
    if st.session_state.chatbot is None:
        try:
            if 'gemini' in st.secrets and st.secrets['gemini']['api_key']:
                st.session_state.chatbot = AIVisualizationChatbot(
                    st.session_state.processed_data,
                    st.secrets['gemini']['api_key']
                )
                st.session_state.use_ai_chatbot = True
            else:
                st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)
                st.session_state.use_ai_chatbot = False
        except:
            st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)
            st.session_state.use_ai_chatbot = False

    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(
                f'<div class="chat-message user-message">👤 <strong>You:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-message bot-message">🤖 <strong>Assistant:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )

            # Display visualization if present
            if 'visualization' in message and message['visualization'] is not None:
                try:
                    st.plotly_chart(message['visualization'], use_container_width=True)
                except Exception as e:
                    st.error(f"Could not display visualization: {str(e)}")

    st.markdown("---")

    # User input section - Using text_input + button for modal compatibility
    st.markdown("#### 💬 Ask a Question")

    col1, col2 = st.columns([4, 1])
    with col1:
        user_query = st.text_input(
            "Type your visualization request here...",
            placeholder="e.g., Show me the distribution of prices",
            key="chatbot_modal_input",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True, key="chatbot_modal_send")

    # Example queries and AI suggestions (below input)
    with st.expander("💡 Example Queries & Smart Suggestions"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Example Queries:**")
            st.markdown("""
            - "Create a scatter plot of price vs discount"
            - "Show me a bar chart of the top 10 categories"
            - "Create a histogram of prices"
            - "Show correlation heatmap"
            - "Create a box plot for numeric columns"
            """)

        with col2:
            if st.session_state.get('use_ai_chatbot', False):
                st.markdown("**✨ AI Smart Suggestions:**")
                try:
                    if hasattr(st.session_state.chatbot, 'get_smart_suggestions'):
                        suggestions = st.session_state.chatbot.get_smart_suggestions()
                        for i, suggestion in enumerate(suggestions[:3], 1):
                            st.markdown(f"{i}. {suggestion}")
                    else:
                        st.info("Smart suggestions available with AI chatbot")
                except:
                    st.info("Loading smart suggestions...")

    # Process query when Send button is clicked
    if send_button and user_query:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })

        # Get chatbot response
        with st.spinner("🤖 Creating visualization..."):
            response = st.session_state.chatbot.process_query(user_query)

            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response['message'],
                'visualization': response.get('figure')
            })

        st.rerun()


def display_results_dashboard():
    """Display PowerBI-style analytics dashboard with comprehensive visualizations"""

    # Header with chatbot button and controls
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("## 📊 Analytics Dashboard")
    with col2:
        if st.session_state.processed_data is not None:
            if st.button("⚙️ Customize Dashboard", use_container_width=True):
                st.session_state.show_customize = not st.session_state.get('show_customize', False)
    with col3:
        if st.session_state.processed_data is not None:
            if st.button("💬 Ask AI", type="primary", use_container_width=True):
                chatbot_modal()

    if st.session_state.pipeline_result is None:
        st.info("👆 Upload and process a file first to see results here")
        return

    result = st.session_state.pipeline_result
    df = st.session_state.processed_data

    # === DASHBOARD CUSTOMIZATION PANEL ===
    if st.session_state.get('show_customize', False):
        with st.expander("🎨 Dashboard Customization", expanded=True):
            st.markdown("### Toggle Dashboard Sections")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.session_state.show_sections['executive_summary'] = st.checkbox(
                    "📋 Executive Summary",
                    value=st.session_state.show_sections['executive_summary'],
                    key="toggle_exec_summary"
                )
                st.session_state.show_sections['health_scorecard'] = st.checkbox(
                    "🎯 Data Health Scorecard",
                    value=st.session_state.show_sections['health_scorecard'],
                    key="toggle_health"
                )
                st.session_state.show_sections['business_metrics'] = st.checkbox(
                    "📈 Business Metrics",
                    value=st.session_state.show_sections['business_metrics'],
                    key="toggle_business"
                )

            with col2:
                st.session_state.show_sections['feature_relationships'] = st.checkbox(
                    "🔗 Feature Relationships",
                    value=st.session_state.show_sections['feature_relationships'],
                    key="toggle_features"
                )
                st.session_state.show_sections['statistical_summary'] = st.checkbox(
                    "📈 Statistical Summary",
                    value=st.session_state.show_sections['statistical_summary'],
                    key="toggle_stats"
                )
                st.session_state.show_sections['interactive_explorer'] = st.checkbox(
                    "📊 Interactive Explorer",
                    value=st.session_state.show_sections['interactive_explorer'],
                    key="toggle_explorer"
                )

            with col3:
                st.session_state.show_sections['pipeline_insights'] = st.checkbox(
                    "🎨 Pipeline Insights",
                    value=st.session_state.show_sections['pipeline_insights'],
                    key="toggle_pipeline"
                )

            st.markdown("---")
            st.markdown("### 🆕 Add Custom Visualization")

            # Get column types
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            viz_col1, viz_col2, viz_col3, viz_col4 = st.columns(4)

            with viz_col1:
                viz_type = st.selectbox(
                    "Chart Type",
                    ["scatter", "line", "bar", "histogram", "box", "violin", "heatmap", "pie"],
                    key="new_viz_type"
                )

            with viz_col2:
                x_col = st.selectbox(
                    "X-Axis" if viz_type != "pie" else "Column",
                    options=numeric_cols + categorical_cols if viz_type in ["bar", "pie"] else numeric_cols,
                    key="new_viz_x"
                )

            with viz_col3:
                if viz_type not in ["histogram", "pie", "heatmap"]:
                    y_col = st.selectbox(
                        "Y-Axis",
                        options=numeric_cols,
                        key="new_viz_y"
                    )
                else:
                    y_col = None

            with viz_col4:
                if viz_type in ["scatter", "line", "bar"]:
                    color_col = st.selectbox(
                        "Color By",
                        options=["None"] + categorical_cols,
                        key="new_viz_color"
                    )
                else:
                    color_col = None

            if st.button("➕ Add Visualization", type="primary"):
                viz_config = {
                    'type': viz_type,
                    'x': x_col,
                    'y': y_col,
                    'color': color_col if color_col != "None" else None,
                    'title': f"{viz_type.title()}: {x_col}" + (f" vs {y_col}" if y_col else "")
                }
                st.session_state.custom_visualizations.append(viz_config)
                st.success(f"✓ Added {viz_type} visualization")
                st.rerun()

            # Display and manage custom visualizations
            if st.session_state.custom_visualizations:
                st.markdown("---")
                st.markdown("### 📊 Custom Visualizations")

                for idx, viz in enumerate(st.session_state.custom_visualizations):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{idx + 1}.** {viz['title']}")
                    with col2:
                        if st.button(f"🗑️ Remove", key=f"remove_viz_{idx}"):
                            st.session_state.custom_visualizations.pop(idx)
                            st.rerun()

        st.markdown("---")

    # === CUSTOM VISUALIZATIONS SECTION (if any) ===
    if st.session_state.custom_visualizations:
        st.markdown("### 🎨 Custom Visualizations")

        from ui.utils import create_custom_visualization

        # Display custom visualizations in grid
        viz_cols = st.columns(2)

        for idx, viz_config in enumerate(st.session_state.custom_visualizations):
            with viz_cols[idx % 2]:
                try:
                    fig = create_custom_visualization(
                        df,
                        viz_config['type'],
                        viz_config['x'],
                        viz_config['y'],
                        viz_config['color']
                    )

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(viz_config['title'])
                    else:
                        st.error(f"Could not create {viz_config['type']} visualization")
                except Exception as e:
                    st.error(f"Error creating visualization: {str(e)}")

        st.markdown("---")

    # === EXECUTIVE SUMMARY SECTION ===
    if st.session_state.show_sections['executive_summary']:
        st.markdown("### 📋 Executive Summary")

        # Generate AI-powered analysis summary
        summary_col1, summary_col2 = st.columns([2, 1])

        with summary_col1:
            with st.container():
                st.markdown("#### 🔍 Key Insights & Analysis")

            # Get numeric and categorical columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            # Generate automated insights about the ACTUAL DATA
            insights = []

            # 1. KEY METRIC ANALYSIS (business-focused)
            if len(numeric_cols) >= 1:
                # Find primary business metric
                key_metric = numeric_cols[0]
                for col in numeric_cols:
                    if any(keyword in col.lower() for keyword in ['price', 'revenue', 'sales', 'amount', 'value', 'cost']):
                        key_metric = col
                        break

                mean_val = df[key_metric].mean()
                median_val = df[key_metric].median()
                std_val = df[key_metric].std()
                min_val = df[key_metric].min()
                max_val = df[key_metric].max()

                insights.append(
                    f"**Primary Metric ({key_metric.replace('_', ' ').title()}):** "
                    f"Average of {mean_val:.2f} with values ranging from {min_val:.2f} to {max_val:.2f}. "
                    f"{'High variability detected' if (std_val/mean_val > 0.5) else 'Relatively consistent values'}."
                )

            # 2. CATEGORICAL DISTRIBUTION INSIGHT
            if len(categorical_cols) >= 1:
                cat_col = categorical_cols[0]
                value_counts = df[cat_col].value_counts()
                top_category = value_counts.index[0]
                top_count = value_counts.iloc[0]
                top_pct = (top_count / len(df)) * 100
                total_unique = len(value_counts)

                if top_pct > 50:
                    insights.append(
                        f"**{cat_col.replace('_', ' ').title()} Distribution:** "
                        f"'{top_category}' dominates with {top_pct:.1f}% of records ({top_count:,} out of {len(df):,}). "
                        f"Total of {total_unique:,} unique categories - ⚠️ significant imbalance detected."
                    )
                else:
                    insights.append(
                        f"**{cat_col.replace('_', ' ').title()} Distribution:** "
                        f"Fairly balanced across {total_unique:,} categories. Top category '{top_category}' represents {top_pct:.1f}% ({top_count:,} records)."
                    )

            # 3. DATA VOLUME AND SCOPE
            total_records = len(df)
            insights.append(
                f"**Dataset Scope:** Contains {total_records:,} records with {len(numeric_cols)} numeric and {len(categorical_cols)} categorical attributes."
            )

            # 4. CORRELATION PATTERNS (business relationships)
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()

                # Find strongest positive correlation
                strong_positive = []
                strong_negative = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if corr_val > 0.7:
                            strong_positive.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
                        elif corr_val < -0.7:
                            strong_negative.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))

                if strong_positive:
                    top_pos = max(strong_positive, key=lambda x: x[2])
                    insights.append(
                        f"**Strong Positive Relationship:** "
                        f"{top_pos[0].replace('_', ' ').title()} and {top_pos[1].replace('_', ' ').title()} "
                        f"show high correlation ({top_pos[2]:.3f}) - they tend to increase together."
                    )

                if strong_negative:
                    top_neg = min(strong_negative, key=lambda x: x[2])
                    insights.append(
                        f"**Inverse Relationship:** "
                        f"{top_neg[0].replace('_', ' ').title()} and {top_neg[1].replace('_', ' ').title()} "
                        f"show negative correlation ({top_neg[2]:.3f}) - one increases as the other decreases."
                    )

                if not strong_positive and not strong_negative:
                    insights.append(
                        f"**Feature Independence:** Numeric features show weak correlations - variables are largely independent."
                    )

            # 5. OUTLIER AND ANOMALY INSIGHT
            if len(numeric_cols) >= 1:
                # Check for outliers in key metric
                q1 = df[key_metric].quantile(0.25)
                q3 = df[key_metric].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = df[(df[key_metric] < lower_bound) | (df[key_metric] > upper_bound)]
                outlier_pct = (len(outliers) / len(df)) * 100

                if outlier_pct > 5:
                    insights.append(
                        f"**Data Quality Alert:** {len(outliers):,} potential outliers detected ({outlier_pct:.1f}%) "
                        f"in {key_metric.replace('_', ' ').title()} - values outside range [{lower_bound:.2f}, {upper_bound:.2f}]."
                    )
                elif outlier_pct > 0:
                    insights.append(
                        f"**Data Quality:** Minimal outliers ({outlier_pct:.1f}%) in {key_metric.replace('_', ' ').title()} - data appears clean."
                    )

            # 6. DIVERSITY AND UNIQUENESS INSIGHT
            if len(categorical_cols) >= 2:
                diversity_scores = []
                for cat in categorical_cols[:3]:
                    unique_count = df[cat].nunique()
                    diversity_pct = (unique_count / len(df)) * 100
                    diversity_scores.append((cat, unique_count, diversity_pct))

                high_diversity = [d for d in diversity_scores if d[2] > 50]
                if high_diversity:
                    insights.append(
                        f"**High Diversity:** "
                        f"{', '.join([d[0].replace('_', ' ').title() for d in high_diversity])} "
                        f"show high uniqueness - valuable for segmentation."
                    )

            # Display insights
            for insight in insights:
                st.markdown(f"- {insight}")

    with summary_col2:
        st.markdown("#### 📊 Quick Stats")
        st.metric("Total Records", f"{len(df):,}", delta=f"{len(df) - result.cleaning_report.original_shape[0]:,} cleaned" if result.cleaning_report else None)
        st.metric("Features", len(df.columns), delta=f"+{len(df.columns) - result.cleaning_report.original_shape[1]}" if result.cleaning_report and len(df.columns) > result.cleaning_report.original_shape[1] else None)

        if result.quality_report:
            quality = result.quality_report.overall_quality.value
            quality_score = {"excellent": 95, "good": 75, "fair": 55, "poor": 30}.get(quality, 50)
            st.metric("Data Quality", f"{quality_score}%", delta=quality.upper())

        st.metric("Processing Time", f"{result.execution_time:.2f}s", delta="Fast" if result.execution_time < 5 else "Normal")

    st.markdown("---")

    # === BUSINESS-FOCUSED VISUALIZATION SUMMARY ===
    st.markdown("### 📊 Business Analytics Overview")

    if df is not None:
        # Get column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # === DATA HEALTH SCORECARD ===
        st.markdown("#### 🎯 Data Health Scorecard")

        health_col1, health_col2, health_col3, health_col4 = st.columns(4)

        # Calculate health metrics
        completeness_score = ((len(df) * len(df.columns) - df.isnull().sum().sum()) / (len(df) * len(df.columns))) * 100

        # Uniqueness score (based on duplicate percentage)
        dup_count = result.quality_report.duplicate_count if result.quality_report else 0
        uniqueness_score = ((len(df) - dup_count) / len(df)) * 100 if len(df) > 0 else 100

        # Consistency score (based on outliers)
        outlier_count = result.quality_report.outlier_count if result.quality_report else 0
        consistency_score = ((len(df) - outlier_count) / len(df)) * 100 if len(df) > 0 else 100

        # Overall data quality
        quality_map = {"excellent": 95, "good": 80, "fair": 60, "poor": 30}
        quality_score = quality_map.get(result.quality_report.overall_quality.value, 50) if result.quality_report else 50

        with health_col1:
            st.metric(
                "Data Completeness",
                f"{completeness_score:.1f}%",
                delta="Complete" if completeness_score > 95 else ("Good" if completeness_score > 80 else "Needs Attention"),
                delta_color="normal" if completeness_score > 80 else "inverse"
            )

        with health_col2:
            st.metric(
                "Data Uniqueness",
                f"{uniqueness_score:.1f}%",
                delta=f"{dup_count:,} duplicates" if dup_count > 0 else "No duplicates",
                delta_color="inverse" if dup_count > 0 else "normal"
            )

        with health_col3:
            st.metric(
                "Data Consistency",
                f"{consistency_score:.1f}%",
                delta=f"{outlier_count:,} outliers" if outlier_count > 0 else "No outliers",
                delta_color="inverse" if outlier_count > 0 else "normal"
            )

        with health_col4:
            quality_label = result.quality_report.overall_quality.value.upper() if result.quality_report else "UNKNOWN"
            st.metric(
                "Overall Quality",
                f"{quality_score}%",
                delta=quality_label,
                delta_color="normal"
            )

        st.markdown("---")

        # === KEY BUSINESS METRICS ===
        st.markdown("#### 📈 Key Business Metrics")

        # Create 2-column layout for key visualizations
        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            # Top-level metric visualization
            if len(numeric_cols) >= 1:
                st.markdown("##### Primary Metric Analysis")

                # Select most important numeric column (usually first or with 'price', 'revenue', 'sales' in name)
                key_metric = numeric_cols[0]
                for col in numeric_cols:
                    if any(keyword in col.lower() for keyword in ['price', 'revenue', 'sales', 'amount', 'value', 'cost']):
                        key_metric = col
                        break

                # Create distribution with statistics overlay
                fig = go.Figure()

                # Histogram
                fig.add_trace(go.Histogram(
                    x=df[key_metric],
                    name='Distribution',
                    marker_color='#667eea',
                    opacity=0.7,
                    nbinsx=30,
                    hovertemplate='Value: %{x}<br>Count: %{y}<extra></extra>'
                ))

                # Add mean and median lines with better positioning
                mean_val = df[key_metric].mean()
                median_val = df[key_metric].median()
                std_val = df[key_metric].std()

                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", line_width=2,
                             annotation_text=f"Mean: {mean_val:.2f}", annotation_position="top right")
                fig.add_vline(x=median_val, line_dash="dot", line_color="green", line_width=2,
                             annotation_text=f"Median: {median_val:.2f}", annotation_position="top left")

                fig.update_layout(
                    title=f"{key_metric.replace('_', ' ').title()} Distribution",
                    xaxis_title=key_metric.replace('_', ' ').title(),
                    yaxis_title="Frequency",
                    template="plotly_white",
                    height=350,
                    showlegend=False,
                    hovermode='closest'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Enhanced summary statistics with interpretation
                min_val = df[key_metric].min()
                max_val = df[key_metric].max()
                q1 = df[key_metric].quantile(0.25)
                q3 = df[key_metric].quantile(0.75)

                st.caption(f"📊 **Range:** {min_val:.2f} - {max_val:.2f} | **Std Dev:** {std_val:.2f} | **IQR:** {q1:.2f} - {q3:.2f}")

                # Add interpretation
                if std_val / mean_val > 0.5:
                    st.caption("⚠️ High variability detected - data shows significant spread")
                else:
                    st.caption("✓ Low variability - data is relatively consistent")

        with viz_col2:
            # Category breakdown
            if len(categorical_cols) >= 1:
                st.markdown("##### Category Performance")

                # Select first meaningful categorical column
                key_category = categorical_cols[0]

                value_counts = df[key_category].value_counts().head(10)

                # Calculate percentages
                percentages = (value_counts / len(df) * 100).round(1)

                fig = go.Figure(data=[
                    go.Bar(
                        x=value_counts.values,
                        y=value_counts.index,
                        orientation='h',
                        marker=dict(
                            color=value_counts.values,
                            colorscale='Viridis',
                            showscale=False
                        ),
                        text=[f"{count:,} ({pct}%)" for count, pct in zip(value_counts.values, percentages)],
                        textposition='auto',
                        hovertemplate='Category: %{y}<br>Count: %{x}<br>Percentage: %{text}<extra></extra>'
                    )
                ])

                fig.update_layout(
                    title=f"Top 10 {key_category.replace('_', ' ').title()}",
                    xaxis_title="Count",
                    yaxis_title=key_category.replace('_', ' ').title(),
                    template="plotly_white",
                    height=350,
                    yaxis={'categoryorder':'total ascending'},
                    hovermode='closest'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Coverage percentage with interpretation
                top_10_pct = (value_counts.sum() / len(df)) * 100
                st.caption(f"📊 **Coverage:** Top 10 categories represent {top_10_pct:.1f}% of all records")

                # Diversity check
                total_categories = df[key_category].nunique()
                if total_categories > 20:
                    st.caption(f"✓ High diversity - {total_categories:,} unique categories found")
                elif total_categories < 5:
                    st.caption(f"⚠️ Low diversity - Only {total_categories} unique categories")

        # === CORRELATION INSIGHTS (if multiple numeric columns) ===
        if len(numeric_cols) >= 2:
            st.markdown("---")
            st.markdown("#### 🔗 Feature Relationships")

            corr_col1, corr_col2 = st.columns([2, 1])

            with corr_col1:
                # Create compact correlation heatmap
                corr_matrix = df[numeric_cols].corr()

                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    zmin=-1,
                    zmax=1,
                    text=corr_matrix.values.round(2),
                    texttemplate='%{text}',
                    textfont={"size": 8},
                    hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
                ))

                fig.update_layout(
                    title="Correlation Matrix - Feature Relationships",
                    template="plotly_white",
                    height=400,
                    xaxis={'tickangle': -45}
                )
                st.plotly_chart(fig, use_container_width=True)

            with corr_col2:
                st.markdown("##### Top Correlations")

                # Find strongest correlations (excluding diagonal)
                corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_pairs.append({
                            'Feature 1': corr_matrix.columns[i],
                            'Feature 2': corr_matrix.columns[j],
                            'Correlation': corr_matrix.iloc[i, j]
                        })

                corr_df = pd.DataFrame(corr_pairs)
                corr_df['Abs_Corr'] = corr_df['Correlation'].abs()
                top_corr = corr_df.nlargest(5, 'Abs_Corr')

                for idx, row in top_corr.iterrows():
                    corr_val = row['Correlation']
                    emoji = "🔴" if corr_val < -0.5 else ("🟢" if corr_val > 0.5 else "🟡")
                    st.write(f"{emoji} **{row['Feature 1'][:15]}** ↔ **{row['Feature 2'][:15]}**")
                    st.write(f"   Correlation: {corr_val:.3f}")
                    st.markdown("---")

    st.markdown("---")

    # === DATA OVERVIEW & STATISTICS ===
    st.markdown("### 📈 Data Overview & Statistical Summary")

    if df is not None:
        # Get numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        tab1, tab2, tab3 = st.tabs(["📊 Statistical Summary", "🔢 Numeric Analysis", "📋 Categorical Analysis"])

        with tab1:
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("#### Dataset Characteristics")
                st.write(f"**Shape:** {len(df):,} rows × {len(df.columns)} columns")
                st.write(f"**Numeric Columns:** {len(numeric_cols)}")
                st.write(f"**Categorical Columns:** {len(categorical_cols)}")
                st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

                # Missing values summary
                missing_total = df.isnull().sum().sum()
                missing_pct = (missing_total / (len(df) * len(df.columns))) * 100
                st.write(f"**Missing Values:** {missing_total:,} ({missing_pct:.2f}%)")

            with col2:
                st.markdown("#### Data Quality Metrics")
                if result.quality_report:
                    qr = result.quality_report
                    st.write(f"**Duplicates:** {qr.duplicate_count:,}")
                    st.write(f"**Outliers:** {qr.outlier_count:,}")
                    st.write(f"**Overall Quality:** {qr.overall_quality.value.upper()}")

                if result.cleaning_report:
                    cr = result.cleaning_report
                    st.write(f"**Actions Taken:** {len(cr.actions_taken)}")
                    dropped_count = len(cr.columns_dropped) if isinstance(cr.columns_dropped, list) else cr.columns_dropped
                    st.write(f"**Columns Dropped:** {dropped_count}")

            # Statistical summary table
            st.markdown("#### Descriptive Statistics")
            if numeric_cols:
                st.dataframe(df[numeric_cols].describe().T, use_container_width=True)
            else:
                st.info("No numeric columns to display statistics")

        with tab2:
            st.markdown("#### Numeric Column Distributions")

            if len(numeric_cols) > 0:
                # Create distribution plots for numeric columns
                num_cols_to_show = min(len(numeric_cols), 6)
                cols_per_row = 3

                for i in range(0, num_cols_to_show, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col_idx in enumerate(range(i, min(i + cols_per_row, num_cols_to_show))):
                        if col_idx < len(numeric_cols):
                            col_name = numeric_cols[col_idx]
                            with cols[j]:
                                fig = px.histogram(
                                    df,
                                    x=col_name,
                                    title=f"{col_name}",
                                    template="plotly_white",
                                    nbins=30
                                )
                                fig.update_layout(
                                    height=250,
                                    margin=dict(l=20, r=20, t=40, b=20),
                                    showlegend=False
                                )
                                st.plotly_chart(fig, use_container_width=True)

                # Correlation heatmap
                if len(numeric_cols) >= 2:
                    st.markdown("#### Correlation Matrix")
                    corr_matrix = df[numeric_cols].corr()
                    fig = px.imshow(
                        corr_matrix,
                        text_auto='.2f',
                        aspect='auto',
                        title="Feature Correlations",
                        template="plotly_white",
                        color_continuous_scale='RdBu_r',
                        zmin=-1,
                        zmax=1
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns available for analysis")

        with tab3:
            st.markdown("#### Categorical Column Analysis")

            if len(categorical_cols) > 0:
                # Show top categories for each categorical column
                for cat_col in categorical_cols[:4]:  # Limit to first 4 categorical columns
                    st.markdown(f"##### {cat_col}")

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Value counts table
                        value_counts = df[cat_col].value_counts().head(10)
                        st.dataframe(
                            pd.DataFrame({
                                'Category': value_counts.index,
                                'Count': value_counts.values,
                                'Percentage': (value_counts.values / len(df) * 100).round(2)
                            }),
                            use_container_width=True,
                            height=300
                        )

                    with col2:
                        # Bar chart
                        fig = px.bar(
                            x=value_counts.index[:10],
                            y=value_counts.values[:10],
                            title=f"Top 10 {cat_col}",
                            labels={'x': cat_col, 'y': 'Count'},
                            template="plotly_white"
                        )
                        fig.update_layout(
                            height=300,
                            xaxis_tickangle=-45,
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categorical columns available for analysis")

    st.markdown("---")

    # === INTERACTIVE VISUALIZATIONS ===
    st.markdown("### 📊 Interactive Data Explorer")

    if df is not None and len(numeric_cols) >= 2:
        col1, col2, col3 = st.columns(3)

        with col1:
            x_axis = st.selectbox("X-Axis", options=numeric_cols, key="explorer_x")

        with col2:
            y_axis = st.selectbox("Y-Axis", options=numeric_cols, index=min(1, len(numeric_cols)-1), key="explorer_y")

        with col3:
            color_by = st.selectbox(
                "Color By",
                options=["None"] + categorical_cols,
                key="explorer_color"
            )

        # Create interactive scatter plot
        fig = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            color=None if color_by == "None" else color_by,
            title=f"{x_axis} vs {y_axis}",
            template="plotly_white",
            opacity=0.7,
            hover_data=df.columns[:5].tolist()  # Show first 5 columns on hover
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # === PIPELINE GENERATED VISUALIZATIONS ===
    st.markdown("### 🎨 Pipeline-Generated Insights")

    if result.insight_report and result.insight_report.plots_generated:
        viz_cols = st.columns(2)

        for idx, plot_path in enumerate(result.insight_report.plots_generated):
            if os.path.exists(plot_path):
                with viz_cols[idx % 2]:
                    st.image(plot_path, use_container_width=True, caption=os.path.basename(plot_path))
    else:
        st.info("No pipeline-generated visualizations available")

    st.markdown("---")

    # === DOWNLOAD SECTION ===
    st.markdown("### 💾 Export & Download")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if result.output_file and os.path.exists(result.output_file):
            with open(result.output_file, 'rb') as f:
                st.download_button(
                    label="📥 Cleaned Data (CSV)",
                    data=f,
                    file_name=os.path.basename(result.output_file),
                    mime="text/csv",
                    use_container_width=True
                )

    with col2:
        # Find latest report
        artifacts_dir = Path("data/artifacts")
        reports = list(artifacts_dir.glob("pipeline_report_*.html"))
        if reports:
            latest_report = max(reports, key=os.path.getctime)
            with open(latest_report, 'rb') as f:
                st.download_button(
                    label="📄 HTML Report",
                    data=f,
                    file_name=os.path.basename(latest_report),
                    mime="text/html",
                    use_container_width=True
                )

    with col3:
        # Export summary as JSON
        summary_data = {
            "records": len(df),
            "features": len(df.columns),
            "quality_score": result.quality_report.overall_quality.value if result.quality_report else "N/A",
            "execution_time": result.execution_time,
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols)
        }
        st.download_button(
            label="📊 Summary (JSON)",
            data=json.dumps(summary_data, indent=2),
            file_name="pipeline_summary.json",
            mime="application/json",
            use_container_width=True
        )

    with col4:
        # Generate and download executive analysis summary
        exec_summary = generate_executive_summary(df, result)
        st.download_button(
            label="📋 Analysis Report (TXT)",
            data=exec_summary,
            file_name="executive_analysis_summary.txt",
            mime="text/plain",
            use_container_width=True
        )


def display_chatbot_interface():
    """Display AI-powered visualization chatbot"""

    st.markdown("## 💬 AI Visualization Chatbot")

    # Show AI status badge
    if st.session_state.get('use_ai_chatbot', False):
        st.markdown("🤖 **Powered by Google Gemini 2.5 Pro** | Advanced AI with superior reasoning & generation")
    else:
        st.markdown("🔧 **Pattern-based mode** | Using keyword matching")

    st.markdown("Ask me to create custom visualizations from your processed data!")

    if st.session_state.processed_data is None:
        st.info("👆 Process a file first to enable the chatbot")
        return

    # Initialize chatbot if not already done
    if st.session_state.chatbot is None:
        try:
            if 'gemini' in st.secrets and st.secrets['gemini']['api_key']:
                st.session_state.chatbot = AIVisualizationChatbot(
                    st.session_state.processed_data,
                    st.secrets['gemini']['api_key']
                )
                st.session_state.use_ai_chatbot = True
            else:
                st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)
                st.session_state.use_ai_chatbot = False
        except:
            st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)
            st.session_state.use_ai_chatbot = False

    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(
                f'<div class="chat-message user-message">👤 <strong>You:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-message bot-message">🤖 <strong>Assistant:</strong> {message["content"]}</div>',
                unsafe_allow_html=True
            )

            # Display visualization if present
            if 'visualization' in message and message['visualization'] is not None:
                try:
                    st.plotly_chart(message['visualization'], use_container_width=True)
                except Exception as e:
                    st.error(f"Could not display visualization: {str(e)}")

    # Chat input
    st.markdown("---")

    # Example queries and AI suggestions
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("💡 Example Queries"):
            st.markdown("""
            - "Create a scatter plot of price vs discount"
            - "Show me a bar chart of the top 10 categories"
            - "Create a histogram of prices"
            - "Show correlation heatmap"
            - "Create a box plot for numeric columns"
            - "Show distribution of selling_proposition"
            """)

    with col2:
        if st.session_state.get('use_ai_chatbot', False):
            with st.expander("✨ AI Smart Suggestions"):
                try:
                    if hasattr(st.session_state.chatbot, 'get_smart_suggestions'):
                        suggestions = st.session_state.chatbot.get_smart_suggestions()
                        for suggestion in suggestions:
                            st.markdown(f"- {suggestion}")
                    else:
                        st.info("Smart suggestions available with AI chatbot")
                except:
                    st.info("Loading smart suggestions...")

    # User input
    user_query = st.chat_input("Ask for a visualization...")

    if user_query:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })

        # Get chatbot response
        with st.spinner("🤖 Creating visualization..."):
            response = st.session_state.chatbot.process_query(user_query)

            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response['message'],
                'visualization': response.get('figure')
            })

        st.rerun()


def display_custom_analytics():
    """Display custom analytics interface"""

    st.markdown("## 📈 Custom Analytics")

    if st.session_state.processed_data is None:
        st.info("👆 Process a file first to enable custom analytics")
        return

    df = st.session_state.processed_data

    # Data overview
    st.markdown("### 📊 Data Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    # Column selector
    st.markdown("### 🔧 Custom Visualization Builder")

    col1, col2 = st.columns(2)

    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Box Plot", "Violin Plot"]
        )

    with col2:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

    # Chart-specific options
    if chart_type == "Scatter Plot":
        col1, col2, col3 = st.columns(3)
        with col1:
            x_col = st.selectbox("X-axis", numeric_cols)
        with col2:
            y_col = st.selectbox("Y-axis", numeric_cols)
        with col3:
            color_col = st.selectbox("Color by (optional)", ["None"] + all_cols)

        if st.button("Generate Chart"):
            fig = px.scatter(
                df, x=x_col, y=y_col,
                color=None if color_col == "None" else color_col,
                title=f"{x_col} vs {y_col}"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Histogram":
        col1, col2 = st.columns(2)
        with col1:
            hist_col = st.selectbox("Column", numeric_cols)
        with col2:
            bins = st.slider("Number of Bins", 10, 100, 30)

        if st.button("Generate Chart"):
            fig = px.histogram(df, x=hist_col, nbins=bins, title=f"Distribution of {hist_col}")
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box Plot":
        box_col = st.selectbox("Column", numeric_cols)

        if st.button("Generate Chart"):
            fig = px.box(df, y=box_col, title=f"Box Plot of {box_col}")
            st.plotly_chart(fig, use_container_width=True)

    # Data table
    st.markdown("---")
    st.markdown("### 📋 Data Table")

    show_all = st.checkbox("Show all rows (may be slow for large datasets)")

    if show_all:
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.dataframe(df.head(100), use_container_width=True, height=400)
        st.info(f"Showing first 100 of {len(df):,} rows")


if __name__ == "__main__":
    main()

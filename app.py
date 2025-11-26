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
                st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)

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


def display_results_dashboard():
    """Display pipeline results dashboard"""

    st.markdown("## 📊 Pipeline Results Dashboard")

    if st.session_state.pipeline_result is None:
        st.info("👆 Upload and process a file first to see results here")
        return

    result = st.session_state.pipeline_result

    # Executive Summary
    st.markdown("### 📋 Executive Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### ⏱️ Execution Time")
        st.markdown(f"<h2>{result.execution_time:.2f}s</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if result.quality_report:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("#### 🎯 Data Quality")
            quality = result.quality_report.overall_quality.value
            color = {"excellent": "green", "good": "blue", "fair": "orange", "poor": "red"}.get(quality, "gray")
            st.markdown(f"<h2 style='color: {color}'>{quality.upper()}</h2>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        if result.cleaning_report:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Data Shape")
            st.markdown(
                f"<h3>{result.cleaning_report.original_shape[0]:,} × {result.cleaning_report.original_shape[1]}</h3>"
                f"<p>→ {result.cleaning_report.cleaned_shape[0]:,} × {result.cleaning_report.cleaned_shape[1]}</p>",
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Detailed Results
    col1, col2 = st.columns(2)

    with col1:
        # Data Quality Details
        if result.quality_report:
            st.markdown("### 🔍 Quality Assessment")

            qr = result.quality_report

            st.metric("Missing Values", f"{sum(qr.missing_values.values()):.0f}")
            st.metric("Duplicate Rows", qr.duplicate_count)
            st.metric("Outliers Detected", qr.outlier_count)

            if qr.missing_values:
                with st.expander("View Missing Values by Column"):
                    missing_df = pd.DataFrame([
                        {"Column": k, "Missing": v}
                        for k, v in qr.missing_values.items() if v > 0
                    ])
                    if not missing_df.empty:
                        st.dataframe(missing_df, use_container_width=True)

    with col2:
        # Cleaning Actions
        if result.cleaning_report:
            st.markdown("### 🧹 Cleaning Actions")

            cr = result.cleaning_report

            st.metric("Total Actions", len(cr.actions_taken))
            st.metric("Columns Dropped", cr.columns_dropped)
            st.metric("Rows Removed", cr.rows_removed)

            if cr.actions_taken:
                with st.expander("View All Actions"):
                    for action in cr.actions_taken:
                        st.text(f"• {action}")

    # Visualizations
    st.markdown("---")
    st.markdown("### 📈 Generated Visualizations")

    if result.insight_report and result.insight_report.plots_generated:
        viz_cols = st.columns(2)

        for idx, plot_path in enumerate(result.insight_report.plots_generated):
            if os.path.exists(plot_path):
                with viz_cols[idx % 2]:
                    st.image(plot_path, use_container_width=True, caption=os.path.basename(plot_path))
    else:
        st.info("No visualizations generated")

    # Download processed data
    st.markdown("---")
    st.markdown("### 💾 Download Results")

    col1, col2 = st.columns(2)

    with col1:
        if result.output_file and os.path.exists(result.output_file):
            with open(result.output_file, 'rb') as f:
                st.download_button(
                    label="📥 Download Cleaned Data (CSV)",
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
                    label="📄 Download HTML Report",
                    data=f,
                    file_name=os.path.basename(latest_report),
                    mime="text/html",
                    use_container_width=True
                )


def display_chatbot_interface():
    """Display RAG-based visualization chatbot"""

    st.markdown("## 💬 Visualization Chatbot")
    st.markdown("Ask me to create custom visualizations from your processed data!")

    if st.session_state.processed_data is None:
        st.info("👆 Process a file first to enable the chatbot")
        return

    # Initialize chatbot if not already done
    if st.session_state.chatbot is None:
        st.session_state.chatbot = VisualizationChatbot(st.session_state.processed_data)

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
            if 'visualization' in message:
                st.plotly_chart(message['visualization'], use_container_width=True)

    # Chat input
    st.markdown("---")

    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - "Create a scatter plot of price vs discount"
        - "Show me a bar chart of the top 10 categories"
        - "Create a histogram of prices"
        - "Show correlation heatmap"
        - "Create a box plot for numeric columns"
        - "Show distribution of selling_proposition"
        """)

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

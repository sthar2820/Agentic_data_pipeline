# 🚀 Streamlit Dashboard Guide

## Overview

The Agentic Data Pipeline now includes a beautiful, interactive Streamlit dashboard that provides:

- 📤 **File Upload Interface** - Drag & drop CSV files
- 🤖 **AI Pipeline Execution** - Real-time processing with all 6 agents
- 💬 **RAG-based Chatbot** - Natural language visualization requests
- 📊 **Interactive Dashboards** - Results visualization and analytics
- 📥 **Export Capabilities** - Download cleaned data and reports

---

## 🎯 Features

### 1. Upload & Process Tab

**What it does:**
- Upload CSV files via drag-and-drop or file browser
- Preview data before processing
- Configure which agents to enable/disable
- Real-time progress tracking during pipeline execution
- Instant success feedback with key metrics

**Agent Controls:**
- ✅ Inspector (always enabled)
- 🔍 Anomaly Detection (toggle on/off)
- ⚙️ Feature Engineering (toggle on/off)
- 📊 Report Generation (toggle on/off)

### 2. Results Dashboard Tab

**What it shows:**
- **Executive Summary** - Quality score, execution time, data shape
- **Quality Assessment** - Missing values, duplicates, outliers
- **Cleaning Actions** - All actions taken by Refiner agent
- **Visualizations** - All generated plots and charts
- **Download Options** - Cleaned CSV and HTML reports

### 3. Visualization Chatbot Tab

**AI-Powered Visualization Creation:**

The chatbot uses RAG (Retrieval-Augmented Generation) patterns to understand your requests and create appropriate visualizations.

**Supported Visualizations:**
- **Scatter Plots** - "Create a scatter plot of price vs discount"
- **Bar Charts** - "Show me a bar chart of top 10 categories"
- **Histograms** - "Create histogram of prices"
- **Box Plots** - "Show box plot of discount"
- **Heatmaps** - "Show correlation heatmap"
- **Pie Charts** - "Create pie chart of categories"
- **Violin Plots** - "Show violin plot of prices"
- **Line Charts** - "Create line chart showing trends"

**Example Queries:**
```
"Create a scatter plot of price vs discount"
"Show me the top 10 products by price"
"What's the distribution of selling_proposition?"
"Show correlation between all numeric columns"
"Create a box plot for price grouped by category"
```

**How it works:**
1. Type your request in natural language
2. The chatbot detects visualization type from keywords
3. Extracts mentioned column names from your query
4. Generates appropriate Plotly visualization
5. Displays interactive chart you can zoom, pan, and explore

### 4. Custom Analytics Tab

**Manual Visualization Builder:**
- Select chart type from dropdown
- Choose columns for X and Y axes
- Configure color grouping
- Adjust bins for histograms
- Generate custom visualizations on demand

**Data Table:**
- View processed data in interactive table
- Toggle between first 100 rows or full dataset
- Sortable columns
- Searchable content

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Install all required packages including Streamlit
pip install -r requirements.txt
```

### Step 2: Launch Dashboard

```bash
# Start the Streamlit app
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

### Step 3: Upload Data

1. Click "Browse files" or drag & drop a CSV file
2. Preview your data
3. Configure agents (enable/disable as needed)
4. Click "🚀 Run Pipeline"

### Step 4: Explore Results

- View quality metrics in Results Dashboard
- Ask the chatbot for custom visualizations
- Build your own charts in Custom Analytics
- Download cleaned data and reports

---

## 💬 Using the Visualization Chatbot

### Pattern Recognition

The chatbot recognizes these patterns in your queries:

**Scatter Plot Keywords:**
- scatter, scatter plot, relationship, correlation, vs

**Bar Chart Keywords:**
- bar, bar chart, compare, comparison, top

**Histogram Keywords:**
- histogram, distribution, frequency

**Box Plot Keywords:**
- box plot, box, outliers, quartile

**Heatmap Keywords:**
- heatmap, correlation, heat map

**And more...**

### Tips for Best Results

1. **Be specific about columns:**
   - Good: "scatter plot of price vs discount"
   - Better: "create scatter plot with price on x-axis and discount on y-axis"

2. **Use "top N" for rankings:**
   - "Show top 5 products"
   - "Top 10 categories by frequency"

3. **Mention column names exactly:**
   - If your column is "selling_proposition", say "selling_proposition"
   - Underscores and hyphens matter!

4. **Request grouping/coloring:**
   - "Box plot of price grouped by category"
   - "Scatter plot colored by category"

### Example Conversation

```
You: "Create a scatter plot of price vs discount"
Bot: "Here's your scatter chart!"
[Interactive scatter plot appears]

You: "Now show me a histogram of price"
Bot: "Here's your histogram chart!"
[Interactive histogram appears]

You: "What about the top 10 products?"
Bot: "Here's your bar chart!"
[Bar chart of top 10 appears]
```

---

## 📊 Dashboard Components

### Sidebar

**Pipeline Controls:**
- Agent enable/disable toggles
- Real-time pipeline status
- Quality metrics display
- Quick links to documentation

**Pipeline Status:**
- ✅ Status indicator (COMPLETED/FAILED)
- ⏱️ Execution time
- 📈 Data quality score

### Main Tabs

**1. Upload & Process**
- File uploader with preview
- Agent configuration
- Pipeline execution button
- Progress tracking
- Quick metrics on completion

**2. Results Dashboard**
- Executive summary cards
- Detailed quality metrics
- Cleaning action log
- Visualization gallery
- Download buttons

**3. Visualization Chatbot**
- Chat interface
- Message history
- Interactive Plotly charts
- Example queries
- Suggestion system

**4. Custom Analytics**
- Data overview metrics
- Chart type selector
- Column selectors
- Interactive chart builder
- Full data table viewer

---

## 🎨 Customization

### Modify Color Scheme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"          # Purple gradient
backgroundColor = "#ffffff"        # White background
secondaryBackgroundColor = "#f5f7fa"  # Light gray cards
textColor = "#262730"             # Dark text
```

### Add Custom Visualizations

Edit `ui/chatbot.py` to add new chart types:

```python
self.visualization_patterns['your_chart'] = {
    'keywords': ['keyword1', 'keyword2'],
    'requires': ['x', 'y'],
    'function': self.create_your_chart
}
```

### Modify Agent Defaults

Edit `configs/pipeline.yaml` to change default agent settings.

---

## 🔧 Troubleshooting

### Issue: Dashboard won't start

**Solution:**
```bash
# Check if port 8501 is available
lsof -i :8501

# Use a different port
streamlit run app.py --server.port 8502
```

### Issue: File upload fails

**Solution:**
- Check file size < 200MB (configurable in `.streamlit/config.toml`)
- Ensure file is valid CSV format
- Check file permissions

### Issue: Chatbot doesn't understand query

**Solution:**
- Use exact column names from your data
- Include visualization type keyword (scatter, bar, histogram, etc.)
- Be more specific: "scatter plot of X vs Y"

### Issue: Visualizations not appearing

**Solution:**
- Ensure you've processed a file first
- Check that processed data has numeric columns for numeric charts
- Look for error messages in chat responses

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or install Streamlit specifically
pip install streamlit>=1.28.0
```

---

## 📱 Mobile Support

The dashboard is responsive and works on tablets, but for best experience use:
- Desktop: Full feature set
- Tablet: Most features work well
- Mobile: Limited (file upload works, but charts may be small)

---

## 🚀 Advanced Usage

### Running in Production

```bash
# Run with specific host and port
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Run in headless mode (no browser auto-open)
streamlit run app.py --server.headless true
```

### Custom Configuration

Create `.streamlit/secrets.toml` for API keys or sensitive config:

```toml
[general]
api_key = "your-api-key"
```

### Performance Optimization

For large datasets:
1. Disable Feature Engineering if not needed
2. Use "Show first 100 rows" in data table
3. Limit visualization complexity
4. Enable caching in Streamlit

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Plotly Docs:** https://plotly.com/python/
- **Pipeline Guide:** [QUICK_START.md](QUICK_START.md)
- **Technical Details:** [IMPROVEMENTS.md](IMPROVEMENTS.md)

---

## 🎉 Tips for Best Experience

1. **Start Small** - Test with a small dataset first
2. **Use Example Queries** - Click the example queries in chatbot
3. **Explore Results** - Check all tabs after processing
4. **Download Reports** - Save HTML reports for sharing
5. **Experiment** - Try different visualizations and configurations

---

## 🐛 Known Limitations

1. **File Size** - Max 200MB upload (configurable)
2. **Chart Types** - Limited to predefined types (extensible)
3. **Chatbot** - Pattern-based, not true NLP (works well for common queries)
4. **Real-time** - Pipeline runs synchronously (no background jobs yet)

---

## 🔜 Future Enhancements

Potential additions:
- Real-time streaming data support
- Advanced NLP for chatbot (LLM integration)
- Multiple file comparison
- Scheduled pipeline runs
- User authentication
- Collaboration features

---

**Happy Data Exploring! 🎉**

For questions or issues, check the main documentation or create an issue on GitHub.

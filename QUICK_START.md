# 🚀 Quick Start Guide - Enhanced Agentic Data Pipeline

## Installation

```bash
# Clone the repository (if not already done)
cd Agentic_data_pipeline-main

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Process a Single File
```bash
python main.py --file data/raw/your_data.csv
```

**What happens:**
1. 🔍 Inspector analyzes data quality
2. 🚨 Anomaly Detector finds unusual patterns (ML-based)
3. 🧹 Refiner cleans data using Inspector's recommendations
4. 💡 Insight Agent generates visualizations
5. 📊 Report Generator creates comprehensive HTML report

**Output:**
- Cleaned data: `data/cleaned/your_data_cleaned_*.csv`
- Comprehensive report: `data/artifacts/pipeline_report_*.html`
- Visualizations: `data/artifacts/*.png`

### 2. Process Entire Directory
```bash
python main.py --directory data/raw/
```

### 3. Check Pipeline Status
```bash
python main.py --status
```

---

## Configuration Quick Reference

Edit `configs/pipeline.yaml` to customize:

### Standard Configuration (Recommended)
```yaml
agents:
  inspector:
    enabled: true      # ✅ Always enable

  refiner:
    enabled: true      # ✅ Always enable

  anomaly_detector:
    enabled: true      # ✅ Recommended - ML anomaly detection

  feature_engineer:
    enabled: false     # ⚙️ Optional - Enable for ML projects

  insight:
    enabled: true      # ✅ Visualizations

  reporter:
    enabled: true      # ✅ Professional reports
```

### For Machine Learning Workflows
```yaml
  feature_engineer:
    enabled: true      # ✨ Enable feature engineering
    config:
      datetime_features: true
      numeric_features: true
      categorical_features: true
      interaction_features: true    # Advanced
      polynomial_features: false
```

### For Strict Data Quality
```yaml
  anomaly_detector:
    config:
      contamination: 0.05           # Expect 5% anomalies
      ensemble_voting: "unanimous"   # Stricter detection
```

---

## Understanding the Output

### 1. Console Output
```
Starting pipeline execution for file: data.csv
Loaded data with shape: (1000, 15)

Running Inspector Agent...
Data quality assessment: good

Running Anomaly Detection Agent...
🔍 Detected 32 anomalies (3.2%)

Running Refiner Agent...
🤖 Using 12 proposed actions from Inspector
Data cleaned: (1000, 15) -> (968, 14)

Running Insight Agent...
Generated 5 visualizations

Generating Comprehensive Report...
Report saved: data/artifacts/pipeline_report_20251125_173045.html

Pipeline completed successfully in 8.45 seconds
```

### 2. Generated Files

**Cleaned Data:**
```
data/cleaned/
└── your_data_cleaned_20251125_173045.csv
```

**Artifacts:**
```
data/artifacts/
├── your_data_dq_report.json          # Quality metrics
├── your_data_clean_plan.json         # Cleaning actions taken
├── data_overview.png                 # Overview visualizations
├── correlation_heatmap.png           # Correlations
├── distributions.png                 # Distributions
├── categorical_analysis.png          # Categorical plots
├── interactive_plot.html             # Interactive Plotly viz
└── pipeline_report_20251125.html     # 📊 MAIN REPORT
```

### 3. Main Report Contents

Open `pipeline_report_*.html` in your browser to see:

- **Executive Summary** - Key metrics at a glance
- **Data Quality** - Issues found and severity
- **Cleaning Results** - What was changed
- **Anomalies** - Unusual patterns detected
- **Features** - New features created (if enabled)
- **Insights** - Statistical findings
- **Recommendations** - Action items

---

## Example Workflow

### Scenario: You receive a new dataset

**Step 1: Initial Analysis**
```bash
python main.py --file new_dataset.csv
```

**Step 2: Review Report**
```bash
open data/artifacts/pipeline_report_*.html
```

**Step 3: Check Data Quality**
Look for:
- Overall quality rating (EXCELLENT, GOOD, FAIR, POOR)
- Number of anomalies detected
- Cleaning actions taken
- Recommendations

**Step 4: Use Cleaned Data**
```python
import pandas as pd

# Load cleaned data
df = pd.read_csv('data/cleaned/new_dataset_cleaned_*.csv')

# Ready for analysis or ML!
```

---

## Agent Capabilities at a Glance

| Agent | Purpose | Key Features |
|-------|---------|--------------|
| **Inspector** | Quality analysis | Missing values, duplicates, outliers, type detection |
| **Anomaly Detector** | ML-based outlier detection | Isolation Forest, LOF, ensemble voting |
| **Refiner** | Intelligent cleaning | Executes Inspector's actions, adaptive strategies |
| **Feature Engineer** | ML feature creation | Datetime, transformations, encoding, interactions |
| **Insight** | Visualizations | Plots, correlations, statistics |
| **Reporter** | Executive reports | HTML reports, recommendations, metrics |

---

## Common Use Cases

### 1. Data Quality Check
**Goal:** Assess data quality before analysis
```yaml
# Enable: Inspector, Anomaly Detector, Reporter
# Disable: Feature Engineer
```

### 2. ML Data Preparation
**Goal:** Prepare data for machine learning
```yaml
# Enable: All agents
# Feature Engineer config:
#   - interaction_features: true
#   - polynomial_features: true
```

### 3. Quick Cleaning
**Goal:** Fast data cleaning
```yaml
# Enable: Inspector, Refiner
# Disable: Anomaly Detector, Feature Engineer, Reporter
```

### 4. Stakeholder Report
**Goal:** Professional report for non-technical audience
```yaml
# Enable: All agents with Reporter
# Focus on comprehensive reporting
```

---

## Troubleshooting

### Issue: "No module named 'sklearn'"
**Solution:**
```bash
pip install scikit-learn>=1.3.0
```

### Issue: "File not found"
**Solution:** Ensure file path is correct
```bash
# Use absolute path or correct relative path
python main.py --file /full/path/to/data.csv
```

### Issue: Too many features created
**Solution:** Disable advanced feature engineering
```yaml
feature_engineer:
  config:
    interaction_features: false
    polynomial_features: false
```

### Issue: Anomaly detection too strict/lenient
**Solution:** Adjust contamination parameter
```yaml
anomaly_detector:
  config:
    contamination: 0.1  # Increase for more lenient (expect 10% anomalies)
```

---

## Performance Tips

1. **Large datasets (>1M rows):**
   - Disable feature engineering or limit to essential features
   - Use `interaction_features: false`

2. **Many columns (>100):**
   - Anomaly detector will focus on numeric columns only
   - Feature engineer limits to top variable columns

3. **Faster processing:**
   - Disable reporter if you don't need HTML reports
   - Disable insight agent if you don't need visualizations

4. **Memory optimization:**
   - Process in batches using `--directory` with smaller files
   - Clean data incrementally

---

## Next Steps

1. ✅ Run pipeline on your data
2. ✅ Review comprehensive report
3. ✅ Adjust configuration based on needs
4. ✅ Use cleaned data for analysis/ML

For detailed information, see [IMPROVEMENTS.md](IMPROVEMENTS.md)

---

**Happy Data Processing! 🎉**

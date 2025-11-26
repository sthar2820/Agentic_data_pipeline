# 🚀 Agentic Data Pipeline - Major Improvements

## Overview
The Agentic Data Pipeline has been significantly enhanced with **advanced autonomous decision-making** and **ML-powered capabilities**. The agents now truly collaborate and make intelligent decisions based on each other's findings.

---

## ✨ What's New

### Phase 1: Enhanced Agent Autonomy

#### 🔗 **Intelligent Agent Communication**
- **Refiner Agent** now uses **Inspector's proposed actions** for autonomous cleaning
- Agents communicate through structured action plans instead of operating independently
- Adaptive cleaning strategies based on data quality assessment

**Before:**
```python
# Old: Refiner ignored Inspector's recommendations
cleaned_data, report = cleaner.clean_data(data)  # Heuristic cleaning only
```

**After:**
```python
# New: Refiner executes Inspector's proposed actions
cleaned_data, report = cleaner.clean_data(data, quality_report)  # Intelligent cleaning
```

#### 🎯 **Autonomous Decision Making**
The Refiner Agent now autonomously:
- Drops columns based on Inspector's analysis (constant, >70% missing)
- Converts data types intelligently (numeric-like strings → numbers)
- Parses datetime columns when detected
- Applies appropriate imputation strategies:
  - **Simple imputation** for 10-30% missing (median/mode)
  - **Advanced imputation** for 30-70% missing (forward/backward fill)
- Standardizes text (whitespace trimming, case normalization)

---

### Phase 2: ML-Powered Capabilities

#### 🚨 **1. Anomaly Detection Agent** (NEW)
**Location:** `agents/anomaly/anomaly_agent.py`

Advanced ML-based anomaly detection using ensemble methods:

**Algorithms:**
- **Isolation Forest** - Effective for high-dimensional data
- **Local Outlier Factor (LOF)** - Detects local density deviations
- **Elliptic Envelope** - Assumes Gaussian distribution

**Features:**
- Ensemble voting (majority, unanimous, or any)
- Feature importance ranking (which columns contribute to anomalies)
- Anomaly scores for each record
- Intelligent recommendations based on anomaly rate

**Usage Example:**
```python
from agents.anomaly.anomaly_agent import AnomalyDetectionAgent

agent = AnomalyDetectionAgent(config)
report = agent.detect_anomalies(data)

print(f"Found {report.anomaly_count} anomalies ({report.anomaly_percentage}%)")
print(f"Top anomaly indicators: {report.feature_importance}")
```

**Output:**
```
🔍 Detected 42 anomalies (3.2%)
Top anomaly indicators: price (0.95), quantity (0.78), discount (0.54)
```

---

#### ⚙️ **2. Feature Engineering Agent** (NEW)
**Location:** `agents/feature_engineer/feature_agent.py`

Automated feature generation for ML-ready datasets:

**Capabilities:**
1. **DateTime Features** - Extracts year, month, day, day of week, quarter, is_weekend
2. **Numeric Transformations** - log, sqrt, binning/discretization
3. **Categorical Encoding**:
   - One-hot encoding for low cardinality (<50 unique)
   - Frequency encoding for high cardinality
4. **Interaction Features** (optional) - Multiplication, division between numeric columns
5. **Polynomial Features** (optional) - Squared, cubed transformations

**Usage Example:**
```python
from agents.feature_engineer.feature_agent import FeatureEngineeringAgent

agent = FeatureEngineeringAgent(config)
engineered_data, report = agent.engineer_features(cleaned_data)

print(f"Features: {report.original_features} → {report.total_features}")
# Output: Features: 12 → 45 (+33 new features)
```

**Smart Decisions:**
- Only encodes features with reasonable cardinality
- Skips log transform on negative values
- Limits interaction features to top 5 most variable columns
- Provides recommendations on feature selection

---

#### 📊 **3. Automated Report Generation Agent** (NEW)
**Location:** `agents/reporter/report_agent.py`

Creates executive-ready, comprehensive HTML reports:

**Report Sections:**
1. **Executive Summary** - Key metrics at a glance
2. **Data Quality Assessment** - Inspector's findings
3. **Data Cleaning Results** - Actions taken by Refiner
4. **Anomaly Detection Results** - ML anomaly analysis
5. **Feature Engineering Results** - New features created
6. **Insights & Visualizations** - Key findings
7. **Final Recommendations** - Consolidated action items

**Features:**
- Beautiful gradient-styled HTML with responsive design
- Quality score visualization with color-coded badges
- Progress bars for quality scores and feature importance
- Mobile-friendly layout
- Professional appearance for stakeholder presentations

**Sample Report:**
```
🤖 Agentic Data Pipeline Report
Generated: 2025-11-25 17:30:45

📈 Executive Summary
├─ Data Quality: GOOD
├─ Original Dataset: 1,250 × 18
├─ Final Dataset: 1,208 × 51
└─ Anomalies Detected: 42 (3.2%)

🔍 Data Quality Assessment
Overall Quality: GOOD
Missing Values: 127 total across 5 columns
...
```

---

## 🔄 Enhanced Pipeline Flow

### Old Pipeline (3 steps):
```
1. Inspector → Analyze quality
2. Refiner → Clean (heuristic)
3. Insight → Visualize
```

### New Pipeline (6 steps):
```
1. Inspector → Analyze quality & propose actions
2. Anomaly Detector → ML-based anomaly detection
3. Refiner → Execute Inspector's proposed actions (intelligent cleaning)
4. Feature Engineer → Create ML-ready features (optional)
5. Insight → Generate visualizations
6. Reporter → Create comprehensive report
```

---

## 📁 New File Structure

```
Agentic_data_pipeline-main/
├── agents/
│   ├── inspector/
│   │   └── inspector_agent.py (enhanced with proposed_actions)
│   ├── refiner/
│   │   └── cleaner_agent.py (✨ ENHANCED - uses Inspector's actions)
│   ├── insight/
│   │   └── insight_agent.py
│   ├── anomaly/              ⭐ NEW
│   │   └── anomaly_agent.py  (ML-based anomaly detection)
│   ├── feature_engineer/     ⭐ NEW
│   │   └── feature_agent.py  (Automated feature engineering)
│   └── reporter/             ⭐ NEW
│       └── report_agent.py   (Comprehensive report generation)
├── orchestrator/
│   └── pipeline.py (✨ ENHANCED - orchestrates all 6 agents)
├── configs/
│   └── pipeline.yaml (✨ UPDATED - new agent configurations)
└── requirements.txt (✨ UPDATED)
```

---

## ⚙️ Configuration

### Enable/Disable Agents

Edit `configs/pipeline.yaml`:

```yaml
agents:
  inspector:
    enabled: true  # Core - Always recommended

  refiner:
    enabled: true  # Core - Always recommended

  anomaly_detector:
    enabled: true  # NEW - ML anomaly detection
    config:
      methods: ["isolation_forest", "lof"]
      contamination: "auto"
      ensemble_voting: "majority"

  feature_engineer:
    enabled: false  # Optional - Enable for ML workflows
    config:
      datetime_features: true
      numeric_features: true
      categorical_features: true
      interaction_features: false  # Advanced
      polynomial_features: false   # Advanced

  insight:
    enabled: true  # Visualizations

  reporter:
    enabled: true  # NEW - Executive reports
```

---

## 🚀 Usage

### Basic Usage (No changes needed!)
```bash
# Process a single file
python main.py --file data/raw/sample.csv

# Process entire directory
python main.py --directory data/raw/

# Check status
python main.py --status
```

### Advanced Configuration

**For ML Workflows (Enable Feature Engineering):**
```yaml
feature_engineer:
  enabled: true
  config:
    interaction_features: true
    polynomial_features: true
```

**For Sensitive Data (Stricter Anomaly Detection):**
```yaml
anomaly_detector:
  config:
    contamination: 0.05  # Expect 5% anomalies
    ensemble_voting: "unanimous"  # Only flag if all methods agree
```

---

## 📊 Output Files

After running the pipeline, you'll find:

```
data/
├── cleaned/
│   └── sample_cleaned_20251125_173045.csv
└── artifacts/
    ├── sample_dq_report.json          (Quality assessment)
    ├── sample_clean_plan.json         (Proposed actions)
    ├── data_overview.png              (Visualizations)
    ├── correlation_heatmap.png
    ├── distributions.png
    ├── interactive_plot.html
    ├── insight_report_20251125.html
    └── pipeline_report_20251125.html  ⭐ NEW (Comprehensive report)
```

---

## 🎯 Key Improvements Summary

### 1. **Truly Agentic Behavior**
- ✅ Agents now communicate and collaborate
- ✅ Refiner executes Inspector's recommendations autonomously
- ✅ Adaptive strategies based on data characteristics

### 2. **ML-Powered Intelligence**
- ✅ Ensemble anomaly detection (3 algorithms)
- ✅ Automated feature engineering
- ✅ Feature importance analysis

### 3. **Better Decision Making**
- ✅ Context-aware cleaning strategies
- ✅ Intelligent imputation (simple vs advanced)
- ✅ Type detection and conversion

### 4. **Professional Reporting**
- ✅ Executive-ready HTML reports
- ✅ Consolidated recommendations
- ✅ Visual quality metrics

### 5. **Flexibility**
- ✅ All new agents are optional
- ✅ Backward compatible
- ✅ Configurable ensemble methods

---

## 🧪 Testing

To test with sample data:

```bash
# Install dependencies
pip install -r requirements.txt

# Run on sample data
python main.py --file data/raw/your_data.csv

# Check the comprehensive report
open data/artifacts/pipeline_report_*.html
```

---

## 🔜 Future Enhancements

Potential additions:
- **Data Drift Detection** - Monitor changes over time
- **AutoML Agent** - Automatic model selection and training
- **Explainability Agent** - SHAP values and feature explanations
- **Optimization Agent** - Memory and performance optimization
- **Validation Agent** - Data schema validation

---

## 📝 Technical Details

### Anomaly Detection Methods

**Isolation Forest:**
- Best for: High-dimensional data
- Works by: Isolating anomalies in random trees
- Pros: Fast, handles high dimensions well
- Cons: Sensitive to feature scaling

**Local Outlier Factor (LOF):**
- Best for: Local density-based anomalies
- Works by: Comparing local density with neighbors
- Pros: Detects local anomalies
- Cons: Computationally expensive for large datasets

**Elliptic Envelope:**
- Best for: Gaussian-distributed data
- Works by: Fits robust covariance estimate
- Pros: Works well on clean, normal distributions
- Cons: Assumes Gaussian distribution

### Feature Engineering Strategies

**Datetime Features:**
- Temporal patterns (hour, day, month, year)
- Cyclical features (day of week, quarter)
- Business logic (is_weekend, is_holiday)

**Numeric Transformations:**
- Log transformation for skewed distributions
- Binning for discretization
- Scaling for model compatibility

**Categorical Encoding:**
- One-hot for low cardinality (<50)
- Frequency encoding for high cardinality
- Preserves information while reducing dimensions

---

## 🎓 Best Practices

1. **Always enable Inspector and Refiner** - Core functionality
2. **Enable Anomaly Detector for data validation** - Catch unusual patterns
3. **Enable Feature Engineer for ML projects** - Prepare data for modeling
4. **Enable Reporter for stakeholder communication** - Professional outputs
5. **Start with default configs** - Tune based on your data characteristics

---

## 📞 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Documentation: See individual agent files for detailed docstrings

---

**Built with ❤️ using AI Agents**

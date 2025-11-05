# Agentic Data Pipeline

A sophisticated, intelligent data processing pipeline powered by three specialized AI agents that automatically analyze, clean, and generate insights from messy datasets.

## 🤖 Meet the Agents

### 1. Inspector Agent 🔍
- **Role**: Data Quality Detective
- **Capabilities**:
  - Analyzes data structure and quality
  - Detects missing values, duplicates, and outliers
  - Assesses overall data health
  - Provides quality recommendations

### 2. Refiner Agent 🧹
- **Role**: Data Cleaning Specialist
- **Capabilities**:
  - Handles missing values intelligently
  - Removes duplicates
  - Manages outliers (clip/remove)
  - Optimizes data types for memory efficiency

### 3. Insight Agent 📊
- **Role**: Data Storyteller
- **Capabilities**:
  - Generates comprehensive visualizations
  - Performs correlation analysis
  - Creates interactive plots
  - Produces detailed HTML reports

## 🏗️ Project Structure

```
agentic-data-pipeline/
├─ data/
│  ├─ raw/                    # Input: messy CSV files
│  ├─ cleaned/                # Output: processed data
│  └─ artifacts/              # Reports, plots, logs
├─ configs/
│  └─ pipeline.yaml           # Configuration settings
├─ agents/
│  ├─ inspector/              # Data quality analysis
│  ├─ refiner/                # Data cleaning
│  └─ insight/                # Visualization & insights
├─ orchestrator/              # Pipeline coordination
├─ tests/                     # Unit tests
├─ requirements.txt           # Dependencies
└─ main.py                    # Main entry point
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentic-data-pipeline

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Process a single file
python main.py --file data/raw/messy_customers.csv

# Process all files in a directory
python main.py --directory data/raw/

# Check pipeline status
python main.py --status
```

### 3. What You Get

After running the pipeline, you'll find:

- **Cleaned Data**: `data/cleaned/filename_cleaned_timestamp.csv`
- **Visualizations**: Various plots in `data/artifacts/`
- **HTML Report**: Comprehensive analysis report
- **Logs**: Detailed execution logs

## 📋 Features

### Data Quality Analysis
- Missing value detection and quantification
- Duplicate identification
- Outlier detection using IQR method
- Data type analysis and optimization suggestions
- Overall quality scoring (Excellent/Good/Fair/Poor)

### Intelligent Data Cleaning
- **Auto Mode**: Smart handling based on data characteristics
- **Missing Values**: Fill with median (numeric) or mode (categorical)
- **Duplicates**: Automatic removal
- **Outliers**: Clipping or removal options
- **Memory Optimization**: Downcast data types when possible

### Rich Visualizations
- Data overview dashboard
- Correlation heatmaps
- Distribution plots
- Categorical analysis
- Interactive Plotly visualizations
- Professional HTML reports

## ⚙️ Configuration

Edit `configs/pipeline.yaml` to customize agent behavior:

```yaml
agents:
  inspector:
    enabled: true
    config:
      max_rows_sample: 1000
      quality_checks: [missing_values, data_types, duplicates, outliers]
  
  refiner:
    enabled: true
    config:
      handle_missing: "auto"  # auto, drop, fill, interpolate
      remove_duplicates: true
      outlier_treatment: "clip"  # clip, remove, ignore
  
  insight:
    enabled: true
    config:
      generate_plots: true
      correlation_analysis: true
      export_format: ["html", "pdf"]
```

## 🧪 Testing

Run the test suite:

```bash
# Run inspector agent tests
python tests/test_inspector.py

# Run all tests (when more are added)
python -m pytest tests/
```

## 📊 Example Output

### Console Output
```
Processing file: data/raw/messy_customers.csv
--------------------------------------------------
Status: ✓ COMPLETED
Execution time: 2.34 seconds
Data quality: good
Data shape: (25, 9) → (24, 9)
Rows removed: 1
Visualizations: 5
Key insights: 4
```

### Generated Files
- `messy_customers_cleaned_20241104_143022.csv`
- `data_overview.png`
- `correlation_heatmap.png`
- `distributions.png`
- `categorical_analysis.png`
- `interactive_plot.html`
- `insight_report_20241104_143022.html`

## 🎯 Use Cases

- **Data Scientists**: Quick EDA and preprocessing
- **Analysts**: Automated data quality assessment
- **Researchers**: Standardized data cleaning workflows
- **Students**: Learning data pipeline concepts
- **Anyone**: Who deals with messy CSV files!

## 🛠️ Supported Formats

- **CSV** (various encodings and separators)
- **Excel** (.xlsx, .xls)
- **JSON**
- **Parquet**

## 🔄 Pipeline Flow

1. **Load Data** → Intelligent format detection
2. **Inspect** → Quality analysis and recommendations
3. **Clean** → Apply cleaning transformations
4. **Analyze** → Generate insights and visualizations
5. **Report** → Comprehensive HTML report
6. **Save** → Cleaned data and artifacts

## 📈 Performance Features

- **Memory Efficient**: Data type optimization
- **Batch Processing**: Handle multiple files
- **Error Handling**: Robust error recovery
- **Logging**: Detailed execution tracking
- **Configurable**: Flexible agent settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Import Errors**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
```

**File Not Found**: Check file paths and permissions

**Memory Issues**: For large files, consider processing in chunks

**Encoding Errors**: The pipeline tries multiple encodings automatically

### Getting Help

- Check the logs in `data/artifacts/pipeline.log`
- Run with `--status` to verify configuration
- Review the HTML reports for detailed insights

---

**Happy Data Processing! 🎉**

# Quick Start: Inspector Agent

## 🚀 One Command to Clean Your Data

```bash
python3 run_agent.py data/raw/your_file.csv
```

That's it! The agent will:
1. ✅ Analyze data quality
2. ✅ Auto-clean the data
3. ✅ Save to `data/cleaned/`
4. ✅ Show before/after comparison

---

## 📂 Output Locations

### Cleaned Data
```
data/cleaned/your_file_cleaned_TIMESTAMP.csv
```

### Quality Reports
```
data/artifacts/your_file_*_dq_report.json
data/artifacts/your_file_*_clean_plan.json
```

---

## 💡 Example

```bash
python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv
```

**Result:**
- Quality: FAIR → EXCELLENT
- Missing: 51.3% → 0%
- Output: `data/cleaned/us-shein-beauty_and_health-4267_cleaned_20251105_103858.csv`

---

## 🎯 What Gets Cleaned

The Inspector Agent automatically:
- ✅ Removes duplicate rows
- ✅ Drops columns with >80% missing data
- ✅ Imputes remaining missing values (median/mode)
- ✅ Handles outliers (clips to IQR bounds)
- ✅ Optimizes data types

---

## 📊 View Results

```bash
# Check cleaned data
python3 -c "import pandas as pd; df=pd.read_csv('data/cleaned/your_file_cleaned_*.csv'); print(df.info()); print(df.head())"

# View quality report
cat data/artifacts/your_file_*_dq_report.json | python3 -m json.tool | less

# List all cleaned files
ls -lh data/cleaned/
```

---

## 🔧 Advanced Options

If you need more control, use the full pipeline:

```bash
# Full pipeline with visualizations
python3 main.py --file data/raw/your_file.csv

# Advanced inspector with options
python3 run_inspector.py --file data/raw/your_file.csv --detailed

# Custom config
python3 run_inspector.py --file data/raw/your_file.csv --config custom.yaml
```

---

## ✅ Success Indicators

After running, you should see:
- ✅ "Quality improved: POOR/FAIR → GOOD/EXCELLENT"
- ✅ Cleaned file in `data/cleaned/`
- ✅ 0% missing values (or very low)
- ✅ High column quality scores (>0.8)

---

**Just run this:**
```bash
python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv
```

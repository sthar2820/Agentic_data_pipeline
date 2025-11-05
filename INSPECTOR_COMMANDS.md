# Quick Inspector Commands

## 🚀 SIMPLEST WAY - Just Run This:

```bash
python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv
```

**That's it!** This will:
- ✅ Analyze data quality
- ✅ Clean the data automatically
- ✅ Save cleaned data to `data/cleaned/`
- ✅ Show before/after quality comparison
- ✅ Save quality reports and cleaning plan

---

## 📋 All Available Commands

### Option 1: Simple Inspector (Recommended)
```bash
python3 run_agent.py <your_file.csv>
```

### Option 2: Advanced Inspector
```bash
# Auto-clean (default)
python3 run_inspector.py --file data/raw/your_file.csv

# Analysis only (no cleaning)
python3 run_inspector.py --file data/raw/your_file.csv --no-clean

# With custom name
python3 run_inspector.py --file data/raw/your_file.csv --name my_dataset

# Detailed report
python3 run_inspector.py --file data/raw/your_file.csv --detailed
```

### Option 3: Full Pipeline (Inspector + Refiner + Insights)
```bash
python3 main.py --file data/raw/your_file.csv
```

---

## 📂 Where Files Are Saved

After running `run_agent.py`, you'll find:

```
data/
├── cleaned/
│   └── your_file_cleaned_20251105_123456.csv  ← Your cleaned data
└── artifacts/
    ├── your_file_*_dq_report.json              ← Quality analysis
    └── your_file_*_clean_plan.json             ← Actions taken
```

---

## 💡 Examples

### Beauty & Health Dataset
```bash
python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv
```

### Any CSV file
```bash
python3 run_agent.py path/to/your/data.csv
```

---

## 🎯 What It Does

1. **Loads your CSV file**
2. **Analyzes quality** (missing values, duplicates, outliers, etc.)
3. **Shows recommendations** (what needs fixing)
4. **Auto-cleans the data**:
   - Removes duplicates
   - Drops columns with >80% missing values
   - Imputes remaining missing values
   - Handles outliers
   - Optimizes data types
5. **Saves cleaned data** to `data/cleaned/`
6. **Re-analyzes cleaned data** to verify improvement
7. **Shows before/after comparison**

---

## ✅ Quick Test

Try it now:
```bash
python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv
```

Expected output:
- Quality: FAIR → EXCELLENT
- Missing: 51.3% → 0%
- Cleaned file saved to `data/cleaned/`

---

## 🆘 Help

```bash
# Show help for simple inspector
python3 run_agent.py

# Show help for advanced inspector
python3 run_inspector.py --help

# Show pipeline status
python3 main.py --status
```

---

**TL;DR: Just run:**
```bash
python3 run_agent.py data/raw/us-shein-beauty_and_health-4267.csv
```

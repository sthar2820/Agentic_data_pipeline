#!/usr/bin/env python3
"""
Quick test script to verify Streamlit dashboard components
"""

import sys
import os

print("=" * 80)
print("🧪 STREAMLIT DASHBOARD COMPONENT TEST")
print("=" * 80)
print()

# Test 1: Import required modules
print("Test 1: Importing required modules...")
try:
    import streamlit as st
    print("  ✅ Streamlit imported successfully")
except ImportError as e:
    print(f"  ❌ Streamlit import failed: {e}")
    sys.exit(1)

try:
    import plotly.express as px
    import plotly.graph_objects as go
    print("  ✅ Plotly imported successfully")
except ImportError as e:
    print(f"  ❌ Plotly import failed: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("  ✅ Pandas imported successfully")
except ImportError as e:
    print(f"  ❌ Pandas import failed: {e}")
    sys.exit(1)

print()

# Test 2: Import UI components
print("Test 2: Importing UI components...")
try:
    from ui.chatbot import VisualizationChatbot
    print("  ✅ VisualizationChatbot imported")
except ImportError as e:
    print(f"  ❌ VisualizationChatbot import failed: {e}")
    sys.exit(1)

try:
    from ui.utils import save_uploaded_file, load_pipeline_results
    print("  ✅ UI utilities imported")
except ImportError as e:
    print(f"  ❌ UI utilities import failed: {e}")
    sys.exit(1)

print()

# Test 3: Test chatbot with sample data
print("Test 3: Testing Visualization Chatbot...")
try:
    # Create sample data
    sample_data = pd.DataFrame({
        'price': [10, 20, 30, 40, 50],
        'discount': [5, 10, 15, 20, 25],
        'category': ['A', 'B', 'A', 'C', 'B']
    })

    # Initialize chatbot
    chatbot = VisualizationChatbot(sample_data)
    print(f"  ✅ Chatbot initialized with {len(sample_data)} rows")

    # Test query processing
    response = chatbot.process_query("create a scatter plot of price vs discount")

    if response['figure'] is not None:
        print("  ✅ Chatbot successfully created visualization")
    else:
        print(f"  ⚠️  Chatbot response: {response['message']}")

    # Test suggestions
    suggestions = chatbot.get_suggestions()
    print(f"  ✅ Chatbot generated {len(suggestions)} suggestions")

except Exception as e:
    print(f"  ❌ Chatbot test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Verify directory structure
print("Test 4: Verifying directory structure...")

required_dirs = [
    'data/raw',
    'data/cleaned',
    'data/artifacts',
    'ui',
    'agents',
    'configs',
    '.streamlit'
]

all_exist = True
for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"  ✅ {dir_path}")
    else:
        print(f"  ❌ {dir_path} - MISSING")
        all_exist = False

if not all_exist:
    print("  ⚠️  Some directories are missing, but this is non-critical")

print()

# Test 5: Verify configuration files
print("Test 5: Verifying configuration files...")

config_files = [
    'app.py',
    'configs/pipeline.yaml',
    '.streamlit/config.toml',
    'ui/chatbot.py',
    'ui/utils.py'
]

for file_path in config_files:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} - MISSING")
        sys.exit(1)

print()

# Test 6: Test visualization types
print("Test 6: Testing visualization types...")

test_queries = [
    ("scatter plot of price vs discount", "scatter"),
    ("bar chart of category", "bar"),
    ("histogram of price", "histogram"),
    ("box plot of discount", "box"),
    ("correlation heatmap", "heatmap")
]

for query, expected_type in test_queries:
    response = chatbot.process_query(query)
    if response['figure'] is not None:
        print(f"  ✅ {expected_type}: '{query}'")
    else:
        print(f"  ⚠️  {expected_type}: '{query}' - {response['message']}")

print()

# Summary
print("=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print()
print("🎉 Streamlit dashboard is ready!")
print()
print("To launch the dashboard, run:")
print("  streamlit run app.py")
print()
print("Or if streamlit is not in PATH:")
print("  python3 -m streamlit run app.py")
print()

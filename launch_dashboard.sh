#!/bin/bash
# Launch script for Streamlit Dashboard

echo "🚀 Launching Agentic Data Pipeline Dashboard..."
echo ""

# Check if streamlit is installed
if command -v streamlit &> /dev/null; then
    streamlit run app.py
elif python3 -m streamlit --version &> /dev/null; then
    python3 -m streamlit run app.py
else
    echo "❌ Streamlit is not installed!"
    echo ""
    echo "Please install dependencies first:"
    echo "  pip3 install -r requirements.txt"
    exit 1
fi

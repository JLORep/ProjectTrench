#!/bin/bash
echo "🚀 Starting TrenchCoat Elite Pro on Azure..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export STREAMLIT_SERVER_PORT=8000
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true

# Create data directories
mkdir -p data/backups
mkdir -p logs

# Initialize database
python -c "from src.data.database import CoinDatabase; db = CoinDatabase(); print('Database initialized')"

# Start the application
streamlit run secure_main_app.py --server.port=8000 --server.address=0.0.0.0 --server.headless=true
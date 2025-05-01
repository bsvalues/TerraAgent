#!/bin/bash

# TerraAgent - One-Click Deployment Script
# This script sets up and runs the TerraAgent application

echo "Starting TerraAgent - PACS Training Assistant..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or later."
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
echo "Reading dependencies from dependencies.md..."
# Extract dependency names from dependencies.md and install them
DEPS=$(grep "^- " dependencies.md | grep -v "^- \[" | sed 's/- //' | tr '\n' ' ')
echo "Installing: $DEPS"
pip install $DEPS

# Check if .env file exists, if not create a template
if [ ! -f ".env" ]; then
    echo "Creating .env file template..."
    cat > .env << EOL
# TerraAgent Environment Variables
# Replace these values with your actual credentials

# Database configuration (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/cama_data

# OpenAI API configuration
OPENAI_API_KEY=your_api_key_here

# Session security
SESSION_SECRET=your_secure_random_string_here
EOL
    echo ".env template created. Please edit it with your actual values."
    echo "Please edit the .env file with your credentials before continuing."
    exit 1
fi

# Start the application
echo "Starting TerraAgent application..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

echo "TerraAgent is running at http://localhost:5000"
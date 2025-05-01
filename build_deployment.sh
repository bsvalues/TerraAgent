#!/bin/bash

# TerraAgent Deployment Builder
# This script creates a deployment package for TerraAgent

echo "Building TerraAgent Deployment Package"
echo "======================================"

# Create deployment directory
DEPLOY_DIR="terraagent_deployment"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy necessary files
echo "Copying application files..."
cp -r templates/ $DEPLOY_DIR/
cp -r static/ $DEPLOY_DIR/
cp -r utils/ $DEPLOY_DIR/
cp -r chains/ $DEPLOY_DIR/
cp *.py $DEPLOY_DIR/
cp dependencies.md $DEPLOY_DIR/
cp README.md $DEPLOY_DIR/
cp start_application.sh $DEPLOY_DIR/
cp start_application.bat $DEPLOY_DIR/
cp create_desktop_shortcut.bat $DEPLOY_DIR/
cp .env.example $DEPLOY_DIR/.env.example

# Create .env template file
echo "Creating .env template..."
cat > $DEPLOY_DIR/.env << EOL
# TerraAgent Environment Variables
# Replace these values with your actual credentials

# Database configuration (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/cama_data

# OpenAI API configuration
OPENAI_API_KEY=your_api_key_here

# Session security
SESSION_SECRET=your_secure_random_string_here
EOL

# Create brief instructions
echo "Creating quick start guide..."
cat > $DEPLOY_DIR/QUICK_START.md << EOL
# TerraAgent Quick Start Guide

## Windows Users
Option 1 - Desktop Shortcut:
1. Double-click the \`create_desktop_shortcut.bat\` file
2. A shortcut will be created on your desktop
3. Double-click the desktop shortcut to start TerraAgent
4. Follow the on-screen instructions
5. Edit the .env file with your credentials when prompted

Option 2 - Direct Start:
1. Double-click the \`start_application.bat\` file
2. Follow the on-screen instructions
3. Edit the .env file with your credentials when prompted
4. The application will start automatically at http://localhost:5000

## Linux/Mac Users
1. Open a terminal in this directory
2. Run \`chmod +x start_application.sh\`
3. Run \`./start_application.sh\`
4. Edit the .env file with your credentials when prompted
5. The application will start automatically at http://localhost:5000

## Need Help?
See the full README.md file for more detailed instructions and troubleshooting.
EOL

# Create archive
echo "Creating deployment archive..."
zip -r terraagent_deployment.zip $DEPLOY_DIR

# Cleanup
echo "Cleaning up..."
rm -rf $DEPLOY_DIR

echo "Deployment package created: terraagent_deployment.zip"
echo "Share this file with users for easy installation."
#!/bin/bash

# Create the project root directory
mkdir -p rescue-rover

# Create the application structure
mkdir -p rescue-rover/app
mkdir -p rescue-rover/app/api
mkdir -p rescue-rover/app/rover
mkdir -p rescue-rover/app/static/css
mkdir -p rescue-rover/app/static/js
mkdir -p rescue-rover/app/static/images
mkdir -p rescue-rover/app/templates
mkdir -p rescue-rover/tests

# Create necessary Python modules
touch rescue-rover/app/__init__.py
touch rescue-rover/app/api/__init__.py
touch rescue-rover/app/api/rover_api.py  # For API integration
touch rescue-rover/app/rover/__init__.py
touch rescue-rover/app/rover/navigation.py  # For navigation without GPS
touch rescue-rover/app/rover/detection.py  # For survivor detection
touch rescue-rover/app/rover/battery.py  # For battery management

# Create static files
touch rescue-rover/app/static/css/styles.css
touch rescue-rover/app/static/js/app.js
touch rescue-rover/app/static/js/map.js  # For map visualization

# Create HTML templates
touch rescue-rover/app/templates/index.html
touch rescue-rover/app/templates/dashboard.html

# Create main application files
touch rescue-rover/app.py
touch rescue-rover/config.py
touch rescue-rover/.env
touch rescue-rover/.gitignore
touch rescue-rover/README.md
touch rescue-rover/requirements.txt

# Create initial content for requirements.txt
cat > rescue-rover/requirements.txt << EOL
Flask==2.3.3
requests==2.31.0
numpy==1.25.2
matplotlib==3.7.2
EOL

# Create initial content for .gitignore
cat > rescue-rover/.gitignore << EOL
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.DS_Store
EOL

# Create initial README content
cat > rescue-rover/README.md << EOL
# Autonomous Rescue Rover for Disaster Zones

A web application for controlling an autonomous rover that can navigate disaster zones, detect survivors, and deliver aid with minimal human intervention.

## Features
- Navigate disaster zones without GPS using dead reckoning and landmark recognition
- Detect survivors using sensor data (ultrasonic, IR, RFID, accelerometer)
- Deliver aid and return safely with minimal human intervention
- Operate with constraints on power and communication

## Installation
1. Clone this repository
2. Install requirements: \`pip install -r requirements.txt\`
3. Run the application: \`python app.py\`

## API Integration
This application interacts with the Rover API endpoints to control and monitor the rover.

## Constraints
- The rover stops moving when recharging
- Recharging starts at 5% battery and stops at 80%
- Communication is lost when battery is below 10%
EOL

echo "Autonomous Rescue Rover project structure created successfully!"

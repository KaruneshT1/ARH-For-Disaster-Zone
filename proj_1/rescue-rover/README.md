# Autonomous Rescue Rover for Disaster Zones

A web application for controlling an autonomous rover that can navigate disaster zones, detect survivors, and deliver aid with minimal human intervention.

## Features
- Navigate disaster zones without GPS using dead reckoning and landmark recognition
- Detect survivors using sensor data (ultrasonic, IR, RFID, accelerometer)
- Deliver aid and return safely with minimal human intervention
- Operate with constraints on power and communication

## Installation
1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## API Integration
This application interacts with the Rover API endpoints to control and monitor the rover.

## Constraints
- The rover stops moving when recharging
- Recharging starts at 5% battery and stops at 80%
- Communication is lost when battery is below 10%

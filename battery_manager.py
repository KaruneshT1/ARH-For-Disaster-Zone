import time
from api_comm import get_rover_status, move_rover, stop_rover

# Monitor battery and handle recharging
def monitor_battery(session_id):
    rover_status = get_rover_status(session_id)
    if rover_status:
        battery_level = rover_status.get("battery", {}).get("level", 100)  # Assuming JSON structure
        print(f"Current battery level: {battery_level}%")
        
        # If battery is below 10%, stop rover and wait for recharge
        if battery_level < 10:
            print("Battery is critically low, stopping rover.")
            stop_rover(session_id)
            print("Waiting for rover to recharge above 10%...")
            wait_for_recharge(session_id)
        
        # Handle recharging
        elif battery_level < 80 and battery_level >= 5:
            print(f"Recharging rover, current level: {battery_level}%")
            wait_for_recharge(session_id)
        
        else:
            print("Battery level sufficient for operation.")
            return True

    return False

# Simulate recharging process
def wait_for_recharge(session_id):
    while True:
        rover_status = get_rover_status(session_id)
        battery_level = rover_status.get("battery", {}).get("level", 100)
        
        if battery_level >= 10:
            print(f"Rover recharged to {battery_level}%. Resuming operation.")
            break
        
        print(f"Current battery level: {battery_level}%. Waiting to recharge...")
        time.sleep(5)  # Check every 5 seconds

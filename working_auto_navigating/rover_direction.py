def determine_rover_direction(current_direction, rfid, ir_sensor, ultrasonic, accelerometer):
    """
    Determine the next direction for the rover based on sensor data.
    
    Args:
        current_direction (str): The rover's current direction ('forward', 'backward', 'left', 'right')
        rfid (bool): Whether RFID tag is detected
        ir_sensor (bool): Whether IR sensor detects reflection
        ultrasonic (tuple): A tuple of (distance, detection) from ultrasonic sensor
        accelerometer (list): A list of [x, y, z] accelerometer values
    
    Returns:
        str: The next direction or "Reached" if destination reached
    """
    try:
        # Normalize current_direction to lowercase
        if current_direction is None:
            current_direction = "forward"
        
        current_direction = current_direction.lower()
        
        # Parse input parameters with better error handling
        try:
            if isinstance(accelerometer, list):
                # Use list indexing with error handling
                x = accelerometer[0] if len(accelerometer) > 0 else 0
                y = accelerometer[1] if len(accelerometer) > 1 else 0
                z = accelerometer[2] if len(accelerometer) > 2 else 0
            elif isinstance(accelerometer, tuple):
                x = accelerometer[0] if len(accelerometer) > 0 else 0
                y = accelerometer[1] if len(accelerometer) > 1 else 0
                z = accelerometer[2] if len(accelerometer) > 2 else 0
            else:
                # Default values if not list or tuple
                print(f"Warning: accelerometer data is not a list or tuple: {type(accelerometer)}")
                x, y, z = 0, 0, 0
        except Exception as e:
            print(f"Error processing accelerometer data: {str(e)}, using defaults")
            x, y, z = 0, 0, 0
        
        try:
            if isinstance(ultrasonic, tuple):
                ultrasonic_distance = ultrasonic[0] if len(ultrasonic) > 0 else 0
                ultrasonic_detected = ultrasonic[1] if len(ultrasonic) > 1 else False
            elif isinstance(ultrasonic, list):
                ultrasonic_distance = ultrasonic[0] if len(ultrasonic) > 0 else 0
                ultrasonic_detected = ultrasonic[1] if len(ultrasonic) > 1 else False
            else:
                # Default values if not tuple or list
                print(f"Warning: ultrasonic data is not a tuple or list: {type(ultrasonic)}")
                ultrasonic_distance, ultrasonic_detected = 0, False
        except Exception as e:
            print(f"Error processing ultrasonic data: {str(e)}, using defaults")
            ultrasonic_distance, ultrasonic_detected = 0, False
        
        # Convert to proper types
        try:
            ultrasonic_distance = float(ultrasonic_distance)
        except (ValueError, TypeError):
            ultrasonic_distance = 0
        
        ultrasonic_detected = bool(ultrasonic_detected)
        rfid = bool(rfid)
        ir_sensor = bool(ir_sensor)
        
        print(f"Direction calculation with: current={current_direction}, rfid={rfid}, ir={ir_sensor}, " +
              f"ultrasonic=({ultrasonic_distance}, {ultrasonic_detected}), accel=({x}, {y}, {z})")
        
        # Rover speed is 1 unit/sec; adjust acceleration to compute drift
        drift_x = x - (1 if current_direction == "right" else -1 if current_direction == "left" else 0)
        drift_y = y - (1 if current_direction == "forward" else -1 if current_direction == "backward" else 0)
        
        # Logic to determine direction based on sensor data
        if rfid and ir_sensor and ultrasonic_detected and abs(ultrasonic_distance) <= 5:
            return "Reached"
        
        elif rfid and not ir_sensor:
            return "Right" if drift_x > 0 else "Left" if drift_x < 0 else "Forward" if drift_y > 0 else "Backward"
        
        elif not rfid and ir_sensor:
            return "Right" if drift_x > 0 else "Left"
        
        elif not ir_sensor and ultrasonic_detected:
            return "Forward" if drift_y > 0 else "Backward"
        
        elif ir_sensor and ultrasonic_detected:
            if abs(ultrasonic_distance) <= 5:
                return "Reached"
            return "Right" if drift_x > 0 else "Left" if drift_x < 0 else "Forward" if drift_y > 0 else "Backward"
        
        else:
            return "Right" if drift_x > 0 else "Left" if drift_x < 0 else "Forward" if drift_y > 0 else "Backward"
            
    except Exception as e:
        print(f"Error in determine_rover_direction: {str(e)}")
        # Default to forward as a safe option if there's any error
        return "Forward"

# Test case
if __name__ == "__main__":
    # Example Usage
    direction = determine_rover_direction("forward", True, True, (4, True), [0.5, 0.2, 0.1])
    print(f"Result: {direction}")
    
    # Test with problematic inputs
    print("Testing with problematic inputs:")
    print(determine_rover_direction(None, None, False, (None, None), None))
    print(determine_rover_direction("forward", True, True, [], []))
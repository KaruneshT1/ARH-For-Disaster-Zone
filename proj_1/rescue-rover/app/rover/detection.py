class SurvivorDetector:
    def __init__(self):
        self.survivors = []
        
    def detect_survivors(self, sensor_data, current_position):
        """Detect survivors using sensor data"""
        # Using IR sensor for heat signatures
        if 'ir' in sensor_data and sensor_data['ir'].get('heat_signature', 0) > 30:
            new_survivor = {
                'position': current_position,
                'time_detected': time.time(),
                'aid_delivered': False
            }
            
            # Check if this is a new survivor
            is_new = True
            for survivor in self.survivors:
                distance = self.calculate_distance(survivor['position'], current_position)
                if distance < 2.0:  # Within 2 meters, consider same survivor
                    is_new = False
                    break
                    
            if is_new:
                self.survivors.append(new_survivor)
                print(f"New survivor detected at {current_position}")

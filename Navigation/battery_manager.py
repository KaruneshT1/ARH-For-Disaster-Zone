class BatteryManager:
    def __init__(self, initial_battery_level=100, low_battery_threshold=10, recharge_threshold=80, critical_battery_level=5):
        """
        Initialize the BatteryManager with given parameters.
        
        Args:
            initial_battery_level (int): The initial battery level in percentage (default is 100%).
            low_battery_threshold (int): Battery level percentage below which communication is lost (default is 10%).
            recharge_threshold (int): Battery level percentage at which recharging stops (default is 80%).
            critical_battery_level (int): Minimum battery percentage required to maintain operation (default is 5%).
        """
        self.battery_level = initial_battery_level
        self.low_battery_threshold = low_battery_threshold
        self.recharge_threshold = recharge_threshold
        self.critical_battery_level = critical_battery_level
        self.recharging = False
        self.communication_status = "Active" if self.battery_level > self.low_battery_threshold else "Inactive"
        self.status = "idle"  # Initial status is idle
        
    def get_battery_status(self):
        """Returns the current battery status and relevant rover information."""
        return {
            "status": self.status,
            "battery": self.battery_level,
            "coordinates": [174, 122],  # Placeholder coordinates for simplicity
        }

    def get_detailed_status(self):
        """Returns a more detailed status of the rover, including sensor data and battery level."""
        return {
            "timestamp": 1743490037.279617,  # Example timestamp
            "position": {
                "x": 174,
                "y": 122
            },
            "accelerometer": {
                "x": -0.06,
                "y": 0.03,
                "z": 0.29
            },
            "battery_level": self.battery_level,
            "communication_status": self.communication_status,
            "recharging": self.recharging
        }

    def recharge_battery(self):
        """Recharges the battery if it is below the threshold."""
        if self.battery_level < self.recharge_threshold and not self.recharging:
            print("Starting recharging...")
            self.recharging = True
            while self.battery_level < self.recharge_threshold:
                self.battery_level += 1  # Simulating recharging by incrementing the battery level
                # In a real scenario, you would control the charge rate and simulate delay
            self.recharging = False
            self.communication_status = "Active" if self.battery_level > self.low_battery_threshold else "Inactive"
            print(f"Recharging complete. Battery level: {self.battery_level}%")

    def stop_recharge(self):
        """Stops recharging once the battery is sufficient."""
        if self.battery_level >= self.recharge_threshold:
            self.recharging = False
            print("Battery level sufficient. Stopping recharging.")

    def update_battery_level(self, new_battery_level):
        """
        Update the battery level with a new value, and adjust communication status.
        
        Args:
            new_battery_level (int): The new battery level in percentage.
        """
        self.battery_level = new_battery_level
        if self.battery_level < self.low_battery_threshold:
            self.communication_status = "Inactive"
        else:
            self.communication_status = "Active"
        
    def manage_battery_and_communication(self):
        """
        Check battery status, manage recharging, and handle communication status.
        """
        if self.battery_level < self.critical_battery_level:
            self.status = "stopped"  # Rover stops operation if the battery is critically low
            print("Critical battery level reached. Rover stopped.")
        elif self.battery_level <= self.low_battery_threshold:
            self.status = "idle"  # Rover is idle if the battery is too low
            self.communication_status = "Inactive"  # Communication is lost if below the threshold
            print("Battery low. Communication lost.")
        else:
            self.status = "moving"  # Rover is operational when battery is sufficient
            print("Battery sufficient. Rover is moving.")

    def handle_battery_cycle(self):
        """Periodically checks battery status and handles recharging if needed."""
        if self.battery_level <= self.low_battery_threshold:
            self.recharge_battery()

    def check_communication_status(self):
        """Check if communication is active based on battery level."""
        if self.battery_level < self.low_battery_threshold:
            self.communication_status = "Inactive"
        else:
            self.communication_status = "Active"

    def simulate_movement(self, movement_type):
        """Simulate movement based on the rover's current battery status."""
        if self.battery_level <= self.critical_battery_level:
            print("Battery too low to move.")
            self.status = "stopped"
        else:
            print(f"Rover moving {movement_type} with battery at {self.battery_level}%")
            self.status = "moving"
        
# Example usage

if __name__ == "__main__":
    battery_manager = BatteryManager()

    # Example flow for rover operation
    battery_manager.update_battery_level(98)  # Initial battery level update
    print(battery_manager.get_battery_status())
    
    # Simulate a low battery scenario
    battery_manager.update_battery_level(7)
    battery_manager.manage_battery_and_communication()
    print(battery_manager.get_detailed_status())
    
    # Recharge and verify communication status
    battery_manager.recharge_battery()
    print(battery_manager.get_detailed_status())

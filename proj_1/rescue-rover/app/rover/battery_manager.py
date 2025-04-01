# battery_manager.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('battery_manager')

class BatteryManager:
    def __init__(self):
        self.battery_level = 100  # Start with full battery
        self.is_charging = False
        self.has_communication = True
        
        # Constraints from the challenge requirements
        self.charging_start_threshold = 5    # Start charging at 5%
        self.charging_stop_threshold = 80    # Stop charging at 80%
        self.communication_threshold = 10    # Lose communication at <10%
        
    def update_battery_level(self, level):
        """Update battery level and check constraints"""
        self.battery_level = level
        
        # Check charging state
        previous_charging = self.is_charging
        
        if self.battery_level <= self.charging_start_threshold and not self.is_charging:
            self.is_charging = True
            logger.info(f"Battery at {self.battery_level}% - Starting to charge")
        elif self.battery_level >= self.charging_stop_threshold and self.is_charging:
            self.is_charging = False
            logger.info(f"Battery at {self.battery_level}% - Charging complete")
            
        # Check communication state
        previous_communication = self.has_communication
        
        if self.battery_level < self.communication_threshold:
            self.has_communication = False
            if previous_communication:
                logger.warning(f"Battery at {self.battery_level}% - Communication lost")
        else:
            self.has_communication = True
            if not previous_communication:
                logger.info(f"Battery at {self.battery_level}% - Communication restored")
                
        # Return whether state changed
        return previous_charging != self.is_charging or previous_communication != self.has_communication

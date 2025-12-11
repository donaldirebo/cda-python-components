#####
#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# This module provides tilt alert actuation using the SenseHAT
# emulator's LED matrix for visual alerts.
#

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class TiltAlertActuatorTask(BaseActuatorSimTask):
    """
    Tilt alert actuator using SenseHAT LED matrix.
    
    Displays a red warning pattern on the LED matrix when tilt
    threshold is exceeded, and clears the display when tilt
    returns to safe levels.
    """
    
    def __init__(self):
        """
        Initialize the tilt alert actuator task.
        """
        super(TiltAlertActuatorTask, self).__init__(
            name=ConfigConst.TILT_ALERT_ACTUATOR_NAME,
            typeID=ConfigConst.TILT_ALERT_ACTUATOR_TYPE,
            simpleName="TILT_ALERT"
        )
        
        # Import and initialize sense_emu SenseHat for LED display
        from sense_emu import SenseHat
        self.sh = SenseHat()
    
    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Activate the tilt alert - display warning on LED matrix.
        
        @param val: The tilt angle value that triggered the alert
        @param stateData: Optional state data message
        @return: Status code indicating success or failure
        """
        try:
            print(f"TILT ALERT ACTIVATED - Tilt angle: {val:.1f}°")
            
            # Display red warning pattern on LED matrix
            red = (255, 0, 0)
            self.sh.clear(red)
            
            return 0
        except Exception as e:
            print(f"Error activating tilt alert: {e}")
            return -1
    
    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Deactivate the tilt alert - clear the LED matrix.
        
        @param val: The current tilt angle value
        @param stateData: Optional state data message
        @return: Status code indicating success or failure
        """
        try:
            print(f"TILT ALERT DEACTIVATED - Tilt angle: {val:.1f}°")
            
            # Clear the LED matrix (set to black)
            self.sh.clear()
            
            return 0
        except Exception as e:
            print(f"Error deactivating tilt alert: {e}")
            return -1
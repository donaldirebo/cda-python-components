#####
#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# This module provides accelerometer sensor emulation for tilt detection
# using the SenseHAT emulator's orientation capabilities.
#
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask

class AccelerometerSensorEmulatorTask(BaseSensorSimTask):
    """
    Accelerometer sensor emulator using SenseHAT orientation data.
    
    Reads pitch, roll, and yaw values from the SenseHAT emulator.
    Returns the maximum absolute tilt angle for threshold comparison,
    and can send individual axis data through a listener.
    """
    
    def __init__(self, dataSet=None):
        """
        Initialize the accelerometer sensor emulator task.
        """
        super(AccelerometerSensorEmulatorTask, self).__init__(
            name=ConfigConst.ACCELEROMETER_SENSOR_NAME,
            typeID=ConfigConst.ACCELEROMETER_SENSOR_TYPE
        )
        
        # Import and initialize sense_emu SenseHat for orientation data
        from sense_emu import SenseHat
        self.sh = SenseHat()
        
        # Listener for sending additional axis data
        self.dataMessageListener = None
        
        # Store latest axis readings
        self.latestPitch = 0.0
        self.latestRoll = 0.0
        self.latestYaw = 0.0
    
    def setDataMessageListener(self, listener):
        """
        Set the data message listener for sending individual axis readings.
        
        @param listener: The IDataMessageListener to receive axis data
        """
        self.dataMessageListener = listener
    
    def generateTelemetry(self) -> SensorData:
        """
        Generate telemetry data from the accelerometer sensor.
        
        Reads orientation data (pitch, roll, yaw) from the SenseHAT emulator,
        sends individual axis data through the listener, and returns the 
        maximum absolute tilt angle for threshold evaluation.
        
        @return: SensorData object containing the max tilt angle value
        """
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        
        try:
            # Read orientation from emulator
            orientation = self.sh.get_orientation()
            pitch = orientation.get('pitch', 0)
            roll = orientation.get('roll', 0)
            yaw = orientation.get('yaw', 0)
            
            # Normalize angles to -180 to 180 range
            if pitch > 180:
                pitch = pitch - 360
            if roll > 180:
                roll = roll - 360
            if yaw > 180:
                yaw = yaw - 360
            
            # Store latest readings
            self.latestPitch = pitch
            self.latestRoll = roll
            self.latestYaw = yaw
            
            # Use maximum absolute tilt angle for threshold comparison
            maxTilt = max(abs(pitch), abs(roll))
            
            print(f"ACCELEROMETER READ - Pitch: {pitch:.1f}°, Roll: {roll:.1f}°, Yaw: {yaw:.1f}°, Max Tilt: {maxTilt:.1f}°")
            
            sensorData.setValue(maxTilt)
            
            # Send individual axis data through listener
            if self.dataMessageListener:
                self._sendAxisData(pitch, roll, yaw)
            
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
            sensorData.setValue(0.0)
        
        self.latestSensorData = sensorData
        return sensorData
    
    def _sendAxisData(self, pitch: float, roll: float, yaw: float):
        """
        Send individual axis readings through the data message listener.
        """
        try:
            # Create and send Pitch sensor data
            pitchData = SensorData(
                name=ConfigConst.PITCH_SENSOR_NAME,
                typeID=ConfigConst.PITCH_SENSOR_TYPE
            )
            pitchData.setValue(pitch)
            self.dataMessageListener.handleSensorMessage(pitchData)
            
            # Create and send Roll sensor data
            rollData = SensorData(
                name=ConfigConst.ROLL_SENSOR_NAME,
                typeID=ConfigConst.ROLL_SENSOR_TYPE
            )
            rollData.setValue(roll)
            self.dataMessageListener.handleSensorMessage(rollData)
            
            # Create and send Yaw sensor data
            yawData = SensorData(
                name=ConfigConst.YAW_SENSOR_NAME,
                typeID=ConfigConst.YAW_SENSOR_TYPE
            )
            yawData.setValue(yaw)
            self.dataMessageListener.handleSensorMessage(yawData)
            
        except Exception as e:
            print(f"Error sending axis data: {e}")

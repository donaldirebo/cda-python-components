import logging
import time

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.data.DataUtil import DataUtil

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.cda.connection.CoapServerAdapter import CoapServerAdapter

class DeviceDataManager(IDataMessageListener):
	"""
	Central data manager for the Constrained Device Application.
	Coordinates all sensor, actuator, and system performance management.
	"""
	
	def __init__(self):
		self.configUtil = ConfigUtil()
		
		self.enableSystemPerf = \
			self.configUtil.getBoolean(
				section = ConfigConst.CONSTRAINED_DEVICE, 
				key = ConfigConst.ENABLE_SYSTEM_PERF_KEY)
			
		self.enableSensing = \
			self.configUtil.getBoolean(
				section = ConfigConst.CONSTRAINED_DEVICE, 
				key = ConfigConst.ENABLE_SENSING_KEY)
		
		# NOTE: this can also be retrieved from the configuration file
		self.enableActuation = True
		
		self.enableMqttClient = \
			self.configUtil.getBoolean(
				section = ConfigConst.CONSTRAINED_DEVICE,
				key = ConfigConst.ENABLE_MQTT_CLIENT_KEY)
		
		self.enableCoapServer = \
			self.configUtil.getBoolean(
				section = ConfigConst.CONSTRAINED_DEVICE,
				key = ConfigConst.ENABLE_COAP_SERVER_KEY)
		
		self.sysPerfMgr = None
		self.sensorAdapterMgr = None
		self.actuatorAdapterMgr = None
		
		# Caches for data
		self.actuatorResponseCache = {}
		self.sensorDataCache = {}
		self.systemPerformanceDataCache = {}
		
		# MQTT client initialization
		self.mqttClient = None
		
		if self.enableMqttClient:
			self.mqttClient = MqttClientConnector()
			self.mqttClient.setDataMessageListener(self)
			logging.info("MQTT client enabled")
		
		# CoAP server initialization
		self.coapServer = None
		
		if self.enableCoapServer:
			self.coapServer = CoapServerAdapter(dataMsgListener = self)
			logging.info("CoAP server enabled")
		
		# NOTE: The following aren't used until Part III
		self.coapClient = None
		
		if self.enableSystemPerf:
			self.sysPerfMgr = SystemPerformanceManager()
			self.sysPerfMgr.setDataMessageListener(self)
			logging.info("Local system performance tracking enabled")
		
		if self.enableSensing:
			self.sensorAdapterMgr = SensorAdapterManager()
			self.sensorAdapterMgr.setDataMessageListener(self)
			logging.info("Local sensor tracking enabled")
			
		if self.enableActuation:
			self.actuatorAdapterMgr = ActuatorAdapterManager(dataMsgListener = self)
			logging.info("Local actuation capabilities enabled")
		
		# Temperature threshold configuration
		self.handleTempChangeOnDevice = \
			self.configUtil.getBoolean(
				ConfigConst.CONSTRAINED_DEVICE, 
				ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY)
			
		self.triggerHvacTempFloor = \
			self.configUtil.getFloat(
				ConfigConst.CONSTRAINED_DEVICE, 
				ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY)
				
		self.triggerHvacTempCeiling = \
			self.configUtil.getFloat(
				ConfigConst.CONSTRAINED_DEVICE, 
				ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY)
		
		# Tilt/Accelerometer threshold configuration
		self.handleTiltChangeOnDevice = \
			self.configUtil.getBoolean(
				ConfigConst.CONSTRAINED_DEVICE, 
				ConfigConst.HANDLE_TILT_CHANGE_ON_DEVICE_KEY)
		
		self.triggerTiltMaxAngle = \
			self.configUtil.getFloat(
				ConfigConst.CONSTRAINED_DEVICE, 
				ConfigConst.TRIGGER_TILT_MAX_ANGLE_KEY,
				defaultVal = 15.0)
		
		# Track tilt alert state to avoid repeated triggers
		self.tiltAlertActive = False
		
	def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
		"""
		Retrieves the named actuator data (response) item from the internal data cache.
		"""
		if name in self.actuatorResponseCache:
			return self.actuatorResponseCache[name]
		return None
		
	def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
		"""
		Retrieves the named sensor data item from the internal data cache.
		"""
		if name in self.sensorDataCache:
			return self.sensorDataCache[name]
		return None
	
	def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
		"""
		Retrieves the named system performance data from the internal data cache.
		"""
		if name in self.systemPerformanceDataCache:
			return self.systemPerformanceDataCache[name]
		return None
	
	def handleActuatorCommandMessage(self, data: ActuatorData) -> ActuatorData:
		"""
		Callback for incoming actuator command messages.
		"""
		logging.info("Actuator data: " + str(data))
		
		if data:
			logging.info("Processing actuator command message.")
			response = self.actuatorAdapterMgr.sendActuatorCommand(data)
			if response:
				logging.info("Incoming actuator response received (from actuator manager): " + str(response))
			return response
		else:
			logging.warning("Incoming actuator command is invalid (null). Ignoring.")
			return None
	
	def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
		"""
		Callback for actuator command responses.
		"""
		if data:
			logging.debug("Incoming actuator response received (from actuator manager): " + str(data))
			
			# Store the data in the cache
			self.actuatorResponseCache[data.getName()] = data
			
			# TODO: In Part III, convert to JSON and send upstream
			
			return True
		else:
			logging.warning("Incoming actuator response is invalid (null). Ignoring.")
			return False
	
	def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
		"""
		Callback for incoming string-based messages.
		"""
		logging.info("Incoming message received: " + msg)
		
		# TODO: Implement message parsing and handling in Part III
		
		return True
	
	def handleSensorMessage(self, data: SensorData) -> bool:
		"""
		Callback for incoming sensor messages.
		
		PIOT-CDA-10-004: Sends sensor data upstream to GDA via MQTT
		"""
		if data:
			logging.info("Incoming sensor data received (from sensor manager): " + str(data))
			
			# Store in cache
			self.sensorDataCache[data.getName()] = data
			
			# Step 1: Analyze sensor data (check thresholds, trigger actuators)
			self._handleSensorDataAnalysis(data=data)
			
			# Step 2: Convert to JSON
			jsonData = DataUtil().sensorDataToJson(data=data)
			
			# Step 3: Send upstream to GDA via MQTT
			self._handleUpstreamTransmission(
				resourceName=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, 
				msg=jsonData
			)
			
			return True
		else:
			logging.warning("Incoming sensor data is invalid (null). Ignoring.")
			return False
	
	def handleSystemPerformanceMessage(self, data: SystemPerformanceData) -> bool:
		"""
		Callback for incoming system performance messages.
		
		PIOT-CDA-10-004: Sends system performance data upstream to GDA via MQTT
		"""
		if data:
			logging.info("Incoming system performance message received (from sys perf manager): " + str(data))
			
			# Store in cache
			self.systemPerformanceDataCache[data.getName()] = data
			
			# Step 1: Convert to JSON
			jsonData = DataUtil().systemPerformanceDataToJson(data=data)
			
			# Step 2: Send upstream to GDA via MQTT
			self._handleUpstreamTransmission(
				resourceName=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, 
				msg=jsonData
			)
			
			return True
		else:
			logging.warning("Incoming system performance data is invalid (null). Ignoring.")
			return False
	
	def startManager(self):
		"""
		Starts all managed components.
		"""
		logging.info("Starting DeviceDataManager...")
		
		if self.sysPerfMgr:
			self.sysPerfMgr.startManager()
		
		if self.sensorAdapterMgr:
			self.sensorAdapterMgr.startManager()
		
		if self.mqttClient:
			self.mqttClient.connectClient()
			
			# Wait for connection to complete before subscribing
			time.sleep(1)
			
			self.mqttClient.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, callback = None, qos = ConfigConst.DEFAULT_QOS)
		
		if self.coapServer:
			self.coapServer.startServer()
			
		logging.info("Started DeviceDataManager.")
		
	def stopManager(self):
		"""
		Stops all managed components.
		"""
		logging.info("Stopping DeviceDataManager...")
		
		if self.sysPerfMgr:
			self.sysPerfMgr.stopManager()
		
		if self.sensorAdapterMgr:	
			self.sensorAdapterMgr.stopManager()
		
		if self.mqttClient:
			self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
			self.mqttClient.disconnectClient()
		
		if self.coapServer:
			self.coapServer.stopServer()
			
		logging.info("Stopped DeviceDataManager.")
		
	def _handleIncomingDataAnalysis(self, msg: str):
		"""
		Analyzes incoming messages and takes action if needed.
		"""
		# TODO: Implement in Part III
		pass
		
	def _handleSensorDataAnalysis(self, data: SensorData):
		"""
		Analyzes sensor data and triggers actuator commands if needed.
		
		Handles both temperature and tilt/accelerometer threshold checking.
		"""
		# Handle temperature threshold checking
		if self.handleTempChangeOnDevice and data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
			logging.info("Handle temp change: %s - type ID: %s", str(self.handleTempChangeOnDevice), str(data.getTypeID()))
			
			ad = ActuatorData(typeID = ConfigConst.HVAC_ACTUATOR_TYPE)
			ad.setLocationID(data.getLocationID())
			
			if data.getValue() > self.triggerHvacTempCeiling:
				ad.setCommand(ConfigConst.COMMAND_ON)
				ad.setValue(self.triggerHvacTempCeiling)
			elif data.getValue() < self.triggerHvacTempFloor:
				ad.setCommand(ConfigConst.COMMAND_ON)
				ad.setValue(self.triggerHvacTempFloor)
			else:
				ad.setCommand(ConfigConst.COMMAND_OFF)
				
			self.handleActuatorCommandMessage(ad)
		
		# Handle tilt/accelerometer threshold checking
		if self.handleTiltChangeOnDevice and data.getTypeID() == ConfigConst.ACCELEROMETER_SENSOR_TYPE:
			logging.info("Handle tilt change: %s - type ID: %s", str(self.handleTiltChangeOnDevice), str(data.getTypeID()))
			
			ad = ActuatorData(typeID = ConfigConst.TILT_ALERT_ACTUATOR_TYPE)
			ad.setLocationID(data.getLocationID())
			
			currentTilt = data.getValue()
			
			if currentTilt > self.triggerTiltMaxAngle:
				# Tilt exceeds threshold - activate alert
				if not self.tiltAlertActive:
					logging.warning("TILT THRESHOLD EXCEEDED: %.1f° > %.1f° - Activating alert!", 
						currentTilt, self.triggerTiltMaxAngle)
					ad.setCommand(ConfigConst.COMMAND_ON)
					ad.setValue(currentTilt)
					self.tiltAlertActive = True
					self.handleActuatorCommandMessage(ad)
			else:
				# Tilt within safe range - deactivate alert if active
				if self.tiltAlertActive:
					logging.info("Tilt returned to safe range: %.1f° <= %.1f° - Deactivating alert.", 
						currentTilt, self.triggerTiltMaxAngle)
					ad.setCommand(ConfigConst.COMMAND_OFF)
					ad.setValue(currentTilt)
					self.tiltAlertActive = False
					self.handleActuatorCommandMessage(ad)
	
	def _handleUpstreamTransmission(self, resourceName: ResourceNameEnum, msg: str):
		"""
		Sends sensor and system performance data upstream to GDA via MQTT.
		
		PIOT-CDA-10-004: Upstream Transmission
		"""
		if not resourceName or not msg:
			logging.warning('Invalid resource or message. Cannot send upstream transmission.')
			return
		
		logging.info('Upstream transmission invoked. Checking communications integration.')
		
		# Use MQTT client to publish the message
		if self.mqttClient:
			try:
				if self.mqttClient.publishMessage(resource=resourceName, msg=msg, qos=1):
					logging.info('Published incoming data to resource (MQTT): %s', str(resourceName))
				else:
					logging.warning('Failed to publish incoming data to resource (MQTT): %s', str(resourceName))
			except Exception as e:
				logging.error('Exception while publishing upstream transmission: %s', str(e))
		else:
			logging.warning('MQTT client not available. Cannot send upstream transmission.')
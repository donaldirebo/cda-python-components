#####
# 
# Full integration test for Lab Module 10 CDA
# Tests complete actuator command flow including MQTT publishing
# 
import logging
import unittest
from time import sleep
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.app.DeviceDataManager import DeviceDataManager
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

class DeviceDataManagerFullIntegrationTest(unittest.TestCase):
	"""
	Full integration test for DeviceDataManager with complete MQTT flow.
	This test traces the entire message publishing cycle including JSON encoding.
	"""
	
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Testing DeviceDataManager full integration flow with MQTT publishing...")
		
	def setUp(self):
		pass
		
	def tearDown(self):
		pass
	
	def testFullActuatorCommandFlow(self):
		"""
		Test complete actuator command flow:
		1. Create DeviceDataManager with communications enabled
		2. Create MQTT subscriber to listen for responses
		3. Send actuator command through MQTT
		4. Wait for response with JSON encoding logs
		"""
		logging.info("=== Starting Full Integration Test ===")
		
		# Create DeviceDataManager with full communications
		ddMgr = DeviceDataManager()
		
		# Create separate MQTT client to subscribe to responses
		responseMqttClient = MqttClientConnector(clientID='TestResponseListener')
		responseMqttClient.setDataMessageListener(self)
		
		# Connect subscriber
		logging.info("Connecting response listener...")
		responseMqttClient.connectClient()
		sleep(2)
		
		# Subscribe to actuator response topic
		logging.info("Subscribing to actuator response topic...")
		responseMqttClient.subscribeToTopic(
			resource=ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE, 
			qos=1
		)
		sleep(2)
		
		# Create actuator command
		logging.info("Creating actuator command...")
		actuatorData = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
		actuatorData.setCommand(ConfigConst.COMMAND_ON)
		actuatorData.setStateData("This is a full integration test.")
		actuatorData.setValue(75.0)
		
		# Process the command through DeviceDataManager
		logging.info("Sending actuator command through DeviceDataManager...")
		ddMgr.handleActuatorCommandMessage(actuatorData)
		
		# Wait for MQTT publishing and response
		logging.info("Waiting for response message...")
		sleep(5)
		
		# Disconnect
		logging.info("Disconnecting MQTT clients...")
		responseMqttClient.disconnectClient()
		
		logging.info("=== Full Integration Test Complete ===")
		
	def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
		"""
		Callback for incoming messages.
		"""
		logging.info("Response message received on topic: " + resourceEnum.value)
		logging.info("Response payload: " + msg)
		return True
	
	def handleActuatorCommandMessage(self, data: ActuatorData) -> ActuatorData:
		"""Not used in this test."""
		return data
	
	def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
		"""Not used in this test."""
		return True
	
	def handleSensorMessage(self, data) -> bool:
		"""Not used in this test."""
		return True
	
	def handleSystemPerformanceMessage(self, data) -> bool:
		"""Not used in this test."""
		return True
	
	def getLatestActuatorDataResponseFromCache(self, name: str = None):
		"""Not used in this test."""
		return None
	
	def getLatestSensorDataFromCache(self, name: str = None):
		"""Not used in this test."""
		return None
	
	def getLatestSystemPerformanceDataFromCache(self, name: str = None):
		"""Not used in this test."""
		return None
	
	def setSystemPerformanceDataListener(self, listener=None):
		"""Not used in this test."""
		pass
	
	def setTelemetryDataListener(self, name: str = None, listener=None):
		"""Not used in this test."""
		pass

if __name__ == "__main__":
	unittest.main()

#####
# 
# Test for PIOT-CDA-10-003: Actuator Command Message Subscription
# 
import logging
import unittest
from time import sleep
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.DataUtil import DataUtil

class MqttActuatorSubscribeTest(unittest.TestCase):
	"""
	Test MqttClientConnector's ability to subscribe to and handle
	incoming ActuatorData command messages.
	"""
	
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Testing PIOT-CDA-10-003: Actuator Command Subscription...")
		
	def setUp(self):
		pass
		
	def tearDown(self):
		pass
	
	def testActuatorCmdPubSub(self):
		"""
		Test publishing an actuator command and subscribing to receive it.
		"""
		qos = 1
		delay = 60  # Keep alive delay
		
		# Create actuator data payload
		actuatorData = ActuatorData()
		payload = DataUtil().actuatorDataToJson(actuatorData)
		
		# Create MQTT client with listener
		mqttClient = MqttClientConnector(clientID='CDAMqttActuatorTest001')
		mqttClient.setDataMessageListener(DefaultDataMessageListener())
		
		# Connect to broker
		logging.info("Connecting to MQTT broker...")
		mqttClient.connectClient()
		sleep(5)
		
		# Publish actuator command
		logging.info("Publishing actuator command...")
		mqttClient.publishMessage(
			resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, 
			msg=payload, 
			qos=qos
		)
		sleep(5)
		
		# Wait for subscription callback to process
		sleep(delay)
		
		# Disconnect
		logging.info("Disconnecting from MQTT broker...")
		mqttClient.disconnectClient()
		
		logging.info("Test complete!")
		
if __name__ == "__main__":
	unittest.main()

#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 - 2025 by Andrew D. King
# 
import logging
import unittest
from time import sleep
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.app.DeviceDataManager import DeviceDataManager
from programmingtheiot.data.ActuatorData import ActuatorData

class DeviceDataManagerCallbackTest(unittest.TestCase):
	"""
	This test case class tests DeviceDataManager's ability to handle
	incoming actuator command messages from the GDA.
	"""
	
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Testing DeviceDataManager actuator callback...")
		
	def setUp(self):
		pass
		
	def tearDown(self):
		pass
	
	def testActuatorDataCallback(self):
		"""Test handling of incoming actuator command messages."""
		ddMgr = DeviceDataManager()
		
		actuatorData = ActuatorData(typeID = ConfigConst.HVAC_ACTUATOR_TYPE)
		actuatorData.setCommand(ConfigConst.COMMAND_ON)
		actuatorData.setStateData("This is a test.")
		
		ddMgr.handleActuatorCommandMessage(actuatorData)
		
		sleep(10)
		
if __name__ == "__main__":
	unittest.main()

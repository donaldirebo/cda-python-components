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

class DeviceDataManagerIntegrationTest(unittest.TestCase):
	"""
	This test case class contains very basic integration tests for
	DeviceDataManager. It should not be considered complete,
	but serve as a starting point for the student implementing
	additional functionality within their Programming the IoT
	environment.
	
	NOTE: This test MAY require the sense_emu_gui to be running,
	depending on whether or not the 'enableEmulator' flag is
	True within the ConstraineDevice section of PiotConfig.props.
	If so, it must have access to the underlying libraries that
	support the pisense module. On Windows, one way to do
	this is by installing pisense and sense-emu within the
	Bash on Ubuntu on Windows environment and then execute this
	test case from the command line, as it will likely fail
	if run within an IDE in native Windows.
	
	PIOT-CDA-10-004: This test now validates upstream transmission of
	sensor data and system performance data to the GDA via MQTT.
	"""
	
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("="*70)
		logging.info("Testing DeviceDataManager class...")
		logging.info("PIOT-CDA-10-004: Upstream Transmission Integration Test")
		logging.info("="*70)
		
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testDeviceDataMgrTimedIntegration(self):
		"""
		PIOT-CDA-10-004: Upstream Transmission Integration Test
		
		This test validates that DeviceDataManager properly sends sensor data
		and system performance data to the GDA via MQTT.
		
		Expected behavior:
		- Sensor data published every poll cycle (~5 seconds)
		- System performance data published every poll cycle
		- Temperature threshold violations trigger actuator commands
		- All messages logged with "Published incoming data to resource (MQTT)"
		"""
		logging.info("-"*70)
		logging.info("Test: testDeviceDataMgrTimedIntegration()")
		logging.info("-"*70)
		
		logging.info("Creating DeviceDataManager instance...")
		ddMgr = DeviceDataManager()
		
		logging.info("Starting DeviceDataManager...")
		ddMgr.startManager()
		
		logging.info("-"*70)
		logging.info("Running integration test for 60 seconds")
		logging.info("Watch console for:")
		logging.info("  - Sensor data being published to MQTT")
		logging.info("  - System performance data being published to MQTT")
		logging.info("  - Optional: Adjust SenseHAT emulator temp to cross thresholds")
		logging.info("-"*70)
		
		sleep(60)
		
		logging.info("-"*70)
		logging.info("Stopping DeviceDataManager...")
		ddMgr.stopManager()
		logging.info("Integration test complete!")
		logging.info("-"*70)
		
if __name__ == "__main__":
	unittest.main()
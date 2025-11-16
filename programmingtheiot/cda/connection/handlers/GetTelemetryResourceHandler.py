import logging

from coapthon import defines
from coapthon.resources.resource import Resource

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData


class GetTelemetryResourceHandler(Resource, ITelemetryDataListener):
	"""
	Observable CoAP resource that provides sensor/telemetry data.
	Supports GET requests and automatic updates via observation.
	"""

	def __init__(self, name: str = ConfigConst.SENSOR_MSG, coap_server=None, dataMsgListener: IDataMessageListener = None):
		super(GetTelemetryResourceHandler, self).__init__(
			name, coap_server, visible=True, observable=True, allow_children=True)

		self.pollCycles = ConfigUtil().getInteger(
			section=ConfigConst.CONSTRAINED_DEVICE,
			key=ConfigConst.POLL_CYCLES_KEY,
			defaultVal=ConfigConst.DEFAULT_POLL_CYCLES)

		self.dataUtil = DataUtil()
		self.sensorData = SensorData()

		self.dataMsgListener = dataMsgListener

		# Register this handler as a listener for telemetry updates
		if self.dataMsgListener:
			self.dataMsgListener.setTelemetryDataListener(self)

		logging.info("GetTelemetryResourceHandler initialized")

	def render_GET_advanced(self, request, response):
		"""
		Handle GET requests for sensor/telemetry data.
		Returns the latest sensor data as JSON.
		"""
		if request:
			response.code = defines.Codes.CONTENT.number

			if not self.sensorData:
				response.code = defines.Codes.EMPTY.number
				self.sensorData = SensorData()

			jsonData = self.dataUtil.sensorDataToJson(self.sensorData)

			logging.info("Latest SensorData JSON: " + jsonData)

			response.payload = (defines.Content_types["application/json"], jsonData)
			response.max_age = self.pollCycles

			# Mark resource as unchanged (will be updated via onSensorDataUpdate)
			self.changed = False

		return self, response

	def render_PUT_advanced(self, request, response):
		"""
		Handle PUT requests for sensor/telemetry data.
		For now, just log and return success.
		"""
		logging.info("PUT request received for SensorData")
		if request.payload:
			logging.debug(f"PUT payload: {request.payload}")
		response.code = defines.Codes.CHANGED.number
		return self, response

	def render_POST_advanced(self, request, response):
		"""
		Handle POST requests for sensor/telemetry data.
		For now, just log and return success.
		"""
		logging.info("POST request received for SensorData")
		if request.payload:
			logging.debug(f"POST payload: {request.payload}")
		response.code = defines.Codes.CREATED.number
		return self, response

	def render_DELETE(self, request):
		"""
		Handle DELETE requests for sensor/telemetry data.
		For now, just log and return success.
		"""
		logging.info("DELETE request received for SensorData")
		return True

	def onSensorDataUpdate(self, data: SensorData) -> bool:
		"""
		Callback invoked when sensor data is updated.
		Stores the data and marks the resource as changed for observers.
		"""
		if data:
			self.sensorData = data
			self.changed = True
			logging.debug("SensorData updated in resource handler")
			return True
		return False
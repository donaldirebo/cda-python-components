import logging

from coapthon import defines
from coapthon.resources.resource import Resource

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class GetSystemPerformanceResourceHandler(Resource, ISystemPerformanceDataListener):
	"""
	Observable CoAP resource that provides system performance data.
	Supports GET requests and automatic updates via observation.
	"""

	def __init__(self, name: str = ConfigConst.SYSTEM_PERF_MSG, coap_server=None, dataMsgListener: IDataMessageListener = None):
		super(GetSystemPerformanceResourceHandler, self).__init__(
			name, coap_server, visible=True, observable=True, allow_children=True)

		self.pollCycles = ConfigUtil().getInteger(
			section=ConfigConst.CONSTRAINED_DEVICE,
			key=ConfigConst.POLL_CYCLES_KEY,
			defaultVal=ConfigConst.DEFAULT_POLL_CYCLES)

		self.dataUtil = DataUtil()
		self.sysPerfData = SystemPerformanceData()

		self.dataMsgListener = dataMsgListener

		# Register this handler as a listener for system performance updates
		if self.dataMsgListener:
			self.dataMsgListener.setSystemPerformanceDataListener(self)

		logging.info("GetSystemPerformanceResourceHandler initialized")

	def render_GET_advanced(self, request, response):
		"""
		Handle GET requests for system performance data.
		Returns the latest system performance data as JSON.
		"""
		if request:
			response.code = defines.Codes.CONTENT.number

			if not self.sysPerfData:
				response.code = defines.Codes.EMPTY.number
				self.sysPerfData = SystemPerformanceData()

			jsonData = self.dataUtil.systemPerformanceDataToJson(self.sysPerfData)

			logging.info("Latest SystemPerformanceData JSON: " + jsonData)

			response.payload = (defines.Content_types["application/json"], jsonData)
			response.max_age = self.pollCycles

			# Mark resource as unchanged (will be updated via onSystemPerformanceDataUpdate)
			self.changed = False

		return self, response

	def render_PUT_advanced(self, request, response):
		"""
		Handle PUT requests for system performance data.
		For now, just log and return success.
		"""
		logging.info("PUT request received for SystemPerformanceData")
		if request.payload:
			logging.debug(f"PUT payload: {request.payload}")
		response.code = defines.Codes.CHANGED.number
		return self, response

	def render_POST_advanced(self, request, response):
		"""
		Handle POST requests for system performance data.
		For now, just log and return success.
		"""
		logging.info("POST request received for SystemPerformanceData")
		if request.payload:
			logging.debug(f"POST payload: {request.payload}")
		response.code = defines.Codes.CREATED.number
		return self, response

	def render_DELETE(self, request):
		"""
		Handle DELETE requests for system performance data.
		For now, just log and return success.
		"""
		logging.info("DELETE request received for SystemPerformanceData")
		return True

	def onSystemPerformanceDataUpdate(self, data: SystemPerformanceData) -> bool:
		"""
		Callback invoked when system performance data is updated.
		Stores the data and marks the resource as changed for observers.
		"""
		if data:
			self.sysPerfData = data
			self.changed = True
			logging.debug("SystemPerformanceData updated in resource handler")
			return True
		return False
import logging

from coapthon import defines
from coapthon.resources.resource import Resource

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData


class UpdateActuatorResourceHandler(Resource):
	"""
	CoAP resource that handles actuator command updates via PUT requests.
	Receives ActuatorData from GDA and forwards to the CDA for execution.
	"""

	def __init__(self, name: str = ConfigConst.ACTUATOR_CMD, coap_server=None, dataMsgListener: IDataMessageListener = None):
		super(UpdateActuatorResourceHandler, self).__init__(
			name, coap_server, visible=True, observable=True, allow_children=True)

		self.pollCycles = ConfigUtil().getInteger(
			section=ConfigConst.CONSTRAINED_DEVICE,
			key=ConfigConst.POLL_CYCLES_KEY,
			defaultVal=ConfigConst.DEFAULT_POLL_CYCLES)

		self.dataUtil = DataUtil()
		self.dataMsgListener = dataMsgListener

		logging.info("UpdateActuatorResourceHandler initialized")

	def render_GET_advanced(self, request, response):
		"""
		Handle GET requests for actuator commands.
		For now, just log and return success.
		"""
		logging.info("GET request received for ActuatorCmd")
		response.code = defines.Codes.CONTENT.number
		response.payload = (defines.Content_types["application/json"], "")
		return self, response

	def render_PUT_advanced(self, request, response):
		"""
		Handle PUT requests for actuator commands.
		Parses JSON payload, processes the command, and returns response.
		"""
		if request:
			logging.info("PUT request received for ActuatorCmd")

			try:
				# Get the request payload
				requestPayload = request.payload

				if requestPayload:
					logging.debug(f"PUT payload received: {requestPayload}")

					# Convert JSON payload to ActuatorData
					actuatorCmdData = self.dataUtil.jsonToActuatorData(requestPayload)

					# Process the actuator command through the data message listener
					if self.dataMsgListener:
						response_payload = self._createResponse(
							response=response,
							data=actuatorCmdData
						)
						response.payload = response_payload
					else:
						logging.warning("Data message listener not set")
						response.code = defines.Codes.INTERNAL_SERVER_ERROR.number

				else:
					logging.warning("PUT request received with empty payload")
					response.code = defines.Codes.BAD_REQUEST.number

				response.max_age = self.pollCycles

			except Exception as e:
				logging.error(f"Error processing PUT request: {e}")
				response.code = defines.Codes.PRECONDITION_FAILED.number

		else:
			response.code = defines.Codes.BAD_REQUEST.number

		return self, response

	def render_POST_advanced(self, request, response):
		"""
		Handle POST requests for actuator commands.
		For now, just log and return success.
		"""
		logging.info("POST request received for ActuatorCmd")
		if request.payload:
			logging.debug(f"POST payload: {request.payload}")
		response.code = defines.Codes.CREATED.number
		return self, response

	def render_DELETE(self, request):
		"""
		Handle DELETE requests for actuator commands.
		For now, just log and return success.
		"""
		logging.info("DELETE request received for ActuatorCmd")
		return True

	def _createResponse(self, response=None, data: ActuatorData = None) -> tuple:
		"""
		Process actuator command and create response payload.
		
		Args:
			response: CoAP response object
			data: ActuatorData to process
			
		Returns:
			Tuple of (content_type, json_data)
		"""
		try:
			# Forward the actuator command to the message listener
			actuatorResponseData = self.dataMsgListener.handleActuatorCommandMessage(data)

			if not actuatorResponseData:
				# If no response, create error response
				actuatorResponseData = ActuatorData()
				actuatorResponseData.updateData(data)
				actuatorResponseData.setAsResponse()
				actuatorResponseData.setStatusCode(-1)

				response.code = defines.Codes.PRECONDITION_FAILED.number
				logging.warning("Actuator command processing failed")
			else:
				response.code = defines.Codes.CHANGED.number
				logging.info("Actuator command processed successfully")

			# Convert response data to JSON
			jsonData = self.dataUtil.actuatorDataToJson(actuatorResponseData)
			logging.debug(f"Actuator response JSON: {jsonData}")

			return (defines.Content_types["application/json"], jsonData)

		except Exception as e:
			logging.error(f"Error creating response: {e}")
			response.code = defines.Codes.INTERNAL_SERVER_ERROR.number
			
			# Return empty JSON response on error
			return (defines.Content_types["application/json"], "")
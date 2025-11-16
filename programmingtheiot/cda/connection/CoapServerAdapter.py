import logging
import traceback

from threading import Thread
from time import sleep

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.handlers.GetTelemetryResourceHandler import GetTelemetryResourceHandler
from programmingtheiot.cda.connection.handlers.UpdateActuatorResourceHandler import UpdateActuatorResourceHandler
from programmingtheiot.cda.connection.handlers.GetSystemPerformanceResourceHandler import GetSystemPerformanceResourceHandler

from coapthon.resources.resource import Resource


class CoapServerAdapter():
	"""
	Definition for a CoAP communications server, with embedded test functions.
	"""

	def __init__(self, dataMsgListener: IDataMessageListener = None):
		"""
		Constructor for CoapServerAdapter.
		
		Args:
			dataMsgListener: Optional IDataMessageListener for processing callbacks
		"""
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		
		# Get CoAP server configuration from PiotConfig.props
		self.host = self.config.getProperty(
			ConfigConst.COAP_GATEWAY_SERVICE, 
			ConfigConst.HOST_KEY, 
			ConfigConst.DEFAULT_HOST
		)
		self.port = self.config.getInteger(
			ConfigConst.COAP_GATEWAY_SERVICE, 
			ConfigConst.PORT_KEY, 
			ConfigConst.DEFAULT_COAP_PORT
		)
		self.serverUri = f"coap://{self.host}:{self.port}"
		
		# Initialize server components
		self.coapServer = None
		self.coapServerTask = None
		
		self.listenTimeout = 30
		
		# Initialize the server
		self._initServer()
		
		logging.info(f"CoAP server configured for host and port: {self.serverUri}")

	def _initServer(self):
		"""
		Initialize the CoAP server instance and register resource handlers.
		"""
		try:
			self.coapServer = CoAP((self.host, self.port))
			logging.info("CoAP server instance created successfully")
			
			# Register resource handlers
			self._registerResourceHandlers()
			
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			logging.error(f"Failed to initialize CoAP server: {e}")
	
	def _registerResourceHandlers(self):
		"""
		Register all resource handlers with the CoAP server.
		"""
		try:
			# System performance resource path
			sysPerfResourcePath = ConfigConst.CDA_SYSTEM_PERF_MSG_RESOURCE
			
			# Create and add system performance resource handler
			sysPerfHandler = GetSystemPerformanceResourceHandler(
				name=ConfigConst.SYSTEM_PERF_MSG,
				coap_server=self.coapServer,
				dataMsgListener=self.dataMsgListener
			)
			self.coapServer.add_resource(sysPerfResourcePath, sysPerfHandler)
			logging.info(f"Registered resource: {sysPerfResourcePath}")
			
			# Telemetry (sensor) resource path
			telemetryResourcePath = ConfigConst.CDA_SENSOR_DATA_MSG_RESOURCE
			
			# Create and add telemetry (sensor) resource handler
			telemetryHandler = GetTelemetryResourceHandler(
				name=ConfigConst.SENSOR_MSG,
				coap_server=self.coapServer,
				dataMsgListener=self.dataMsgListener
			)
			self.coapServer.add_resource(telemetryResourcePath, telemetryHandler)
			logging.info(f"Registered resource: {telemetryResourcePath}")
			
			# Actuator command resource path
			actuatorResourcePath = ConfigConst.CDA_ACTUATOR_CMD_MSG_RESOURCE
			
			# Create and add actuator command resource handler
			actuatorHandler = UpdateActuatorResourceHandler(
				name=ConfigConst.ACTUATOR_CMD,
				coap_server=self.coapServer,
				dataMsgListener=self.dataMsgListener
			)
			self.coapServer.add_resource(actuatorResourcePath, actuatorHandler)
			logging.info(f"Registered resource: {actuatorResourcePath}")
			
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			logging.error(f"Failed to register resource handlers: {e}")

	def _runServer(self):
		"""
		Run the CoAP server in a separate thread.
		This method blocks while listening for incoming requests.
		"""
		try:
			self.coapServer.listen(self.listenTimeout)
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			logging.warning("Failed to run CoAP server")

	def addResource(self, resourcePath: ResourceNameEnum = None, endName: str = None, resource = None):
		"""
		Add a resource handler to the CoAP server with proper URI path handling.
		
		Args:
			resourcePath: ResourceNameEnum identifying the resource path
			endName: Optional end name for the resource (e.g., specific actuator name)
			resource: The resource handler instance to add
		
		Returns:
			True if resource was added successfully, False otherwise
		"""
		if not resourcePath or not resource:
			logging.warning(f"No resource provided for path: {resourcePath}")
			return False
		
		try:
			# Get the URI path from the ResourceNameEnum
			uriPath = resourcePath.value
			
			# Append end name if provided
			if endName:
				uriPath = uriPath + '/' + endName
				resource.name = endName
			
			# Trim leading/trailing slashes and split into components
			trimmedUriPath = uriPath.strip("/")
			resourceList = trimmedUriPath.split("/")
			resourceTree = None
			registrationPath = ""
			generationCount = 0
			
			# Build the resource tree path, checking if resources exist
			for resourceName in resourceList:
				generationCount += 1
				registrationPath = registrationPath + "/" + resourceName
				
				try:
					resourceTree = self.coapServer.root[registrationPath]
				except KeyError:
					resourceTree = None
			
			# Register the resource if path doesn't already exist
			if not resourceTree:
				if len(resourceList) != generationCount:
					logging.warning(f"Failed to build complete resource path: {registrationPath}")
					return False
				
				resource.path = registrationPath
				self.coapServer.root[registrationPath] = resource
				logging.info(f"Registered resource: {registrationPath}")
				return True
			else:
				logging.warning(f"Resource already exists at path: {registrationPath}")
				return False
				
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			logging.error(f"Error adding resource: {e}")
			return False

	def startServer(self):
		"""
		Start the CoAP server in a separate daemon thread.
		"""
		if self.coapServer:
			logging.info("Starting CoAP server...")
			
			# Stop existing server task if running
			if self.coapServerTask and self.coapServerTask.is_alive():
				self.stopServer()
				self.coapServerTask = None
			
			# Start new server task
			self.coapServerTask = Thread(target=self._runServer)
			self.coapServerTask.setDaemon(True)
			self.coapServerTask.start()
			
			logging.info("\n\n***** CoAP server started. *****\n\n")
		else:
			logging.warning("CoAP server not yet initialized (shouldn't happen)")

	def stopServer(self):
		"""
		Stop the CoAP server and clean up resources.
		"""
		if self.coapServer:
			logging.info("Stopping CoAP server...")
			
			try:
				self.coapServer.close()
				self.coapServerTask.join(5)
				logging.info("CoAP server stopped")
			except Exception as e:
				traceback.print_exception(type(e), e, e.__traceback__)
				logging.warning(f"Error stopping CoAP server: {e}")
		else:
			logging.warning("CoAP server not yet initialized (shouldn't happen)")

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		"""
		Set the data message listener for processing callbacks.
		
		Args:
			listener: IDataMessageListener instance
			
		Returns:
			True if listener was set successfully, False otherwise
		"""
		if listener:
			self.dataMsgListener = listener
			return True
		
		return False
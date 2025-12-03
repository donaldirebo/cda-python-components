"""
MqttClientConnector for CDA (Constrained Device Application)
Lab Module 06 - MQTT Client Implementation
"""

import logging
import paho.mqtt.client as mqttClient

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient


class MqttClientConnector(IPubSubClient):
    """
    MQTT Client Connector for publishing and subscribing to MQTT topics.
    Implements the IPubSubClient interface.
    """
    
    def __init__(self, clientID: str = None):
        """
        Initialize the MQTT Client Connector.
        
        Args:
            clientID: Optional custom client ID. If not provided, will use
                      device location ID from config or default value.
        """
        super().__init__()
        
        self.config = ConfigUtil()
        self.dataMsgListener = None
        
        # Load MQTT configuration from properties file
        self.host = \
            self.config.getProperty( \
                ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
        
        self.port = \
            self.config.getInteger( \
                ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_MQTT_PORT)
        
        self.keepAlive = \
            self.config.getInteger( \
                ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.KEEP_ALIVE_KEY, ConfigConst.DEFAULT_KEEP_ALIVE)
        
        self.defaultQos = \
            self.config.getInteger( \
                ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.DEFAULT_QOS_KEY, ConfigConst.DEFAULT_QOS)
        
        self.mqttClient = None
        
        # Set client ID - priority: parameter > config file > default
        if clientID:
            # If clientID provided as parameter, use it directly
            self.clientID = clientID
        else:
            # Otherwise, read from config file with default fallback
            defaultClientID = 'CDAMqttClientID001'
            self.clientID = \
                self.config.getProperty( \
                    ConfigConst.CONSTRAINED_DEVICE, ConfigConst.DEVICE_LOCATION_ID_KEY, defaultClientID)
        
        logging.info('\tMQTT Client ID:   ' + self.clientID)
        logging.info('\tMQTT Broker Host: ' + self.host)
        logging.info('\tMQTT Broker Port: ' + str(self.port))
        logging.info('\tMQTT Keep Alive:  ' + str(self.keepAlive))
    
    
    # ============================================
    # IPubSubClient Implementation
    # ============================================
    
    def connectClient(self) -> bool:
        """
        Connect to the MQTT broker.
        
        Returns:
            bool: True if connection initiated, False if already connected.
        """
        if not self.mqttClient:
            # Create MQTT client instance with clean session enabled
            self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=True)
            
            # Register callback handlers
            self.mqttClient.on_connect = self.onConnect
            self.mqttClient.on_disconnect = self.onDisconnect
            self.mqttClient.on_message = self.onMessage
            self.mqttClient.on_publish = self.onPublish
            self.mqttClient.on_subscribe = self.onSubscribe
        
        if not self.mqttClient.is_connected():
            logging.info('MQTT client connecting to broker at host: ' + self.host)
            
            self.mqttClient.connect(self.host, self.port, self.keepAlive)
            self.mqttClient.loop_start()
            return True
        else:
            logging.warning('MQTT client is already connected. Ignoring connect request.')
            return False
    
    
    def disconnectClient(self) -> bool:
        """
        Disconnect from the MQTT broker.
        
        Returns:
            bool: True if disconnection initiated, False if already disconnected.
        """
        if self.mqttClient and self.mqttClient.is_connected():
            try:
                self.mqttClient.loop_stop()
                self.mqttClient.disconnect()
                return True
            except Exception as e:
                logging.error('Failed to disconnect MQTT client: ' + str(e))
                return False
        else:
            logging.warning('MQTT client already disconnected or not initialized. Ignoring.')
            return False
    
    
    def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
        """
        Publish a message to an MQTT topic.
        
        Args:
            resource: ResourceNameEnum representing the MQTT topic.
            msg: The message payload (typically JSON string).
            qos: Quality of Service level (0, 1, or 2). Defaults to ConfigConst.DEFAULT_QOS.
        
        Returns:
            bool: True if message published, False otherwise.
        """
        # Check validity of resource (topic)
        if not resource:
            logging.warning('No topic specified. Cannot publish message.')
            return False
        
        # Check validity of message
        if not msg:
            logging.warning('No message specified. Cannot publish message to topic: ' + resource.value)
            return False
        
        # Check validity of QoS - set to default if necessary
        if qos < 0 or qos > 2:
            qos = ConfigConst.DEFAULT_QOS
        
        # Publish message and wait for completion
        msgInfo = self.mqttClient.publish(topic=resource.value, payload=msg, qos=qos)
        msgInfo.wait_for_publish()
        
        return True
    
    
    def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
        """
        Subscribe to an MQTT topic.
        
        Args:
            resource: ResourceNameEnum representing the MQTT topic to subscribe to.
            callback: Optional callback function for handling messages (not currently used).
            qos: Quality of Service level (0, 1, or 2). Defaults to ConfigConst.DEFAULT_QOS.
        
        Returns:
            bool: True if subscription initiated, False otherwise.
        """
        # Check validity of resource (topic)
        if not resource:
            logging.warning('No topic specified. Cannot subscribe.')
            return False
        
        # Check validity of QoS - set to default if necessary
        if qos < 0 or qos > 2:
            qos = ConfigConst.DEFAULT_QOS
        
        # Subscribe to topic
        logging.info('Subscribing to topic %s', resource.value)
        self.mqttClient.subscribe(resource.value, qos)
        
        return True
    
    
    def unsubscribeFromTopic(self, resource: ResourceNameEnum = None) -> bool:
        """
        Unsubscribe from an MQTT topic.
        
        Args:
            resource: ResourceNameEnum representing the MQTT topic to unsubscribe from.
        
        Returns:
            bool: True if unsubscription initiated, False otherwise.
        """
        # Check validity of resource (topic)
        if not resource:
            logging.warning('No topic specified. Cannot unsubscribe.')
            return False
        
        logging.info('Unsubscribing to topic %s', resource.value)
        self.mqttClient.unsubscribe(resource.value)
        
        return True
    
    
    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        """
        Set the data message listener for handling incoming messages.
        
        Args:
            listener: IDataMessageListener implementation to handle messages.
        
        Returns:
            bool: True if listener set, False if listener is None.
        """
        if listener:
            self.dataMsgListener = listener
            return True
        else:
            logging.warning('Listener is None. Not setting data message listener.')
            return False
    
    
    # ============================================
    # MQTT Callback Handlers (Public)
    # ============================================
    
    def onConnect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker.
        """
        logging.info('MQTT client connected to broker: ' + str(client))
    
    
    def onDisconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.
        """
        logging.info('MQTT client disconnected from broker: ' + str(client))
    
    
    def onMessage(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.
        """
        payload = msg.payload
        
        if payload:
            logging.info('MQTT message received with payload: ' + str(payload.decode("utf-8")))
        else:
            logging.info('MQTT message received with no payload: ' + str(msg))
        
        # Forward message to data message listener if set
        if self.dataMsgListener:
            try:
                self.dataMsgListener.handleIncomingMessage(msg.topic, payload.decode('utf-8'))
            except Exception as e:
                logging.error('Error handling message in listener: ' + str(e))
    
    
    def onPublish(self, client, userdata, mid):
        """
        Callback for when a message is published.
        """
        logging.info('MQTT message published: ' + str(client))
    
    
    def onSubscribe(self, client, userdata, mid, granted_qos):
        """
        Callback for when subscription is acknowledged by the broker.
        """
        logging.info('MQTT client subscribed: ' + str(client))
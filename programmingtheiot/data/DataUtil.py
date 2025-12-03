import json
import logging
from decimal import Decimal
from json import JSONEncoder

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class DataUtil():
    """
    Utility for converting IoT data objects to/from JSON.
    """
    
    def __init__(self, encodeToUtf8=False):
        self.encodeToUtf8 = encodeToUtf8
        logging.info("Created DataUtil instance.")
    
    def actuatorDataToJson(self, data: ActuatorData = None, useDecForFloat: bool = False):
        if not data:
            logging.debug("ActuatorData is null. Returning empty string.")
            return ""
        logging.info("Encoding ActuatorData to JSON [pre] --> " + str(data))
        jsonData = self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)
        logging.info("Encoding ActuatorData to JSON [post] --> " + str(jsonData))
        return jsonData
    
    def sensorDataToJson(self, data: SensorData = None, useDecForFloat: bool = False):
        if not data:
            logging.debug("SensorData is null. Returning empty string.")
            return ""
        return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)
    
    def systemPerformanceDataToJson(self, data: SystemPerformanceData = None, useDecForFloat: bool = False):
        if not data:
            logging.debug("SystemPerformanceData is null. Returning empty string.")
            return ""
        return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)
    
    def jsonToActuatorData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning null.")
            return None
        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
        ad = ActuatorData()
        self._updateIotData(jsonStruct, ad)
        return ad
    
    def jsonToSensorData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning null.")
            return None
        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
        sd = SensorData()
        self._updateIotData(jsonStruct, sd)
        return sd
    
    def jsonToSystemPerformanceData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning null.")
            return None
        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
        spd = SystemPerformanceData()
        self._updateIotData(jsonStruct, spd)
        return spd
    
    def _formatDataAndLoadDictionary(self, jsonData: str, useDecForFloat: bool = False) -> dict:
        jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')
        if useDecForFloat:
            return json.loads(jsonData, parse_float=Decimal)
        else:
            return json.loads(jsonData)
    
    def _generateJsonData(self, obj, useDecForFloat: bool = False) -> str:
        if self.encodeToUtf8:
            jsonData = json.dumps(obj, cls=JsonDataEncoder).encode('utf8')
        else:
            jsonData = json.dumps(obj, cls=JsonDataEncoder, indent=4)
        
        if jsonData:
            jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')
        return jsonData
    
    def _updateIotData(self, jsonStruct, obj):
        varStruct = vars(obj)
        for key in jsonStruct:
            if key in varStruct:
                setattr(obj, key, jsonStruct[key])
            else:
                logging.warn("JSON data contains key not mappable to object: %s", key)

class JsonDataEncoder(JSONEncoder):
    """
    JSON encoder for IoT data objects.
    """
    def default(self, o):
        return o.__dict__
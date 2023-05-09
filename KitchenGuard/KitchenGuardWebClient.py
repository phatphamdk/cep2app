from __future__ import annotations
import json
import re
from copy import deepcopy
from dataclasses import dataclass, replace as dataclass_replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Union
from uuid import UUID

#class kgweb:
 #   def send_event():
        
class Events:
    def StoveOnEvent():
        stove_state_state = HeucodEvent()
        stove_state_state.value = True
        stove_state_state.timestamp = datetime.now(tz=timezone.utc)
        stove_state_state.event_type = HeucodEventType.BasicEvent
        print(stove_state_state.to_json())



class HeucodEventType(Enum):
    def __new__(cls, type_: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = type_
        obj.description = description

        return obj

    def __int__(self):
        return self.value

    def __repr__(self) -> str:
        return self.description

    def __str__(self) -> str:
        return self.description

    BasicEvent = (81325, "KitchenGuard.BasicEvent")
    StoveState = (48234, "KithcenGuard.StoveStateEvent")


class HeucodEventJsonEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202
        def to_camel(key):
            # Convert the attribtues names from snake case (Python "default") to camel case.
            return "".join([key.split("_")[0].lower(), *map(str.title, key.split("_")[1:])])

        if isinstance(obj, HeucodEvent):
            result = deepcopy(obj.__dict__)
            keys_append = {}
            keys_remove = set()
            camel_name = {}

            for k, v in result.items():
                # Check if the name must be changed to camel case
                first, *others = k.split("_")

                if first != "id" and len(others) > 0 and v is not None:
                    camel_name[k] = to_camel(k)
                    keys_remove.add(k)

                # Remove value if it is None
                if v is None:
                    keys_remove.add(k)
                # Change the attribute "id_" to "id"
                elif k == "id_":
                    keys_append["id"] = str(v) if not isinstance(v, str) else v
                    keys_remove.add(k)
                elif isinstance(v, UUID):
                    result[k] = str(v)
                elif isinstance(v, datetime):
                    result[k] = int(v.timestamp())
                elif isinstance(v, HeucodEventType):
                    result[k] = str(v)

            for k, v in camel_name.items():
                result[v] = result[k]
            for k in keys_remove:
                result.pop(k)
            for k, v in keys_append.items():
                result[k] = v
        # Attributes to ignore
        elif isinstance(obj, HeucodEventJsonEncoder):
            pass
        else:
            # Base class default() raises TypeError:
            return json.JSONEncoder.default(self, obj)

        return result


@dataclass
class HeucodEvent:
    # --------------------  General event properties --------------------
    # The unique ID of the event. Usually a GUID or UUID but one is free to choose.
    id_: Union[UUID, str] = None
    # The type of the event. This should preferably match the name of the "class" of the device
    # following the HEUCOD ontology in enumeration HeucodEventType.
    event_type: str = None
    # The type of the event as an integer. This should prefaribly match the name of the "class" of
    # the device following the HEUCOD ontology in enumeration HeucodEventType.
    event_type_enum: int = None
    # This field supports adding a prose description of the event - which can e.g. by used for
    # audit and logging purposes.
    description: str = None
    # This field can contain advanced or composite values which are well-known to the specialized
    # vendors.
    advanced: str = None
    # The timestamp of the event being created in the UNIX Epoch time format.
    timestamp: int = None
    # -------------------- Sensor details --------------------
    # All sensors should have a unique ID which they continue to use to identify themselves.
    sensor_id: str = None
    # The type of sensor used.
    sensor_type: str = None
    # The model of the device.
    device_model: str = None
    # The vendor of the device.
    device_vendor: str = None
    # The average power consumption of the device in watts. Use together with the length attribute
    # to calcualte the value in kWh (kilowatt/hour).
    power: int = None
    # The battery level in percentage (0-100). A battery alert service may use this information to
    # send alerts at 10% or 20 % battery life - and critical alerts at 0%.
    battery: int = None
    # Link Quality (LQ) is the quality of the real data received in a signal. This is a value from 0
    # to 255, being 255 the best quality. Typically expect from 0 (bad) to 50-90 (good). It is
    # related to RSSI and SNR values as a quality indicator.
    link_quality: float = None

    value: Any = None
    # -------------------- Python class specific attributes --------------------
    json_encoder = HeucodEventJsonEncoder

    @classmethod
    def from_json(cls, event: str) -> HeucodEvent:
        if not event:
            raise ValueError("The string can't be empty or None")

        try:
            json_obj = json.loads(event)
        except json.JSONDecodeError as ex:
            raise ex from None

        instance = cls()

        # Convert the names of the JSON attributes to snake case (from camel case).
        obj_dict = {}
        for k, v in json_obj.items():
            if k != "id":
                key_tokens = re.split("(?=[A-Z])", k)
                obj_dict["_".join([t.lower() for t in key_tokens])] = v
            else:
                # The id_ attribtues is an exception of the naming standard. In Python, id is a
                # reserved word and its use for naming variables/attribtues/... should be avoided.
                # Thus the name id_.
                obj_dict["id_"] = v

        instance = dataclass_replace(instance, **obj_dict)

        return instance

    def to_json(self):
        if not self.json_encoder:
            raise TypeError("A converter was not specified. Use the converter attribute to do so.")

        # The dumps function looks tries to serialize the JSON string based in the JSON encoder that
        # is passed in the second argument. In this case, it will be the class HeucodEventJsonEncoder,
        # that inherits json.JSONEncoder. It has only the default() function this is called by
        # dumps() when serializing the class.
        return json.dumps(self, cls=self.json_encoder)


if __name__ == "__main__":
    # Example for a PIR event that detected a person leaving its bed. The sensor reports occupancy
    # as false, since it doesn't detect movement. Once it detects movement, it reports occupancy = true.
    stove_state_state = HeucodEvent()
    # In this example, yo ucan use the already provided HeucodEventType values to indicate what is
    # the type of the event. Using them can improve integration with other clients/servers since
    # all of them are usign a standard values.
    stove_state_state.timestamp = datetime.now(tz=timezone.utc)
    stove_state_state.value = True
    #stove_state_state.gateway_id = "gateway-0001"
    # Get the event as JSON
    print(stove_state_state.to_json())

   
    #event = HeucodEvent.from_json('{"timestamp": 1648473393, "value": true, "eventType": "OpenCare.EVODAY.EDL.BedOccupancyEvent", "eventTypeEnum": 82043, "patientId": "patient-0001", "deviceModel": "RTCGQ11LM", "deviceVendor": "Aqara", "gatewayId": "gateway-0001", "id": "0001"}')
    #print(event)
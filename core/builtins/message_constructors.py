from copy import deepcopy
from typing import Union

from .assigned_element import *


class MessageChainInstance:
    messages: list[Union[Union[
        AccountElement,
        SensorElement,
        WeatherElement,
        WeatherInfoElement,
        UIElement,
        HeartElement,
        DeepSeekElement,
        DeepSeekAnswerElement], dict
    ]] = None
    serialized: bool = None

    def deserialize(self):
        self.messages = [{"meta": element.Meta.type, "data": element.dump()} for element in self.messages]
        self.serialized = False
        return self.messages

    def serialize(self):
        if self.serialized:
            return self.messages
        msg_chain_lst = []
        for meta, data in enumerate(self.messages):
            match meta:
                case "AccountElement":
                    msg_chain_lst.append(AccountElement(**data))
                case "SensorElement":
                    msg_chain_lst.append(SensorElement(**data))
                case "WeatherElement":
                    msg_chain_lst.append(WeatherElement(**data))
                case "WeatherInfoElement":
                    msg_chain_lst.append(WeatherInfoElement(**data))
                case "UIElement":
                    msg_chain_lst.append(UIElement(**data))
                case "HeartElement":
                    msg_chain_lst.append(HeartElement(**data))
                case "DeepSeekElement":
                    msg_chain_lst.append(DeepSeekElement(**data))
                case "DeepSeekAnswerElement":
                    msg_chain_lst.append(DeepSeekAnswerElement(**data))
                case _:
                    assert False, "Unknown message type: {meta}"

    @classmethod
    def assign(cls,
               elements: list[Union[
                   AccountElement,
                   SensorElement,
                   WeatherElement,
                   WeatherInfoElement,
                   UIElement,
                   HeartElement,
                   DeepSeekElement,
                   DeepSeekAnswerElement]]) -> "MessageChain":
        cls.serialized = True
        cls.messages = elements
        return deepcopy(cls())

MessageChain = MessageChainInstance.assign

__all__ = ["MessageChain"]
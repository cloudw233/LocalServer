from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from typing import Literal, Union

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(strict=True)


class Account(BaseModel):
    username: str
    password: Union[str, int] = None
    action: Literal["login", "register", "data"]
    face_recognition_data: str = None


class Sensor(Account):
    DHT_T: float = None
    DHT_H: float = None
    power: float = None
    urgent_button: bool = None
    tilt: bool = None
    heart_data: int = None
    smoke: dict = None
    seat: int = None


class Weather(BaseModel):
    city: str


class UI(BaseModel):
    seat: float | int

class Heart(Account):
    bpm: int

class DeepSeek(BaseModel):
    question: str
__all__ = ['Account', 'Sensor', 'Weather', 'UI', 'Heart', 'DeepSeek']

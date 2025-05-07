import httpx
import orjson as json

from urllib.parse import quote

from core.builtins.assigned_element import WeatherInfoElement
from core.builtins.elements import WeatherElements, WeatherInfoElements
from core.pydantic_models import WeatherDaily, Indices
from core.utils.http import url_get
from config import config
from.key import generate_jwt

key = generate_jwt()

# header = {"Authorization": "Bearer "+key}
header = {"X-QW-Api-Key": config("legacy_api_key")}

class QWeather:
    def __init__(self, client: httpx.AsyncClient = None, city=None):
        self.__city_id = None
        self.__lon = None
        self.__lat = None
        self.city = city
        self.client = client


    async def find_city(self):
        """
        通过城市名称查找城市ID，
        参见 https://dev.qweather.com/docs/api/geo/city-lookup/
        :return: 城市id
        """
        url = f"https://geoapi.qweather.com/v2/city/lookup?location={quote(self.city)}"
        response = json.loads(await url_get(self.client, url, header))
        if response.get('code', 404) == "200":
            self.__city_id = response.get('location')[0].get('id')
            self.__lat = response.get('location')[0].get('lat')
            self.__lon = response.get('location')[0].get('lon')
        else:
            raise ValueError(f"City {self.city} not found.")
        return response.get('location')[0].get('id')


    async def get_7days(self, city_id=None):
        """
        获取未来7天的天气预报，
        参见 https://dev.qweather.com/docs/api/weather/weather-daily-forecast/
        :param city_id: 城市ID
        :return: 返回的7日天气
        """
        if city_id is None:
            await self.find_city()
        url = f"https://devapi.qweather.com/v7/weather/7d?location={quote(self.__city_id)}"
        response = json.loads(await url_get(self.client,url,header))
        if response.get('code', 404) == "200":
            return response.get('daily')
        else:
            raise ValueError(f"City {self.city} not found.")

    async def get_indices(self, city_id=None):
        """
        获取生活指数，
        参见 https://dev.qweather.com/docs/api/indices/indices1d/
        :param city_id: 城市ID
        :return: 返回的生活指数
        """
        if city_id is None:
            await self.find_city()
        url = f"https://devapi.qweather.com/v7/indices/1d?type=0&location={quote(self.__city_id)}"
        response = json.loads(await url_get(self.client, url, header))
        if response.get('code', 404) == "200":
            return response.get('daily')
        else:
            raise ValueError(f"City {self.city} not found.")

    async def get_aqi(self, city_id="none"):
        """
        获取空气质量，
        参见 https://dev.qweather.com/docs/api/air/air-now/
        :param city_id: 城市ID
        :return: 返回的空气质量
        """
        if city_id is None:
            await self.find_city()
        url = f"https://api.qweather.com/airquality/v1/current/{quote(self.__lat)}/{quote(self.__lon)}"
        response = json.loads(await url_get(self.client, url, header))
        if response.get('code', 404) == "200":
            return response.get('now')
        else:
            raise ValueError(f"City {self.city} not found.")

    async def get_weather_element(self, weather_element: WeatherElements) -> WeatherInfoElements:
        """
        获取天气元素
        :param weather_element: 天气元素
        :return: 返回的天气元素
        """
        # if self.__city_id is None:
        #     self.city = weather_element.city
        #     await self.find_city()
        # city_id = await self.find_city()
        # daily = await self.get_7days(city_id)
        # indices = await self.get_indices(city_id)
        # weather_info = WeatherInfoElement(
        #     indices=indices,
        #     daily=daily,
        #     city=self.city,
        #     city_id=city_id,
        #     lat=self.__lat,
        #     lon=self.__lon
        # )
        weather_info = WeatherInfoElement(
            indices=[Indices(
                date='2222-22-2',
                type='114514',
                name='指数',
                level='12',
                category='xd',
                text='适合玩原神',
            )],
            daily=[WeatherDaily(fxDate="1",
                                sunrise="2",
                                sunset="3",
                                moonrise="4",
                                moonset='5',
                                moonPhase='6',
                                moonPhaseIcon='7',
                                tempMax='8',
                                tempMin='9',
                                iconDay='100',
                                textDay='114514',
                                iconNight='100',
                                textNight='1919810',
                                wind360Day='11',
                                windDirDay='111',
                                windScaleDay='1111',
                                windSpeedDay='11111',
                                wind360Night='111111',
                                windDirNight='11111111',
                                windScaleNight='11111111',
                                windSpeedNight='111111',
                                humidity='1111111',
                                precip='1111111',
                                pressure='1111111',
                                vis='11111',
                                cloud='1111',
                                uvIndex='111',
                                )],
            city=self.city,
            city_id="114514",
            lat="114",
            lon="514"
        )
        return weather_info


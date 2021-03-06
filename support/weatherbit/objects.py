from enum import Enum

class Units(Enum):
    metric = 0,
    imperial = 1

class PrecEvents(Enum):
    rain = 0,
    snow = 1,
    hail = 2,
    freezing_rain = 3,

class precipitation:

    def __init__(self, precipitation_data):
        self._current = None

class temperature():

    def __init__(self, temperature_data):
        self._feels_like = temperature_data['app_temp']
        self._actual = temperature_data['temp']
        self._unit = None

    @property
    def feels_like(self):
        return self._feels_like

    @property
    def actual(self):
        return self._actual

class forecast:

    def __init__(self, forecast_data):
        self._timestamp = forecast_data['ts']
        self._wind_speed = forecast_data['wind_spd']
        self._wind_direction = forecast_data['wind_dir']
        self._cloud_coverage = forecast_data['clouds']
        self._pressure = forecast_data['pres']
        self._day_to_night_ratio = forecast_data['pod']
        self._visibility = forecast_data['vis']
        self._uv_index = forecast_data['uv']

        self._temperature = temperature(forecast_data)
        self._precipitation = precipitation(forecast_data)

    @property
    def temperature(self):
        return self._temperature

    @property
    def precipitation(self):
        return self._precipitation

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def wind_speed(self):
        return self._wind_speed

    @property
    def wind_direction(self):
        return self._wind_direction

    @property
    def cloud_coverage(self):
        return self._cloud_coverage

    @property
    def pressure(self):
        return self._pressure

    @property
    def day_to_night(self):
        if self._day_to_night_ratio == "d":
            return 0
        elif self._day_to_night_ratio == "n":
            return 1
        return self._day_to_night_ratio

    @property
    def visibility(self):
        return self._visibility

    @property
    def uv_index(self):
        return self._uv_index

class weather:

    def __init__(self, data):
        obj_data = data['data']
        self._forecast = []
        self._city_name = data['city_name']
        self._state_code = data['state_code']
        self._country_code = data['country_code']
        self._lat = data['lat']
        self._lon = data['lon']
        self._timezone = data['timezone']
        self._process_forecasts(obj_data)


    def _process_forecasts(self, data):

        for x_forecast in data:
            self._forecast.append(forecast(x_forecast))

    def __len__(self):
        return self._forecast.__len__()

    @property
    def forecasts(self):
        return self._forecast

    @property
    def city_name(self):
        return self._city_name

    @property
    def state(self):
        return self._state_code

    @property
    def lat(self):
        return self._lat

    @property
    def lon(self):
        return self._lon
import requests, json
from support.weatherbit import objects
from support import __version__, __title__

class ConnectionError(Exception):
    pass

class connection():

    _api_address = 'https://api.weatherbit.io/v2.0/'

    def __init__(self, api_token):
        self._session = requests
        self._api_token = api_token
        self._header = {'user-agent':'{}/{}'.format(__title__, __version__)}

    def _build_address(self, endpoint):
        return self._api_address + endpoint
    def get_forecast_hourly(self, byIp=True, **kwargs):
        try:
            kwargs['city']
            kwargs['state']
            kwargs['country']
            kwargs['postal_code'],
            kwargs['city_id']
        except KeyError:
            pass

        location_method = {
            'city' : 0,
            'state' : 0,
            'country' : 0,
            'postal_code' : 1,
            'city_id' : 2
        }

        last_type = -1

        for key in kwargs.keys():
            try:
                if location_method[key] == last_type or last_type == -1:
                    last_type = location_method[key]
                else:
                    raise(ValueError("Incompatible location type"))
            except KeyError:
                pass

        if last_type == 0:
            try:
                kwargs['city']
            except KeyError:
                raise(ValueError("Missing 'city' value"))
            state = None
            country = None
            try:
                state = kwargs['state']
            except KeyError:
                pass
            try:
                country = kwargs['country']
            except KeyError:
                pass

            location = "?city={}".format(kwargs['city'])
            if state != None:
                location += ",{}".format(state)
            if country != None:
                location += "&country={}".format(country)

        elif last_type == 1:
            location = ""
        elif last_type == 2:
            location = ""
        else:
            location = "?ip=auto"
        address = self._build_address("forecast/hourly"+location)
        payload = {'key' : self._api_token,
                   'units':'I',
                   'hours':12}

        r = self._session.get(address, params=payload, headers=self._header)
        try:
            rjson = r.json()
            weatherobj = objects.weather(rjson)
        except json.decoder.JSONDecodeError:
            raise(ConnectionError)
        return weatherobj


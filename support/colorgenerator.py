from colour import Color

# Will choose red hue for 65 to 95, and then begin to turn orange afterwords
# Will choose blue hue for 35 to 65, and then begin to turn cyan below 35

blue = Color("blue")
red = Color("red")
white = Color("white")
cyan = Color("#00FFFF")
dark_orange = Color("#FF8C00")

class TemperatureScheme:
    _low_min = 5
    _high_min = 105
    def __init__(self, midpoint=65, min=35, max=95):
        self._midpoint = midpoint
        self._min = min
        self._max = max

        self._min_range = midpoint - min
        self._max_range = max - midpoint
        colors_low = list(blue.range_to(white, self._min_range))
        colors_high = list(white.range_to(red, self._max_range))
        self._colors = colors_low + colors_high


        self._colors_low_low = list(cyan.range_to(blue, self._min - self._low_min))
        self._colors_high_high = list(red.range_to(dark_orange, self._high_min - self._max))


    def get(self, temp):
        #Do normal method
        if temp >= self._min or temp <= self._max:
            color_temp = temp - self._min
            return int(self._colors[color_temp].get_hex_l()[1:], 16)
        #Do less than normal temp
        elif temp < self._min:
            color_temp = temp - self._low_min
            try:
                return int(self._colors_low_low[color_temp].get_hex_l()[1:], 16)
            except KeyError:
                return int(cyan.get_hex_l()[1:], 16)
        #Do greater than normal temp
        elif temp > self._max:
            color_temp = temp - self._max
            try:
                return int(self._colors_high_high[color_temp].get_hex_l()[1:], 16)
            except KeyError:
                return int(dark_orange.get_hex_l()[1:], 16)
        pass
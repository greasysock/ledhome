from colour import Color
import sys
EPSILON = sys.float_info.epsilon  # smallest possible difference
# Will choose red hue for 65 to 95, and then begin to turn orange afterwords
# Will choose blue hue for 35 to 65, and then begin to turn cyan below 35

blue = Color("blue")
red = Color("red")
white = Color("#FFFFFF")
black = Color("black")
cyan = Color("#00FFFF")
dark_orange = Color("#FF8C00")

class TemperatureScheme:
    _low_min = 5
    _high_min = 105
    def __init__(self, midpoint=65, min=35, max=95):
        self._midpoint = midpoint
        self._min = min
        self._max = max

        self._min_range = midpoint - min + 1
        self._max_range = max - midpoint + 1

        colors_low = self._range_to(blue, white, self._min_range)
        colors_high = list(white.range_to(red, self._max_range))
        self._colors = colors_low + colors_high

        self._colors_low_low = list(cyan.range_to(blue, self._min - self._low_min))
        self._colors_high_high = list(red.range_to(dark_orange, self._high_min - self._max))

    # Source Author: https://stackoverflow.com/questions/20792445/calculate-rgb-value-for-a-range-of-values-to-create-heat-map martineau
    def _convert_to_rgb(self, minval, maxval, val, colors):
        fi = float(val - minval) / float(maxval - minval) * (len(colors) - 1)
        i = int(fi)
        f = fi - i
        if f < EPSILON:
            return colors[i]
        else:
            (r1, g1, b1), (r2, g2, b2) = colors[i], colors[i + 1]
            return int(r1 + f * (r2 - r1)), int(g1 + f * (g2 - g1)), int(b1 + f * (b2 - b1))
    def _range_to(self, target_col, range_col, steps):
        minval, maxval = 1, 3
        delta = float(maxval - minval) / steps
        colors = [self.tuple_change_scale(target_col.get_rgb()),
                  self.tuple_change_scale(range_col.get_rgb())]  # [BLUE, GREEN, RED]
        out_list = list()
        for i in range(steps + 1):
            val = minval + i * delta
            r, g, b = self._convert_to_rgb(minval, maxval, val, colors)
            r = r/255
            g = g/255
            b = b/255
            temp_color = Color(rgb=(r,g,b))
            out_list.append(temp_color)
        return out_list
    def tuple_change_scale(self, color_tuple):
        return self.change_scale(color_tuple[0]), self.change_scale(color_tuple[1]), self.change_scale(color_tuple[2])
    def change_scale(self, color, in_scale = 1,out_scale=16):
        out_color = color / in_scale
        out_value = round((color * out_scale ** 2))
        if out_value > 0:
            return out_value - 1
        return out_value

    def get(self, temp):
        #Do normal method
        if temp >= self._min and temp <= self._max:
            color_temp = temp - self._min
            out_color = self._colors[color_temp]
        #Do less than normal temp
        elif temp < self._min:
            color_temp = temp - self._low_min
            try:
                if color_temp < 0:
                    out_color = cyan
                else:
                    out_color = self._colors_low_low[color_temp]
            except IndexError:
                out_color = cyan
        #Do greater than normal temp
        elif temp > self._max:
            color_temp = temp - self._max
            try:
                out_color = self._colors_high_high[color_temp]
            except IndexError:
                out_color = dark_orange
        else:
            out_color = black
        out_red = self.change_scale(out_color.get_red())
        out_green = self.change_scale(out_color.get_green())
        out_blue = self.change_scale(out_color.get_blue())
        return out_red, out_green, out_blue
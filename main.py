from support import apa102, colorschemes
from weather import Weather
from colour import Color
import time

num_led = 10
woeid = 2347592

top_high = 100
bottom_low = 10
color_range = top_high - bottom_low

blue = Color("blue")
colors = list(blue.range_to(Color("red"), color_range))

def get_high_low():
    weather = Weather()
    lookup = weather.lookup(woeid)
    forcast = lookup.forecast()
    return (int(forcast[0].high()), int(forcast[0].low()))

if __name__ == "__main__":
    weather = get_high_low()
    print(weather)
    print(colors[weather[0]])
    pass
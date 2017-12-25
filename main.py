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
    print(colors[weather[0]].get_hex()[1:])
    color_code = int(colors[weather[0]].get_hex()[1:],16)
    color_code_low = int(colors[weather[1]].get_hex()[1:],16)
    high_cycle = colorschemes.Solid(num_led=num_led, pause_value=3,num_steps_per_cycle=num_led,num_cycles=3,color=color_code, brightness=100)
    low_cycle = colorschemes.Solid(num_led=num_led, pause_value=3,num_steps_per_cycle=num_led,num_cycles=3,color=color_code_low, brightness=100)
    while True:
        high_cycle.start()
        low_cycle.start()

    pass
# tealight
An led driver script that changes the color temperature based on the weather. Currently only supports APA102 LEDs.

### Requirements:

* A Raspberry Pi or a development board with GPIO libraries.
* APA102 Led Strips. Although support for other strips can easily be added.
* A free account on `weatherbit.io`

### Prerequisites:

* Python 3, tmux
* Tkinter for testing on PC, otherwise optional
* https://github.com/adafruit/Adafruit_Python_GPIO

### Setup:

Edit your bashrc script or zsh shell startup script to include these lines and add your api code that you received from weatherbit. You are responsible for keeping this secure.
```
#tealight configuration
export weatherbit_api="your_weathebit_api"
export weatherbit_city="New York"
export weatherbit_state="NY"
```
Then to run, enter:
 ```
mkdir ~/git
cd ~/git
git clone https://github.com/greasysock/tealight.git
cd tealight
python3 ./main.py
```
To have this run indefinitely, enter a tmux shell and start tealight in there.
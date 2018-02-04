# tealight
An led driver script that changes the color based on the weather. Currently only supports APA102 LEDs.

### Requirements:

* A Raspberry Pi or a development board with GPIO libraries.
* An APA102 Led Strip. Although support for other strips can easily be added.
* A free account on https://www.weatherbit.io

### Prerequisites:

* Python 3, tmux, scipy, numpy `sudo apt-get install python3 tmux python3-scipy python3-numpy python3-pip`
* Python 3 packages colour and requests `sudo pip3 install colour requests`
* Tkinter for testing on PC, otherwise optional
* https://github.com/adafruit/Adafruit_Python_GPIO
```
sudo apt-get update
sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo python3 ./setup.py install
cd ..
rm -R Adafruit_Python_GPIO
```

### Setup:

Edit your bashrc script or zsh shell startup script to include these lines and add your api code that you received from weatherbit. You are responsible for keeping this secure.
```
#tealight configuration
export weatherbit_api="your_weathebit_api"
export weatherbit_city="New York"
export weatherbit_state="NY"
```
Then to install and run:
 ```
mkdir ~/git
cd ~/git
git clone https://github.com/greasysock/tealight.git
cd tealight
python3 ./main.py
```
To have this run indefinitely, enter a tmux shell and start tealight in there.


# Raspberry Pi Pico 2W OSINT Portal

An OSINT portal for the Raspberry Pi Pico 2W


## Authors

- [@basilesanast1](https://www.github.com/basilesanast1)


## About this project

This project utilizes the WiFi capabilities of the Raspberry Pi Pico 2W in order to display a working OSINT portal via a local web server. It scrapes weather data, headlines and categorizes them.
## Installation

Installing this portal on your Raspberry Pi Pico 2W is very easy. All the files needed are uploaded in this repository. You will need:

1. MicroPython 1.28.0 (.uf2 file is in the repository)
2. [Thonny](https://thonny.org/)
3. Raspberry Pi Pico 2W board (any other compatible boards will do)
4. USB data cable


First download this repository as a `.zip` file. Extract the contents of the `.zip` file and keep `main.py` and `RPI_PICO2_W-20260406-v1.28.0.uf2`. Next, hold the `BOOTSEL` button down on your Pico and connect it to your computer. After it connects release the button. Then copy `RPI_PICO2_W-20260406-v1.28.0.uf2` to the root of your Pico. It will automatically reboot and show up as a serial device. Next, open Thonny and connect to your Pico. In Thonny, open `main.py` and edit `SSID` and `PASSWORD` with your WiFi credentials. After that, save the file to your Pico with Thonny and you are done. When the script starts, you will see the IP address of your Pico in the serial console. The portal will be hosted at `http://IP_ADDRESS:8080`
    

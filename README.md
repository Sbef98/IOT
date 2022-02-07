# IOT
> An LED is enough sometimes

## Purpose of this project
The purpose is to build a framework that easily allows anybody to make their shop smarter than usual. With the help of
sensors and actuators we want customers to have a better experience in your shop. Therefor we want for example to change
the color of the light or the temperature in the shop if specific customer groups enter it.

## Usage:
The code inside of `sensor/protocol` is supposed to run on an arduino where several sensors are attached.

The code in the folder `bridge` is supposed to run on e.g. a raspberry pi which then is able to send messages to via http to a cloud.

Start the bridge via `python -m bridge` from the current folder. 

The code in the folder `cloud` is supposed to run somewhere reachable via http. It stores values and computes predictions for the actuators on the arduino based on the data stored in the database.

## Resources:
- For being able to detect age and gender of customers entering our shop we used [https://github.com/afaq-ahmad/Gender-and-Age-Detection-based-Customer-Tracking-Classification-on-Raspberry-pi](https://github.com/afaq-ahmad/Gender-and-Age-Detection-based-Customer-Tracking-Classification-on-Raspberry-pi) since we want to use it in edge-computing on a raspberry pi later

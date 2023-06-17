# Dronehook
Repository of all documentation for and code used on Dronehook.

# Outline
Dronehook is an autonomous fixed-wing UAV designed to grab packages from a designated station mid-flight. We are designing it to combine the long-range advantage of fixed-wing flight with the reliability, scalability, and speed of an autonomous system. Much of the project has been resolving compatibility and install issues, which will all be documented here.

# Setup
Our Ground Control Station (GCS) is a Dell XPS 13 laptop running Ubuntu 18.04. We tried to use both 22.04 and 20.04 but ran into issues in both versions when downloading [Ardupilot SITL](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html), which is software that allows us to simulate our plane's flight controller and send it commands to determine if the control code we are writing functions as intended.
Our code is written in Python but we are considering refactoring it to C++ if we think there will be significant performance increases. We use Python 3.6.9 with [OpenCV 4.6.0 installed on a NNVIDIA Jetson Nano](https://github.com/AastaNV/JEP/tree/master/script). We attached a CSI camera (Raspberry Pi HQ Camera v1.0 -- IMX477 sensor) directly to the Jetson and used the jetson-io.py installed on the Jetson to switch the camera driver from IMX219 to IMX477. The example code [found here](https://jetsonhacks.com/2019/04/02/jetson-nano-raspberry-pi-camera/) worked for us in the CLI to start up the camera. The code uses the gstreamer plugin to control the camera. OpenCV 3.2.0 does not come with gstreamer support so the Python examples did not work, though the CLI ones did.

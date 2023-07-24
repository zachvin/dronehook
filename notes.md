# File description
This file follows all software/electrical work in building and understanding Dronehook.

# Electronics
## NVIDIA Jetson pinout description

| Pin | Desc | Purpose |
| --- | --- | --- |
| 39 | GND
| 37 | GPIO | Encoder A |
| 35 | GPIO | Encoder B |
| 33 | PWM | Motor speed |
| 31 | GPIO | Motor direction |
| 20 | GND
| 17 | 3.3V | Logic power

Most of the IO pins are physically next to each other on the board. This is intentional and for the purpose of combining the connecting jumper cables with heat shrink to make a single connector. Pins 20 and 17 are diagonal to one another and form another connector using an extra two blank cables. Detailed information on the motor driver connections can be found [here](https://www.pololu.com/product/2960/pictures).

# Software
## Explanation of file structure
The Dronehook repository contains all the test and final onboard files. The test files are split into folders according to their function on the plane and the final files are in the `onboard` folder.

## Control flow
Dronehook uses `pymavlink` (but not `dronekit-python`). The master code runs on the onboard companion computer (a NVIDIA Jetson Nano) and creates a software connection via USB to the flight controller. Upon successful connection, the code then arms the plane and takes off autonomously. The drone then flies to a GPS location that we set manually (this will be automated in the future) and then flies to the GPS location of the Package Retrieval Station (PRS). On this leg of the mission the camera starts up and Dronehook starts looking for the ArUco marker.

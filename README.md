# DroneHook
Repository for all documentation for and code used on DroneHook.

# Setup
Simulation setup is as described in this set of YouTube videos:
https://www.youtube.com/watch?v=2iF9jp0YA8w&list=PLgiealSjeVyx3t4N9GroE29SbVwhYrOtL&index=3

Image processing files require OpenCV and Numpy for Python.

# Running the Dronekit simulation
`sim_vehicle.py --map --console`

`python3 drones.py`

# Running image processing with OpenCV on Linux
1. Open virtual environment:
`source venvs/dronesim3/bin/activate`
2. Make file executable:
`chmod +x trackballoon.py`
3. Run file
`./trackballoon.py`

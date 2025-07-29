# py_get_init_pos

Modified version of the [ROS2 Python Basic Subscriber Example](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html) combined with the [geonav_conversions.py file from geonav_transform](https://github.com/bsb808/geonav_transform/blob/master/src/geonav_transform/geonav_conversions.py). Converts GPS coordinates from a [NavSatFix](https://github.com/ros2/common_interfaces/blob/rolling/sensor_msgs/msg/NavSatFix.msg) message topic into the local XYZ coordinate system used by Rviz2 to obtain the initial position of the sensor on the local grid. Writes the XYZ coordinates to the [initial_state](https://docs.ros.org/en/noetic/api/robot_localization/html/state_estimation_nodes.html#initial-state) parameter of a user-specified robot_localization params yaml file.

## Requirements

Ubuntu & ROS2    
GPS Data published as a NavSatFix ROS2 topic 

### Tested Using

Ubuntu 22.04 ARM64    
ROS2 Humble    
Nvidia Jetson AGX Orin    
Inertial Sense uINS    
[ISRoverNetworkNMEA](https://github.com/arcater/ISRoverNetworkNMEA)
[is_gps_publisher_ros2](https://github.com/ChesterMK7/is_gps_publisher_ros2)    

## Setup

Create a ROS2 Workspace

``` bash
mkdir -p gpsWS/src
cd gpsWS/src
```

Clone the respository in the src folder

``` bash
git clone https://github.com/ChesterMK7/py_get_init_pos -b orientation_experimental
```

Make sure to configure the files you want to use

``` bash
nano py_get_init_pos/py_get_init_pos/<python_file>
```

Specifically modify these lines in gps_convert.py/orientation_experimental.py

``` python
# Filenames for param input and output
input_file = "/home/orin/Desktop/launch_files/nav2_gps/scout/params/scout_dual_ekf_navsat_params.backup.yaml"
# Note that the output file WILL BE OVERWRITTEN when the node runs
output_file = "/home/orin/Desktop/launch_files/nav2_gps/scout/params/scout_dual_ekf_navsat_params.yaml"
```

Return to the workspace directory and build using colcon

``` bash
cd ..
source /opt/ros/<ros2-version>/setup.bash
colcon build
```

Source the workspace

``` bash
source install/setup.bash
```

## Usage

Run the initial position node

``` bash
ros2 run py_get_init_pos gps_convert
```

Run the calculate orientation node (untested)

``` bash
ros2 run py_get_init_pos orientation_calc

# ROS 2 Autonomous Mobile Robot

Completed educational simulation of a differential-drive robot: build a room map
with SLAM Toolbox, save it, and navigate to RViz goals using AMCL and Nav2.
The robot has reached navigation goals in simulation. This project uses no physical hardware.

Developed on Windows/WSL2 with Ubuntu 24.04, ROS 2 Jazzy, and Gazebo Harmonic.
Inspired by Josh Newans’ Building a Mobile Robot tutorial, adapted from Gazebo
Classic to Harmonic.

## Architecture

- URDF/Xacro defines the chassis, two driving wheels, caster, and sensor frames.
- Gazebo Harmonic DiffDrive drives the wheels and publishes odometry and
  `odom → base_link`. Wheel radius: 0.05 m; separation: 0.35 m.
- Gazebo JointStatePublisher and ROS bridges supply `/joint_states`.
  `robot_state_publisher` publishes internal robot transforms.
- A GPU LiDAR supplies `/scan`; bridges also carry `/cmd_vel`, `/odom`, `/tf`, and `/clock`.
- SLAM Toolbox builds the occupancy map during manual driving.
- For saved-map navigation, the map server loads the map, AMCL publishes
  `map → odom`, and Nav2 plans and sends velocity commands to Gazebo.
- All navigation runs with simulation time. No ros2_control is required for this setup.

The navigation TF chain is `map → odom → base_link → laser_frame`
(with the chassis frame between base_link and laser_frame).
Do not run SLAM Toolbox alongside AMCL or a standalone joint-state publisher
alongside Gazebo’s joint-state system.

## Build

The Git repository/package is `~/ros2_navigation_ws/src/my_bot`, inside the workspace.
Required ROS packages include `ros-jazzy-ros-gz`, `ros-jazzy-slam-toolbox`,
`ros-jazzy-navigation2`, `ros-jazzy-nav2-bringup`, `ros-jazzy-xacro`,
`ros-jazzy-robot-state-publisher`, `ros-jazzy-rviz2`, and
`ros-jazzy-teleop-twist-keyboard`.

```bash
cd ~/ros2_navigation_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select my_bot
source install/setup.bash
```

## Run saved-map navigation

Stop any previous simulation/navigation launches first, then:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_navigation_ws/install/setup.bash
ros2 launch my_bot navigation.launch.py
```

This starts the room simulation, robot and bridges, map server, AMCL, Nav2, and
RViz with `config/navigation.rviz`. Wait for navigation lifecycle nodes to become
active, then choose **Nav2 Goal** and click-drag on clear floor to set position
and final heading. Begin with a short goal, then test the doorway and obstacles.
Stop keyboard teleoperation before sending navigation goals.
Ctrl+C in the launch terminal stops the launched processes.

AMCL is configured to initialize at `(x=0, y=0, yaw=0)` in the **saved map frame**.
This assumes the map was created from the same starting pose as the simulation.
Automatic initialization has been configured; verify scan-to-wall alignment on
startup before driving. If needed, correct it with RViz’s **2D Pose Estimate**.
For another spawn/map, change `amcl.initial_pose` in `config/nav2.yaml`, or set
`set_initial_pose: false` to initialize manually.

Launch arguments: `world`, `map`, `params_file`, `rviz_config`, and `rviz`.
For example, use `rviz:=false` to omit RViz.

## Create a new map

Run each long-running command in a separate terminal with ROS and the workspace sourced.
Keep saved-map navigation/AMCL stopped.

```bash
ros2 launch my_bot launch_sim.launch.py \
  world:="$HOME/ros2_navigation_ws/src/my_bot/worlds/room.sdf"
```

```bash
ros2 launch slam_toolbox online_async_launch.py \
  use_sim_time:=true \
  slam_params_file:="$HOME/ros2_navigation_ws/src/my_bot/config/slam.yaml"
```

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive slowly through both areas and return to known locations. Inspect `/map`
and `/scan` in RViz with fixed frame `map`. Keep SLAM running while saving:

```bash
mkdir -p ~/ros2_navigation_ws/src/my_bot/maps
ros2 run nav2_map_server map_saver_cli \
  -f ~/ros2_navigation_ws/src/my_bot/maps/new_room \
  --ros-args -p use_sim_time:=true
```

This writes an occupancy image and YAML metadata, not a resumable SLAM pose graph.
Keep the two files together. Rebuild to install newly added maps, then select the
new YAML with the navigation launch’s `map` argument.

## Project files and scope

| Path | Purpose |
|---|---|
| `description/` | Robot, sensors, and Harmonic drive systems |
| `worlds/room.sdf` | Colored enclosed room, wide doorway, static obstacles |
| `worlds/obstacles.sdf` | Original obstacle world |
| `maps/room.yaml`, `maps/room.pgm` | Saved navigation map |
| `config/slam.yaml` | Mapping configuration |
| `config/nav2.yaml` | Localization, costmaps, controllers, and speed limits |
| `config/navigation.rviz` | Saved navigation displays and tools |
| `launch/navigation.launch.py` | Combined saved-map navigation startup |

RGB and depth camera Xacros were explored and their images viewed during development.
They are optional: check the includes in `robot.urdf.xacro` to see which are enabled.
The combined launch bridges LiDAR, not camera images; depth data is not used by Nav2.
Localization accuracy and controller tuning can be refined further; the completed
milestone is basic goal navigation in this simulated room, not hardware validation.

## Acknowledgments

[Josh Newans / Articulated Robotics](https://articulatedrobotics.xyz/),
the [`my_bot` template](https://github.com/joshnewans/my_bot), and the ROS 2,
Gazebo, SLAM Toolbox, and Nav2 projects.

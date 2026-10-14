
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_bot'

    # 1. Start robot_state_publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. Start Gazebo Harmonic
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': '-r empty.sdf'
        }.items()
    )

    # 3. Spawn the robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'my_bot',
            '-z', '0.2'
        ],
        output='screen'
    )

    # 4. Bridge ROS 2 velocity commands to Gazebo
    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
        ],
        output='screen'
    )


    # 5. Bridge Gazebo odometry to ROS 2
    odom_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
        ],
        output='screen'
    )

    # 6. Bridge Gazebo TF to ROS 2
    tf_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        output='screen'
    )

    # 7. Bridge Gazebo simulation time to ROS 2
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    # 8. Bridge simulated wheel joint positions to robot_state_publisher
    joint_state_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/empty/model/my_bot/joint_state'
            '@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        remappings=[
            ('/world/empty/model/my_bot/joint_state', '/joint_states')
        ],
        output='screen'
    )


    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        cmd_vel_bridge,
        odom_bridge,
        tf_bridge,
        clock_bridge,
        joint_state_bridge,
    ])

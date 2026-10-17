"""Start the room simulation, saved-map navigation, and RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('my_bot')
    nav2_share = get_package_share_directory('nav2_bringup')

    arguments = [
        DeclareLaunchArgument(
            'world', default_value=os.path.join(package_share, 'worlds', 'room.sdf')),
        DeclareLaunchArgument(
            'map', default_value=os.path.join(package_share, 'maps', 'room.yaml')),
        DeclareLaunchArgument(
            'params_file', default_value=os.path.join(package_share, 'config', 'nav2.yaml')),
        DeclareLaunchArgument(
            'rviz_config', default_value=os.path.join(package_share, 'config', 'navigation.rviz')),
        DeclareLaunchArgument('rviz', default_value='true'),
    ]

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_share, 'launch', 'launch_sim.launch.py')),
        launch_arguments={'world': LaunchConfiguration('world')}.items(),
    )

    # Nav2 bringup starts both localization and navigation lifecycle managers.
    # AMCL waits for the initial pose supplied through RViz.
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': 'true',
            'slam': 'False',
            'autostart': 'true',
            'use_composition': 'False',
        }.items(),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    return LaunchDescription(arguments + [simulation, navigation, rviz])

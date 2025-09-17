import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    
    # Get URDF file path
    my_rb1_description_dir = get_package_share_directory('my_rb1_description')
    urdf_file = os.path.join(my_rb1_description_dir, 'urdf', 'my_rb1_robot.urdf')
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                Command(['cat ', urdf_file]), 
                value_type=str
            ),
            'use_sim_time': True
        }]
    )
    
    # Spawn Robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_rb1_robot',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'rb1_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher,
        spawn_entity
    ])
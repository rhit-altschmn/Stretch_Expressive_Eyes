#!/usr/bin/env python3

import argparse as ap
from functools import partial
import math
import sys
from .keyboard_core import KBHit

import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint, MultiDOFJointTrajectoryPoint
from geometry_msgs.msg import Transform

import hello_helpers.hello_misc as hm


class GetKeyboardCommands:

    def __init__(self, node):
        self.kb = KBHit()
        
        self.node = node
        self.step_size = 'medium'
        self.rad_per_deg = math.pi/180.0
        self.small_deg = 3.0
        self.small_rad = self.rad_per_deg * self.small_deg
        self.small_translate = 0.005  #0.02
        self.medium_deg = 6.0
        self.medium_rad = self.rad_per_deg * self.medium_deg
        self.medium_translate = 0.04
        self.big_deg = 12.0
        self.big_rad = self.rad_per_deg * self.big_deg
        self.big_translate = 0.06
        self.mode = 'position' #'trajectory' #'navigation'

    def get_deltas(self):
        if self.step_size == 'small':
            deltas = {'rad': self.small_rad, 'translate': self.small_translate}
        if self.step_size == 'medium':
            deltas = {'rad': self.medium_rad, 'translate': self.medium_translate} 
        if self.step_size == 'big':
            deltas = {'rad': self.big_rad, 'translate': self.big_translate} 
        return deltas

    def print_commands(self):
        print('---------- KEYBOARD TELEOP MENU -----------')
        '''print('                                           ')
        print('              i HEAD UP                    ')
        print(' j HEAD LEFT            l HEAD RIGHT       ')
        print('              , HEAD DOWN                  ')
        print('                                           ')
        print('                                           ')
        print(' 7 BASE ROTATE LEFT     9 BASE ROTATE RIGHT')
        print(' home                   page-up            ')
        print('                                           ')
        print('                                           ')
        print('              8 LIFT UP                    ')
        print('              up-arrow                     ')
        print(' 4 BASE FORWARD         6 BASE BACK        ')
        print(' left-arrow             right-arrow        ')
        print('              2 LIFT DOWN                  ')
        print('              down-arrow                   ')
        print('                                           ')
        print('                                           ')
        print('              w ARM OUT                    ')
        print(' a WRIST FORWARD        d WRIST BACK       ')
        print('              x ARM IN                     ')
        print('                                           ')
        print('                                           ')
        print('              5 GRIPPER CLOSE              ')
        print('              0 GRIPPER OPEN               ')
        print('                                           ')
        print('  step size:  b BIG, m MEDIUM, s SMALL     ')
        print('                                           ')
        print('              q QUIT                       ')
        print('                                           ')
        print('-------------------------------------------')'''

    def get_command(self, node):
        command = None
        c = None

        if self.kb.kbhit(): # Returns True if any key pressed
            c = self.kb.getch()


        match c:
            # Base
            case 'w':
                command = {'joint': 'translate_mobile_base', 'inc': self.get_deltas()['translate']}
            case 's':
                command = {'joint': 'translate_mobile_base', 'inc': -self.get_deltas()['translate']}
            case 'a':
                command = {'joint': 'rotate_mobile_base', 'inc': self.get_deltas()['rad']}
            case 'd':
                command = {'joint': 'rotate_mobile_base', 'inc': -self.get_deltas()['rad']}

            # head cam
            case 'f':
                command = {'joint': 'joint_head_tilt', 'delta': (2.0 * self.get_deltas()['rad'])}
            case 'c':
                command = {'joint': 'joint_head_tilt', 'delta': -(2.0 * self.get_deltas()['rad'])}
            case 'x':
                command = {'joint': 'joint_head_pan', 'delta': (2.0 * self.get_deltas()['rad'])}
            case 'v':
                command = {'joint': 'joint_head_pan', 'delta': -(2.0 * self.get_deltas()['rad'])}

            # head cam hot keys
            case 'F':
                command = {'joint': 'joint_head_pan', 'hot': (2.0 * self.get_deltas()['rad'])}
            case 'C':
                command = {'joint': 'joint_head_pan', 'hot': -(2.0 * self.get_deltas()['rad'])}
            case 'X':
                command = {'joint': 'joint_head_pan', 'hot': (2.0 * self.get_deltas()['rad'])}
            case 'V':
                command = {'joint': 'joint_head_pan', 'hot': -(2.0 * self.get_deltas()['rad'])}

            # lift
            case 'h':
                command = {'joint': 'joint_lift', 'delta': self.get_deltas()['translate']}
            case 'n':
                command = {'joint': 'joint_lift', 'delta': -self.get_deltas()['translate']}
            case 'b':
                command = {'joint': 'wrist_extension', 'delta': self.get_deltas()['translate']}
            case 'm':
                command = {'joint': 'wrist_extension', 'delta': -self.get_deltas()['translate']}

            # wrist
            case 'l':
                command = {'joint': 'joint_wrist_yaw', 'delta': -self.get_deltas()['rad']}
            case 'j':
                command = {'joint': 'joint_wrist_yaw', 'delta': self.get_deltas()['rad']}
            case 'k':
                command = {'joint': 'joint_wrist_pitch', 'delta': -self.get_deltas()['rad']}
            case 'i':
                command = {'joint': 'joint_wrist_pitch', 'delta': self.get_deltas()['rad']}
            case 'u':
                command = {'joint': 'joint_wrist_roll', 'delta': -self.get_deltas()['rad']}
            case 'o':
                command = {'joint': 'joint_wrist_roll', 'delta': self.get_deltas()['rad']}

            # gripper
            case '8':
                command = {'joint': 'joint_gripper_finger_left', 'delta': -self.get_deltas()['rad']}
            case '7':
                command = {'joint': 'joint_gripper_finger_left', 'delta': self.get_deltas()['rad']}
            
        
        # if c == 'b':
        #     node.get_logger().info('process_keyboard.py: changing to BIG step size')
        #     self.step_size = 'big'
        # if c == 'm':
        #     node.get_logger().info('process_keyboard.py: changing to MEDIUM step size')
        #     self.step_size = 'medium'
        # if c == 's':
        #     node.get_logger().info('process_keyboard.py: changing to SMALL step size')
        #     self.step_size = 'small'
        
        if c == 'q' or c == 'Q':
            node.get_logger().info('keyboard_teleop exiting...')
            node.get_logger().info('Received quit character (q), so exiting')
            node.destroy_node()
            rclpy.shutdown()
            sys.exit(0)

        ####################################################

        return command


class KeyboardTeleopNode(Node):

    def __init__(self):
        super().__init__('keyboard_teleop')
        

        self.keys = GetKeyboardCommands(self)

        self.joint_state = JointState()
        self.robot_mode = String()
        
    def joint_states_callback(self, joint_state):
        self.joint_state = joint_state

    def mode_callback(self, mode):
        self.robot_mode = mode.data

    def send_command(self, command):
        joint_state = self.joint_state
        if (joint_state is not None) and (command is not None):
            if self.robot_mode == 'position':
                point = JointTrajectoryPoint()
                duration = Duration(seconds=0.0)
                point.time_from_start = duration.to_msg()
                trajectory_goal = FollowJointTrajectory.Goal()
                # trajectory_goal.goal_time_tolerance = rclpy.time.Time()
                joint_name = command['joint']
                trajectory_goal.trajectory.joint_names = [joint_name]

                # for base joints
                if 'inc' in command:
                    inc = command['inc']
                    new_value = inc

                # for non-base joints
                elif 'delta' in command:
                    joint_index = joint_state.name.index(joint_name)
                    joint_value = joint_state.position[joint_index]
                    delta = command['delta']
                    new_value = joint_value + delta
                
                point.positions = [new_value]
                trajectory_goal.trajectory.points = [point]
                self.trajectory_client.send_goal_async(trajectory_goal)

                '''elif self.robot_mode == 'trajectory':
                trajectory_goal = FollowJointTrajectory.Goal()
                # trajectory_goal.goal_time_tolerance = rclpy.time.Time()
                joint_name = command['joint']
                duration1 = Duration(seconds=0.0)
                duration2 = Duration(seconds=1.0)

                # for base joints
                if 'inc' in command:
                    inc = command['inc']
                    point1 = MultiDOFJointTrajectoryPoint()
                    point2 = MultiDOFJointTrajectoryPoint()
                    point1.time_from_start = duration1.to_msg()
                    point2.time_from_start = duration2.to_msg()
                    transform1 = Transform()
                    transform2 = Transform()
                    transform1.translation.x = 0.0
                    transform1.rotation.w = 1.0
                    transform2.translation.x = inc
                    transform2.rotation.w = 1.0
                    point1.transforms = [transform1]
                    point2.transforms = [transform2]
                    # joint_name should be 'position' and not one generated by command i.e. 'translate/rotate_mobile_base'
                    joint_name = 'position'
                    trajectory_goal.multi_dof_trajectory.joint_names = [joint_name]
                    trajectory_goal.multi_dof_trajectory.points = [point1, point2]
                    self.trajectory_client.send_goal_async(trajectory_goal)

                # for non-base joints
                elif 'delta' in command:
                    point1 = JointTrajectoryPoint()
                    point2 = JointTrajectoryPoint()
                    point1.time_from_start = duration1.to_msg()
                    point2.time_from_start = duration2.to_msg()
                    joint_index = joint_state.name.index(joint_name)
                    joint_pos_value = joint_state.position[joint_index]
                    joint_vel_value = joint_state.velocity[joint_index]
                    delta = command['delta']
                    new_value = joint_pos_value + delta
                    point1.positions = [joint_pos_value]
                    point2.positions = [new_value]
                    point1.velocities = [joint_vel_value]
                    point2.velocities = [0.0]
                    trajectory_goal.trajectory.joint_names = [joint_name]
                    trajectory_goal.trajectory.points = [point1, point2]
                    self.trajectory_client.send_goal_async(trajectory_goal)'''

            else:
                self.get_logger().warn('Keyboard teleoperation available only in position or manipulation mode')


    def main(self):
        self.trajectory_client = ActionClient(self, FollowJointTrajectory, '/stretch_controller/follow_joint_trajectory')
        server_reached = self.trajectory_client.wait_for_server(timeout_sec=10.0)
        if not server_reached:
            self.get_logger().error('Unable to connect to server. Timeout exceeded. Is stretch_driver running?')
            sys.exit()

        self.joint_states_sub = self.create_subscription(JointState, '/stretch/joint_states', self.joint_states_callback, 1)
        self.joint_states_sub

        self.robot_mode_sub = self.create_subscription(String, 'mode', self.mode_callback, 10)
        self.robot_mode_sub

        self.trajectory_client = ActionClient(self, FollowJointTrajectory, '/stretch_controller/follow_joint_trajectory')
        server_reached = self.trajectory_client.wait_for_server(timeout_sec=60.0)
        if not server_reached:
            self.get_logger().error('Unable to connect to arm action server. Timeout exceeded.')
            sys.exit()

        
        self.keys.print_commands()
        while rclpy.ok():
            rclpy.spin_once(self)
            command = self.keys.get_command(self)
            self.send_command(command)

        self.keys.kb.set_normal_term()
        self.destroy_node()
        rclpy.shutdown()

def main():
    try:
        rclpy.init()
        node = KeyboardTeleopNode()
        node.main()
    except KeyboardInterrupt:
        node.get_logger().info('interrupt received, so shutting down')

if __name__ == '__main__':
    main()
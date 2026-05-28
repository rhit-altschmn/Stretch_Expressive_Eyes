#!/usr/bin/env python

import rospy
from std_msgs.msg import String
# from pynput import keyboard
import sys, tty, termios

# from playsound import playsound

class KeyboardPublisher:
    def __init__(self):
        rospy.init_node('keyboard_publisher', anonymous=True)

        # Create a publisher for the keyboard input
        self.keyboard_pub = rospy.Publisher('keyboard_input', String, queue_size=10)

        # Set up the keyboard listener
        # self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        # self.keyboard_listener.start()

        # Spin to keep the node alive
        rospy.spin()

    # This allows Ctrl-C and related keyboard commands to still function.
    # It detects escape codes in order to recognize arrow keys. It also
    # has buffer flushing to avoid repeated commands.  This is
    # blocking code.

    def getch(self):
        stdin_fd = 0
        # "Return a list containing the tty attributes for file descriptor
        # fd, as follows: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]"
        # from https://docs.python.org/2/library/termios.html
        original_tty_attributes = termios.tcgetattr(stdin_fd)
        new_tty_attributes = termios.tcgetattr(stdin_fd)
        # Change the lflag (local modes) to turn off canonical mode
        new_tty_attributes[3] &= ~termios.ICANON
        # Set VMIN = 0 and VTIME > 0 for a timed read, as explained in:
        # http://unixwiz.net/techtips/termios-vmin-vtime.html
        new_tty_attributes[6][termios.VMIN] = b'\x00'
        new_tty_attributes[6][termios.VTIME] = b'\x01'
        try:
            termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, new_tty_attributes)
            ch1 = sys.stdin.read(1)
            if ch1 == '\x1b':
            # special key pressed
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                ch = ch1 + ch2 + ch3
            else:
                # not a special key
                ch = ch1
        finally:
            termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, original_tty_attributes)
        
        self.keyboard_pub.publish(ch)
        
        # return ch




    # def on_key_press(self, key):
    #     try:
    #         # Get the character representation of the key
    #         key_char = key.char

    #         # Publish the pressed key to the topic
    #         self.keyboard_pub.publish(key_char)

    #         if key.char == 't':
    #             playsound('/home/hello-robot/catkin_ws/src/joystick_commands/scripts/sounds/robot_sound.mp3')

    #     except AttributeError:
    #         # Handle special keys if needed
    #         pass

if __name__ == '__main__':
    try:
        KeyboardPublisher()
    except rospy.ROSInterruptException:
        pass

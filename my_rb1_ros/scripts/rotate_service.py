#!/usr/bin/env python3

import rospy
from my_rb1_ros.srv import Rotate, RotateResponse
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import tf

class RotateService:
    def __init__(self):
        rospy.init_node('rotate_service_server')
        
        self.service = rospy.Service('/rotate_robot', Rotate, self.handle_rotate_request)
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        
        self.current_yaw = 0.0
        self.is_rotating = False
        
        rospy.loginfo("Service Ready")
        rospy.loginfo("Rotate service server ready")

    def odom_callback(self, msg):
        orientation = msg.pose.pose.orientation
        euler = tf.transformations.euler_from_quaternion([
            orientation.x, orientation.y, orientation.z, orientation.w
        ])
        self.current_yaw = euler[2]

    def handle_rotate_request(self, req):
        rospy.loginfo("Service Requested")
        rospy.loginfo("Received rotation request: %d degrees" % req.degrees)
        
        if self.is_rotating:
            return RotateResponse("Rotation failed: Robot is already rotating")
        
        success = self.rotate_robot(req.degrees)
        
        if success:
            rospy.loginfo("Service Completed")
            return RotateResponse("Rotation completed successfully")
        else:
            return RotateResponse("Rotation failed")

    def rotate_robot(self, degrees):
        self.is_rotating = True
        target_rotation = math.radians(degrees)
        initial_yaw = self.current_yaw
        target_yaw = initial_yaw + target_rotation
        
        while target_yaw > math.pi:
            target_yaw -= 2 * math.pi
        while target_yaw < -math.pi:
            target_yaw += 2 * math.pi
        
        angular_speed = 0.5
        if degrees < 0:
            angular_speed = -angular_speed
        
        twist = Twist()
        twist.angular.z = angular_speed
        rate = rospy.Rate(10)
        
        while not rospy.is_shutdown():
            yaw_diff = target_yaw - self.current_yaw
            
            while yaw_diff > math.pi:
                yaw_diff -= 2 * math.pi
            while yaw_diff < -math.pi:
                yaw_diff += 2 * math.pi
            
            if abs(yaw_diff) < 0.05:
                break
            
            self.cmd_vel_pub.publish(twist)
            rate.sleep()
        
        twist.angular.z = 0
        self.cmd_vel_pub.publish(twist)
        self.is_rotating = False
        return True

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        service = RotateService()
        service.run()
    except rospy.ROSInterruptException:
        pass
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2020 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from genericworker import *
import time
from pyrep import PyRep
from pyrep.objects.vision_sensor import VisionSensor
from pyrep.objects.dummy import Dummy
from pyrep.objects.shape import Shape
from pyrep.objects.joint import Joint
import numpy as np
from pytransform3d.transform_manager import TransformManager
import pytransform3d.transformations as pytr
import pytransform3d.rotations as pyrot
import cv2
from threading import Lock
import itertools as it
import numpy_indexed as npi


class TimeControl:
    def __init__(self, period_):
        """
        Initializes an instance's variables with provided arguments and performs
        required operations, including setting a counter to zero and creating timer
        objects for measuring elapsed time.

        Args:
            period_ (float): duration of a specific interval that is to be counted
                by the function.

        """
        self.counter = 0
        self.start = time.time()  # it doesn't exist yet, so initialize it
        self.start_print = time.time()  # it doesn't exist yet, so initialize it
        self.period = period_

    def wait(self):
        """
        Updates the counter and prints the frequency every second (period) until
        a total time elapsed is reached, at which point it sleeps for the remaining
        time and resets its start time.

        """
        elapsed = time.time() - self.start
        if elapsed < self.period:
            time.sleep(self.period - elapsed)
        self.start = time.time()
        self.counter += 1
        if time.time() - self.start_print > 1:
            print("Freq -> ", self.counter, " Hz")
            self.counter = 0
            self.start_print = time.time()


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map):
        """
        Sets up an instance of `SpecificWorker` with a `TransformManager` and adds
        an transform from an intrinsic Euler-XYZ representation to a world transformation.

        Args:
            proxy_map (`object`.): 4x4 transformation matrix used to translate the
                world coordinate system to the camera's intrinsic coordinate system
                during initialization.
                
                		- `pytr`: It is an instance of the class `TransformManager`,
                which represents the transformation between different coordinate
                systems.
                		- `transform_from`: It is a callable that takes an intrinsic
                euler xyz rotation matrix as input and returns the corresponding
                world-space translation vector.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.tm = TransformManager()
        self.tm.add_transform("origin", "world",
                              pytr.transform_from(pyrot.active_matrix_from_intrinsic_euler_xyz([0.0, 0.0, 0.0]), [0.0, 0.0, 0.0])
                              )

    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):

        #SCENE_FILE = '../../etc/informatica.ttt'
        """
        Sets parameters for a Robocomp simulation, including the scene file, camera
        and laser sensors, PoseEstimation, and joystick data. It also initializes
        a mutex for locking access to sensitive data.

        Args:
            params (dict): 2D laser data read from the Pioneer's front-mounted
                left and right cameras, which is stored in the `ldata_read` list.

        """
        SCENE_FILE = '/home/robocomp/robocomp/components/robocomp-pioneer/etc/exterior-robolab.ttt'

        self.pr = PyRep()
        self.pr.launch(SCENE_FILE, headless=False)
        self.pr.start()

        self.robot_object = Shape("Pioneer")
        self.back_left_wheel = Joint("p3at_back_left_wheel_joint")
        self.back_right_wheel = Joint("p3at_back_right_wheel_joint")
        self.front_left_wheel = Joint("p3at_front_left_wheel_joint")
        self.front_right_wheel = Joint("p3at_front_right_wheel_joint")
        self.radius = 110  # mm
        self.semi_width = 140  # mm

        # cameras
        self.cameras_write = {}
        self.cameras_read = {}

        self.front_left_camera_name = "pioneer_camera_left"
        cam = VisionSensor(self.front_left_camera_name)
        self.cameras_write[self.front_left_camera_name] = {"handle": cam,
                                                     "id": 0,
                                                     "angle": np.radians(cam.get_perspective_angle()),
                                                     "width": cam.get_resolution()[0],
                                                     "height": cam.get_resolution()[1],
                                                     "focal": (cam.get_resolution()[0] / 2) / np.tan(
                                                         np.radians(cam.get_perspective_angle() / 2)),
                                                     "rgb": np.array(0),
                                                     "depth": np.ndarray(0)}

        self.front_right_camera_name = "pioneer_camera_right"
        cam = VisionSensor(self.front_right_camera_name)
        self.cameras_write[self.front_right_camera_name] = {"handle": cam,
                                                     "id": 1,
                                                     "angle": np.radians(cam.get_perspective_angle()),
                                                     "width": cam.get_resolution()[0],
                                                     "height": cam.get_resolution()[1],
                                                     "focal": (cam.get_resolution()[0] / 2) / np.tan(
                                                         np.radians(cam.get_perspective_angle() / 2)),
                                                     "rgb": np.array(0),
                                                     "depth": np.ndarray(0)}


        self.cameras_read = self.cameras_write.copy()
        self.mutex_c = Lock()

        # laser
        self.ldata_write = []
        self.ldata_read = []

        # PoseEstimation
        self.robot_full_pose_write = RoboCompFullPoseEstimation.FullPoseEuler()
        self.robot_full_pose_read = RoboCompFullPoseEstimation.FullPoseEuler()
        self.mutex = Lock()


        self.ldata = []
        self.joystick_newdata = []
        self.speed_robot = []
        self.speed_robot_ant = []
        self.last_received_data_time = 0

    def compute(self):
        """
        Performs a series of actions related to the robot's control, vision, and
        pose estimation, while utilizing the `TimeControl` class to limit the
        execution time.

        """
        tc = TimeControl(0.05)
        while True:
            self.pr.step()
            self.read_laser()
            self.read_cameras([self.front_left_camera_name, self.front_right_camera_name])
            self.read_joystick()
            self.read_robot_pose()
            self.move_robot()

            tc.wait()

    ###########################################
    ### LASER get and publish laser data
    ###########################################

    def read_laser(self):
        """
        Extracts non-intersecting groups of three laser readings and transforms
        them into polar coordinates, then finds the closest position in the polar
        coordinate system for each measurement and fills an angle array with the
        corresponding distance measurement. It then writes the filled angle array
        to a file and pushes the data to a proxy.

        """
        data = self.pr.script_call("get_depth_data@Hokuyo_front", 1)
        if len(data[1]) > 0:
            polar = np.zeros(shape=(int(len(data[1]) / 3), 2))
            i = 0
            for x, y, z in self.grouper(data[1], 3):  # extract non-intersecting groups of 3
                polar[i] = [-np.arctan2(y, x), np.linalg.norm([x, y])]  # add to list in polar coordinates
                i += 1

            angles = np.linspace(-np.radians(120), np.radians(120), 360)  # create regular angular values
            positions = np.searchsorted(angles,
                                        polar[:, 0])  # list of closest position in polar for each laser measurement
            self.ldata_write = [RoboCompLaser.TData(a, 0) for a in angles]  # create empty 360 angle array
            pos, medians = npi.group_by(positions).median(polar[:, 1])  # group by repeated positions
            for p, m in it.zip_longest(pos, medians):  # fill the angles with measures
                if p < len(self.ldata_write):
                    self.ldata_write[p].dist = int(m * 1000)  # to millimeters
            if self.ldata_write[0] == 0:
                self.ldata_write[0] = 200  # half robot width
            for i in range(0, len(self.ldata_write)):
                if self.ldata_write[i].dist == 0:
                    self.ldata_write[i].dist = self.ldata_write[i - 1].dist

            self.ldata_read, self.ldata_write = self.ldata_write, self.ldata_read

            try:
                self.laserpub_proxy.pushLaserData(self.ldata_read)
            except Ice.Exception as e:
                print(e)

    def grouper(self, inputs, n, fillvalue=None):
        iters = [iter(inputs)] * n
        return it.zip_longest(*iters, fillvalue=fillvalue)

    ###########################################
    ### CAMERAS get and publish cameras data
    ###########################################
    def read_cameras(self, camera_names):
        """
        Reads data from given cameras, normalizes and converts RGB and depth images
        to a robot-compatible format, and pushes the resulting RGBD stream to a
        publisher using a Proxy.

        Args:
            camera_names (str): list of camera names for which RGB and depth images
                are to be captured and processed by the `RoboCompCameraRGBDSimple`
                module.

        """
        for camera_name in camera_names:
            cam = self.cameras_write[camera_name]
            image_float = cam["handle"].capture_rgb()
            depth = cam["handle"].capture_depth(True)
            image = cv2.normalize(src=image_float, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX,
                                  dtype=cv2.CV_8U)
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cam["rgb"] = RoboCompCameraRGBDSimple.TImage(cameraID=cam["id"], width=cam["width"], height=cam["height"],
                                                         depth=3, focalx=cam["focal"], focaly=cam["focal"],
                                                         alivetime=time.time(), image=image.tobytes())
            cam["depth"] = RoboCompCameraRGBDSimple.TDepth(cameraID=cam["id"], width=cam["handle"].get_resolution()[0],
                                                           height=cam["handle"].get_resolution()[1],
                                                           focalx=cam["focal"], focaly=cam["focal"],
                                                           alivetime=time.time(), depthFactor=1.0,
                                                           depth=depth.tobytes())

        self.mutex_c.acquire()
        self.cameras_write, self.cameras_read = self.cameras_read, self.cameras_write
        self.mutex_c.release()

            # try:
            #    self.camerargbdsimplepub_proxy.pushRGBD(cam["rgb"], cam["depth"])
            # except Ice.Exception as e:
            #    print(e)

    ###########################################
    ### JOYSITCK read and move the robot
    ###########################################
    def read_joystick(self):
        """
        Reads joystick data and converts it into a motor speed value using the
        `convert_base_speed_to_motors_speed()` function. It also updates the last
        received data time stamp.

        """
        if self.joystick_newdata:  # and (time.time() - self.joystick_newdata[1]) > 0.1:
            datos = self.joystick_newdata[0]
            adv = 0.0
            rot = 0.0
            for x in datos.axes:
                if x.name == "advance":
                    adv = x.value if np.abs(x.value) > 10 else 0
                if x.name == "rotate" or x.name == "turn":
                    rot = x.value if np.abs(x.value) > 0.01 else 0

            converted = self.convert_base_speed_to_motors_speed(adv, rot)
            print("Joystick ", [adv, rot], converted)
            self.joystick_newdata = None
            self.last_received_data_time = time.time()
        else:
            elapsed = time.time() - self.last_received_data_time
            if elapsed > 2 and elapsed < 3:
                self.convert_base_speed_to_motors_speed(0, 0)

    def convert_base_speed_to_motors_speed(self, adv, rot):
        #  adv = r*(Wl + Wr)/2
        #  rot = r*(-Wl + Wr)/2c
        #  isolating Wl,Wr
        #  Wl = ( adv - c*rot ) / r
        #  Wr = ( adv + c*rot ) / r
        """
        Takes the advancement and robot width as input and outputs the motor speeds
        required to maintain a constant radius circular motion based on the radius
        of the robot.

        Args:
            adv (addition operator.): speed of the vehicle at which the wheels'
                joint angles are being calculated.
                
                		- `adv`: The total advance or lead distance, which is a numerical
                value representing the difference between the desired position and
                the current position of the robot.
                		- `self.semi_width`: The width of the robot body in meters, used
                to calculate the relative positions of the wheels.
                		- `self.radius`: The radius of the wheels in meters, used to
                calculate the wheel speeds.
                
                	The function then calculates the left and right velocities of the
                wheels based on the advance distance and the properties of the
                robot body, and sets the target joint velocities for each wheel
                using the `set_joint_target_velocity` method. The return values
                are the left and right velocities in meters per second.
            rot (float): 3D rotation of the robot's body with respect to its
                original orientation, which is used to calculate the left and right
                velocities of the wheels based on their position and semi-major axis.

        Returns:
            pair of real numbers, where each number represents the target velocity
            for one wheel of the robot in the respective direction (left or right:
            the desired velocities for each wheel of the robot.
            
            		- `left_vel`: The desired left wheel velocity in meters per second.
            		- `right_vel`: The desired right wheel velocity in meters per second.
            
            	The function takes in the advance distance `adv` and the rotational
            angle `rot`, and returns the velocity targets for each wheel motor in
            meters per second. The velocity targets are calculated by dividing the
            appropriate amount (based on the semi-width of the robot and the radius
            of the wheels) by the radius of the wheels.

        """
        left_vel = (adv + self.semi_width * rot) / self.radius
        right_vel = (adv - self.semi_width * rot) / self.radius
        self.back_left_wheel.set_joint_target_velocity(left_vel)
        self.back_right_wheel.set_joint_target_velocity(right_vel)
        self.front_left_wheel.set_joint_target_velocity(left_vel)
        self.front_right_wheel.set_joint_target_velocity(right_vel)
        return left_vel, right_vel

    ###########################################
    ### ROBOT POSE get and publish robot position
    ###########################################
    def read_robot_pose(self):
        """
        Reads the robot's full pose from a file and updates the robot's full pose
        struct in memory.

        """
        slam_0 = Shape("slam_0")
        pose = slam_0.get_position()
        rot = slam_0.get_orientation()
        linear_vel, ang_vel = slam_0.get_velocity()

        isMoving = np.abs(linear_vel[0]) > 0.01 or np.abs(linear_vel[1]) > 0.01 or np.abs(ang_vel[2]) > 0.01
        self.bState = RoboCompGenericBase.TBaseState(x=pose[0] * 1000,
                                                     z=pose[1] * 1000,
                                                     alpha=rot[2]- np.pi,
                                                     advVx=linear_vel[0] * 1000,
                                                     advVz=linear_vel[1] * 1000,
                                                     rotV=ang_vel[2],
                                                     isMoving=isMoving)

        # self.tm.add_transform("world", "robot", pytr.transform_from(pyrot.active_matrix_from_intrinsic_euler_xyz
        #                                                             ([rot[0], rot[1], rot[2]-np.pi]),
        #                                                             [pose[0]*1000.0, pose[1]*1000.0, pose[2]*1000.0]
        #                                                             ))
        #
        # t = self.tm.get_transform("origin", "robot")
        # angles = pyrot.extrinsic_euler_xyz_from_active_matrix(t[0:3, 0:3])

        self.robot_full_pose_write.x = pose[0] * 1000
        self.robot_full_pose_write.y = pose[1] * 1000
        self.robot_full_pose_write.z = pose[2] * 1000
        self.robot_full_pose_write.rx = rot[0]
        self.robot_full_pose_write.ry = rot[1]
        self.robot_full_pose_write.rz = rot[2] - np.pi
        self.robot_full_pose_write.vx = linear_vel[0] * 1000.0
        self.robot_full_pose_write.vy = linear_vel[1] * 1000.0
        self.robot_full_pose_write.vz = linear_vel[2] * 1000.0
        self.robot_full_pose_write.vrx = ang_vel[0]
        self.robot_full_pose_write.vry = ang_vel[1]
        self.robot_full_pose_write.vrz = ang_vel[2]

        # swap
        self.mutex.acquire()
        self.robot_full_pose_write, self.robot_full_pose_read = self.robot_full_pose_read, self.robot_full_pose_write
        self.mutex.release()


    ###########################################
    ### MOVE ROBOT from Omnirobot interface
    ###########################################
    def move_robot(self):

        """
        Converts the base speed to motor speeds and sends them to the robot, updates
        the robot's speed value to none if it is moving and the speed values are
        (0,0,0), and prints the velocities sent to the robot.

        """
        if self.speed_robot: #!= self.speed_robot_ant:  # or (isMoving and self.speed_robot == [0,0,0]):
            self.convert_base_speed_to_motors_speed(self.speed_robot[0], self.speed_robot[1])
            # print("Velocities sent to robot:", self.speed_robot)
            #self.speed_robot_ant = self.speed_robot
            self.speed_robot = None

    ##################################################################################
    # SUBSCRIPTION to sendData method from JoystickAdapter interface
    ###################################################################################
    def JoystickAdapter_sendData(self, data):
        self.joystick_newdata = [data, time.time()]

    ##################################################################################
    #                       Methods for CameraRGBDSimple
    # ===============================================================================
    #
    # getAll
    #
    def CameraRGBDSimple_getAll(self, camera):
        """
        Retrieves and returns an instance of `RoboCompCameraRGBDSimple` based on
        the given `camera` parameter, if such a camera exists in the list of
        available cameras (`self.cameras_read`). If no matching camera is found,
        an `HardwareFailedException` is raised with a custom message providing the
        camera name.

        Args:
            camera (str): 3D camera to be read from, and if it exists in the
                dictionary `self.cameras_read`, its RGB and depth values are
                returned as a RoboCompCameraRGBDSimple object, otherwise an exception
                is raised.

        Returns:
            instance of the `RoboCompCameraRGBDSimple.TRGBD` class: a `TRGBD`
            object containing the RGB and depth information of a single camera,
            or an `HardwareFailedException` message if no camera was found with
            the given name.
            
            		- `RoboCompCameraRGBDSimple.TRGBD`: This is the return value of the
            function when both RGB and depth images are available for the specified
            camera. It is a tuple containing the RGB image and the depth image as
            separate elements.
            		- `e`: This is an exception object that is raised if no camera with
            the specified name was found. The `what` attribute of the exception
            provides the error message.

        """
        if camera in self.cameras_read.keys():
            return RoboCompCameraRGBDSimple.TRGBD(self.cameras_read[camera]["rgb"], self.cameras_read[camera]["depth"])
        else:
            e = RoboCompCameraRGBDSimple.HardwareFailedException()
            e.what = "No camera found with this name: " + camera
            raise e

    #
    # getDepth
    #
    def CameraRGBDSimple_getDepth(self, camera):
        """
        Checks if a camera with the given name exists in a list of available
        cameras, and returns the depth value associated with that camera if found.
        If not found, it raises an exception with a specific message.

        Args:
            camera (str): name of a camera to check if it exists in the list of
                available cameras stored in the `self.cameras_read` attribute, and
                if not, raises an exception with the reason.

        Returns:
            int: a depth value for a specified camera, or an `HardwareFailedException`
            object if no camera with the specified name is found.

        """
        if camera in self.cameras_read.keys():
            return self.cameras_read[camera]["depth"]
        else:
            e = RoboCompCameraRGBDSimple.HardwareFailedException()
            e.what = "No camera found with this name: " + camera
            raise e

    #
    # getImage
    #
    def CameraRGBDSimple_getImage(self, camera):
        """
        Retrieves an RGB image from a specified camera, returning the image if the
        camera is found in the list of read cameras, or raising `HardwareFailedException`
        otherwise.

        Args:
            camera (str): name of the camera for which the RGB value is being
                retrieved, and it is used to determine whether the camera exists
                in the `self.cameras_read` dictionary and return its RGB value if
                found, or raise an exception otherwise.

        Returns:
            rgb` value: an RGB image of the specified camera or a HardwareFailedException
            message if no camera with that name is found.
            
            		- `rgb`: This is the image data in RGB format.

        """
        if camera in self.cameras_read.keys():
            return self.cameras_read[camera]["rgb"]
        else:
            e = RoboCompCameraRGBDSimple.HardwareFailedException()
            e.what = "No camera found with this name: " + camera
            raise e

    ##############################################
    ## Omnibase
    #############################################

    #
    # correctOdometer
    #
    def DifferentialRobot_correctOdometer(self, x, z, alpha):
        pass

    #
    # getBasePose
    #
    def DifferentialRobot_getBasePose(self):
        #
        # implementCODE
        #
        """
        Returns an array of three values: `x`, `z`, and `alpha`. These values
        represent the position and orientation of a robot's base, as represented
        by its `bState` attribute.

        Returns:
            int: a list of three values: `x`, `z`, and `alpha`.

        """
        x = self.bState.x
        z = self.bState.z
        alpha = self.bState.alpha
        return [x, z, alpha]

    #
    # getBaseState
    #
    def DifferentialRobot_getBaseState(self):
        return self.bState

    #
    # resetOdometer
    #
    def DifferentialRobot_resetOdometer(self):
        pass

    #
    # setOdometer
    #
    def DifferentialRobot_setOdometer(self, state):
        pass

    #
    # setOdometerPose
    #
    def DifferentialRobot_setOdometerPose(self, x, z, alpha):
        pass

    #
    # setSpeedBase
    #
    def DifferentialRobot_setSpeedBase(self, advz, rot):
        self.speed_robot = [advz, rot]

    #
    # stopBase
    #
    def DifferentialRobot_stopBase(self):
        pass

    # ===================================================================
    # CoppeliaUtils
    # ===================================================================
    def CoppeliaUtils_addOrModifyDummy(self, type, name, pose):
        """
        Modifies or creates a dummy object in CoppeliaSim based on its name and
        type. It sets the position, orientation, and parent frame object of the dummy.

        Args:
            type (`RoboCompCoppeliaUtils.TargetTypes` value.): target type of the
                Dummy object being created, which determines the specific action
                to take on the Dummy, such as setting position and orientation
                based on the given pose values.
                
                		- `RoboCompCoppeliaUtils.TargetTypes.Info`: No further explanation
                is provided as it is not a property or attribute of `type`.
                		- `RoboCompCoppeliaUtils.TargetTypes.Hand`: No further explanation
                is provided as it is not a property or attribute of `type`.
                		- `RoboCompCoppeliaUtils.TargetTypes.HeadCamera`: No further
                explanation is provided as it is not a property or attribute of `type`.
            name (str): 3D model name that the Dummy instance will be associated
                with.
            pose (3D vector representing position and orientation values.): 3D
                position and orientation of the dummy in a robot's workspace, which
                is used to set the position and orientation of the dummy in the
                Coppelia simulation.
                
                		- `x`: The x-coordinate of the pose.
                		- `y`: The y-coordinate of the pose.
                		- `z`: The z-coordinate of the pose.
                		- `rx`, `ry`, and `rz`: The roll, pitch, and yaw angles of the
                orientation.
                
                	The function creates a new dummy object if `name` does not already
                exist in the Coppelia framework, or modifies an existing dummy
                object with the provided pose information if it already exists.

        """
        if not Dummy.exists(name):
            dummy = Dummy.create(0.1)
            # one color for each type of dummy
            if type == RoboCompCoppeliaUtils.TargetTypes.Info:
                pass
            if type == RoboCompCoppeliaUtils.TargetTypes.Hand:
                pass
            if type == RoboCompCoppeliaUtils.TargetTypes.HeadCamera:
                pass
            dummy.set_name(name)
        else:
            dummy = Dummy(name)
            parent_frame_object = None
            if type == RoboCompCoppeliaUtils.TargetTypes.HeadCamera:
                parent_frame_object = Dummy("viriato_head_camera_pan_tilt")
            # print("Coppelia ", name, pose.x/1000, pose.y/1000, pose.z/1000)
            dummy.set_position([pose.x / 1000., pose.y / 1000., pose.z / 1000.], parent_frame_object)
            dummy.set_orientation([pose.rx, pose.ry, pose.rz], parent_frame_object)

    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of getFullPose method from FullPoseEstimation interface
    #
    def FullPoseEstimation_getFullPoseEuler(self):
        return self.robot_full_pose_read

    def FullPoseEstimation_getFullPoseMatrix(self):
        """
        Retrieves a full pose matrix from a given transformation matrix and returns
        the estimated full pose matrix.

        Returns:
            FullPoseMatrix: a full pose matrix representing the robot's position
            and orientation in the world.
            
            		- `m00`, `m01`, `m02`, and `m03`: These represent the x, y, z, and
            roll angles of the robot's base link.
            		- `m10`, `m11`, `m12`, and `m13`: These represent the x, y, z, and
            pitch angles of the robot's end effector link.
            		- `m20`, `m21`, `m22`, and `m23`: These represent the x, y, z, and
            yaw angles of the robot's arm link.
            		- `m30`, `m31`, `m32`, and `m33`: These represent the x, y, z, and
            roll angles of the robot's hand link.
            
            	Overall, this function returns a 4x4 matrix representing the full
            pose of the robot in its environment. The properties of this matrix
            are used to calculate various aspects of the robot's position and
            orientation, such as its distance from obstacles, its stability, and
            its ability to perform tasks.

        """
        t = self.tm.get_transform("origin", "robot")
        m = RoboCompFullPoseEstimation.FullPoseMatrix()
        m.m00 = t[0][0]
        m.m01 = t[0][1]
        m.m02 = t[0][2]
        m.m03 = t[0][3]
        m.m10 = t[1][0]
        m.m11 = t[1][1]
        m.m12 = t[1][2]
        m.m13 = t[1][3]
        m.m20 = t[2][0]
        m.m21 = t[2][1]
        m.m22 = t[2][2]
        m.m23 = t[2][3]
        m.m30 = t[3][0]
        m.m31 = t[3][1]
        m.m32 = t[3][2]
        m.m33 = t[3][3]
        return m

    #
    # IMPLEMENTATION of setInitialPose method from FullPoseEstimation interface
    #
    def FullPoseEstimation_setInitialPose(self, x, y, z, rx, ry, rz):

        # should move robot in Coppelia to designated pose
        """
        Adds a transformation to the `TM` object, specified by the input arguments
        "origin" and "world". The transformation is created from an intrinsic Euler
        angle representation and applies to the provided output coordinates.

        Args:
            x (float): 2D world coordinates of the origin point relative to the
                camera's perspective, which is used to transform the origin point
                from intrinsic Euler angles to world coordinates.
            y (int): 2D point in world coordinates where the transformation should
                be applied.
            z (float): 3D coordinates of the transformation origin in world space.
            rx (float): x-axis rotation angle of the transformation matrix.
            ry (float): 3rd rotation axis in the Euler angular velocity representation,
                which is applied to the provided 4D vector to transform it from
                intrinsic to world coordinates.
            rz (number.): 3rd rotational axis about the `origin`, which is used
                to transform the world position `x,y,z` to the local coordinates
                of the target matrix `pyrot.active_matrix_from_intrinsic_euler_xyz()`
                .
                
                		- `ry`: The roll angle of the object in radians.
                		- `rx`: The pitch angle of the object in radians.
                		- `rz`: The yaw angle of the object in radians.

        """
        self.tm.add_transform("origin", "world",
                               pytr.transform_from(pyrot.active_matrix_from_intrinsic_euler_xyz([rx, ry, rz]), [x, y, z])
        )

    #
    # IMPLEMENTATION of getAllSensorDistances method from Ultrasound interface
    #
    def Ultrasound_getAllSensorDistances(self):
        """
        Retrieves and returns an instance of the `SensorsState` class containing
        the latest ultrasound sensor distances readings.

        Returns:
            robocup_ultrasound_sensors_state_t: a sensors state object containing
            the distances of all ultrasound sensors.
            
            		- `ret`: The return value is an instance of the `RoboCompUltrasound.SensorsState`
            class, which contains information about the current state of the
            ultrasound sensors.
            
            	Note that the structure and contents of the `SensorsState` class may
            vary depending on the specific implementation and requirements of the
            RoboComp Ultrasound module. Therefore, it is important to consult the
            documentation or API references provided with the module for more
            detailed information on the possible attributes and methods available
            in the class.

        """
        ret = RoboCompUltrasound.SensorsState()
        #
        # write your CODE here
        #
        return ret

    #
    # IMPLEMENTATION of getAllSensorParams method from Ultrasound interface
    #
    def Ultrasound_getAllSensorParams(self):
        """
        Returns a list of sensor parameters for an ultrasound application.

        Returns:
            list: a list of sensor parameters for an ultrasound application.

        """
        ret = RoboCompUltrasound.SensorParamsList()
        #
        # write your CODE here
        #
        return ret

    #
    # IMPLEMENTATION of getBusParams method from Ultrasound interface
    #
    def Ultrasound_getBusParams(self):
        """
        Retrieves the bus parameters for an ultrasound imaging device using the
        RoboCompUltrasound library.

        Returns:
            instance of the `RoboCompUltrasound.BusParams` class: a RoboComp
            Ultrasound bus parameters structure.
            
            		- `ret`: A `RoboCompUltrasound.BusParams` object, which contains
            information about the ultrasound bus parameters.
            
            	The attributes of this object include:
            
            		- `bus_type`: The type of bus used for the ultrasound data transmission
            (e.g., serial, parallel, etc.).
            		- `bus_speed`: The speed of the ultrasound bus in bits per second.
            		- `max_payload`: The maximum payload size for the ultrasound bus.
            		- `min_interval`: The minimum interval between consecutive samples
            in milliseconds.
            		- `samples_per_frame`: The number of samples per frame in the
            ultrasound image.
            		- `frames_per_second`: The number of frames per second in the
            ultrasound video.

        """
        ret = RoboCompUltrasound.BusParams()
        #
        # write your CODE here
        #
        return ret

    #
    # IMPLEMENTATION of getSensorDistance method from Ultrasound interface
    #
    def Ultrasound_getSensorDistance(self, sensor):
        """
        Calculates and returns an estimate of the distance between a sensor and
        an object, based on ultrasonic waves emitted from the sensor.

        Args:
            sensor (int): 16-bit sensor value returned by the previous `int()`
                call, which is then used to compute and return the final result.

        Returns:
            int: an integer value representing the distance from the sensor to the
            object being scanned.

        """
        ret = int()
        #
        # write your CODE here
        #
        return ret

    #
    # IMPLEMENTATION of getSensorParams method from Ultrasound interface
    #
    def Ultrasound_getSensorParams(self, sensor):
        """
        Sets the default values for an ultrasonic sensor's parameters using RoboComp
        Ultrasound module.

        Args:
            sensor (`UltrasoundSensorParam` object reference, as the return value
                of the function `RoboCompUltrasound.SensorParams()` indicates.):
                ultrasound sensor settings used for the RoboComp Ultrasound module.
                
                		- `type`: The type of sensor, which can be `ROBOCOMP_ULTRASOUND`
                for an ultrasound sensor.
                		- `frequency`: The operating frequency of the sensor in Hertz (Hz).
                		- `resolution`: The spatial resolution of the sensor in pixels
                or other appropriate units.
                		- `samples_per_frame`: The number of samples per frame captured
                by the sensor.
                		- `frames_per_second`: The frames per second rate at which the
                sensor captures data.
                		- `channel_count`: The number of channels or input points on the
                sensor.
                		- `data_format`: The data format of the sensor, such as Grayscale
                or RGB.

        Returns:
            instance of the RoboCompUltrasound.SensorParams class, which can be
            used to represent the parameter values of an ultrasound sensor in
            various robotic applications: a structure containing parameters related
            to the ultrasound sensor.
            
            		- `RoboCompUltrasound.SensorParams`: This is a class that contains
            various attributes related to ultrasound sensors. These attributes include:
            		+ `sensor_type`: A string that specifies the type of sensor, such
            as "Ultrasonic" or "Lidar".
            		+ `sensor_model`: A string that represents the specific model of the
            sensor, such as "VUI-100" or "L4D-SST".
            		+ `sensor_version`: An integer that represents the version of the
            sensor software.
            		+ `accelerometer_range`: An integer that represents the range of
            accelerations that the sensor can measure, in units of acceleration
            (e.g., g-forces).
            		+ `gyroscope_range`: An integer that represents the range of angular
            velocities that the sensor can measure, in units of radians per second
            (e.g., degrees per second).
            		+ `resolution`: An integer that represents the resolution of the
            sensor in pixels or other units, depending on the type of sensor.
            		+ `frames_per_second`: An integer that represents the number of
            frames per second that the sensor can capture.
            
            	These properties provide important information about the capabilities
            and limitations of the ultrasound sensor, and can be used to optimize
            its use in various applications.

        """
        ret = RoboCompUltrasound.SensorParams()
        #
        # write your CODE here
        #
        return ret

    # ===================================================================
    # ===================================================================
    #
    # IMPLEMENTATION of getRSSIState method from RSSIStatus interface
    #
    def RSSIStatus_getRSSIState(self):
        """
        Returns an object with an updated percentage value for RSSI status, set
        to 100%.

        Returns:
            TRSSI` value: a struct that contains the current percentage of RSSI
            signal strength.
            
            		- `percentage`: A floating-point number representing the percentage
            of signal strength. (type: `float`)

        """
        ret = RoboCompRSSIStatus.TRSSI()
        ret.percentage = 100;
        return ret

    #
    # IMPLEMENTATION of getBatteryState method from BatteryStatus interface
    #
    def BatteryStatus_getBatteryState(self):
        """
        Sets the percentage of a battery to 100, effectively indicating that the
        battery is fully charged.

        Returns:
            instance of `RoboCompBatteryStatus: a battery status object representing
            the full charge level of the RoboComp battery.
            
            		- percentage: A floating-point number representing the battery's
            current level, between 0 and 100, where 0 indicates an empty battery
            and 100 represents a fully charged battery.

        """
        ret = RoboCompBatteryStatus.TBattery()
        ret.percentage = 100
        return ret
    #

# =============== Methods for Component Implements ==================
    # ===================================================================
    #
    # IMPLEMENTATION of getLaserAndBStateData method from Laser interface
    #
    def Laser_getLaserAndBStateData(self):
        """
        Retrieves and combines data from two sources: a laser sensor
        (`RoboCompLaser.TLaserData`) and a base state (`RoboCompGenericBase.TBaseState`).
        The combined data is returned as a tuple of two variables.

        Returns:
            (RoboCompLaser.TLaserData, RoboCompGenericBase.TBaseState: a tuple
            containing the laser data and the base state data.
            
            	Ret (RoboCompLaser.TLaserData): It represents the laser data containing
            various attributes such as laser class, name, and serial number.
            
            	bState (RoboCompGenericBase.TBaseState): It contains information about
            the base state of the system, which may not be directly related to the
            laser data but can provide additional context for processing or analyzing
            the output.

        """
        ret = RoboCompLaser.TLaserData()
        bState = RoboCompGenericBase.TBaseState()
        return [ret, bState]
    #
    # IMPLEMENTATION of getLaserConfData method from Laser interface
    #
    def Laser_getLaserConfData(self):
        ret = RoboCompLaser.LaserConfData()
        return ret
    #
    # IMPLEMENTATION of getLaserData method from Laser interface
    #
    def Laser_getLaserData(self):
        return self.ldata_read
    # ===================================================================
    # ===================================================================
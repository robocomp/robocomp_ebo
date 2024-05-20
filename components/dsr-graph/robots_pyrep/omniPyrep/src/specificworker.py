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
import os, time, queue
from bisect import bisect_left
from os.path import dirname, join, abspath
from pyrep import PyRep
#from pyrep.robots.mobiles.viriato import Viriato
#from pyrep.robots.mobiles.viriato import Viriato
from pyrep.robots.mobiles.youbot import YouBot
from pyrep.objects.vision_sensor import VisionSensor
from pyrep.objects.dummy import Dummy
from pyrep.objects.shape import Shape
from pyrep.objects.shape import Object
from pyrep.objects.joint import Joint

import numpy as np
import numpy_indexed as npi
from itertools import zip_longest
import cv2
import queue

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map):
        super(SpecificWorker, self).__init__(proxy_map)
       
    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        
        """
        Sets the parameters for the Omnidrone robot simulation, including the scene
        file, robot model, wheel radius, distance and axes length, and rotation
        factor. It also defines vision sensors and creates lists to store new data
        from the joystick and robot speed.

        Args:
            params (list): 45 pre-defined parameters required for the OmniRobot,
                YouBot, and Viriato robots, which are assigned values to facilitate
                initialization and object creation.

        """
        SCENE_FILE = '../../etc/omnirobot.ttt'
        #SCENE_FILE = '../etc/viriato_dwa.ttt'

        self.pr = PyRep()
        self.pr.launch(SCENE_FILE, headless=False)
        self.pr.start()
        
        #self.robot = Viriato()
        self.robot = YouBot()
        self.robot_object = Shape("youBot")

        #self.ViriatoBase_WheelRadius = 76.2  #mm real robot
        self.ViriatoBase_WheelRadius = 44  # mm coppelia
        self.ViriatoBase_DistAxes = 380.
        self.ViriatoBase_AxesLength = 422.
        self.ViriatoBase_Rotation_Factor = 8.1  # it should be (DistAxes + AxesLength) / 2

        # Each laser is composed of two cameras. They are converted into a 360 virtual laser
        self.hokuyo_base_front_left = VisionSensor("hokuyo_base_front_left")
        self.hokuyo_base_front_right = VisionSensor("hokuyo_base_front_right")
        self.hokuyo_base_back_right = VisionSensor("hokuyo_base_back_right")
        self.hokuyo_base_back_left = VisionSensor("hokuyo_base_back_left")
        self.ldata = []

        self.joystick_newdata = []
        self.speed_robot = []
        self.speed_robot_ant = []
        self.last_received_data_time = 0

    #@QtCore.Slot()
    def compute(self):
        """
        Continuously runs a simulation of a robotic arm's movements based on sensor
        data, sleeping for <0.05 seconds between iterations and logging the number
        of iterations per second.

        """
        cont = 0
        start = time.time()
        while True:
            self.pr.step()
            self.read_laser()
            self.read_joystick()
            self.read_robot_pose()
            self.move_robot()

            elapsed = time.time()-start
            if elapsed < 0.05:
                time.sleep(0.05-elapsed)
            cont += 1
            if elapsed > 1:
                print("Freq -> ", cont)
                cont = 0
                start = time.time()

    ###########################################
    ### LASER get and publish laser data
    ###########################################
    def read_laser(self):
        """
        Computes omni-laser data using input from sensors and pushes it to a Proxy
        Publisher.

        """
        self.ldata = self.compute_omni_laser([self.hokuyo_base_front_right,
                                         self.hokuyo_base_front_left,
                                         self.hokuyo_base_back_left,
                                         self.hokuyo_base_back_right
                                         ], self.robot)
        try:
            self.laserpub_proxy.pushLaserData(self.ldata)
        except Ice.Exception as e:
            print(e)

    ###########################################
    ### JOYSITCK read and move the robot
    ###########################################
    def read_joystick(self):
        """
        Reads the joystick data and updates the robot's angular velocities based
        on the elapsed time since the last received data. If the elapsed time is
        between 2-3 seconds, the function sets the base angular velocities to zero.

        """
        if self.joystick_newdata: #and (time.time() - self.joystick_newdata[1]) > 0.1:
            self.update_joystick(self.joystick_newdata[0])
            self.joystick_newdata = None
            self.last_received_data_time = time.time()
        else:
            elapsed = time.time() - self.last_received_data_time
            if elapsed > 2 and elapsed < 3:
                self.robot.set_base_angular_velocites([0, 0, 0])


    ###########################################
    ### ROBOT POSE get and publish robot position
    ###########################################
    def read_robot_pose(self):
        """
        Calculates and returns the base state of a RoboComp robot based on its
        current 2D pose and velocity information, and pushes it to the robot's
        omnicon controller.

        """
        pose = self.robot.get_2d_pose()
        linear_vel, ang_vel = self.robot_object.get_velocity()
        # print("Veld:", linear_vel, ang_vel)
        try:
            isMoving = np.abs(linear_vel[0]) > 0.01 or np.abs(linear_vel[1]) > 0.01 or np.abs(ang_vel[2]) > 0.01
            self.bState = RoboCompGenericBase.TBaseState(x=pose[0] * 1000,
                                                         z=pose[1] * 1000,
                                                         alpha=pose[2],
                                                         advVx=linear_vel[0] * 1000,
                                                         advVz=linear_vel[1] * 1000,
                                                         rotV=ang_vel[2],
                                                         isMoving=isMoving)
            self.omnirobotpub_proxy.pushBaseState(self.bState)
        except Ice.Exception as e:
            print(e)

    ###########################################
    ### MOVE ROBOT from Omnirobot interface
    ###########################################
    def move_robot(self):

        """
        Updates the angular velocity of a robot based on the movement of an Ant
        and its current speed.

        """
        if self.speed_robot != self.speed_robot_ant:  # or (isMoving and self.speed_robot == [0,0,0]):
            self.robot.set_base_angular_velocites(self.speed_robot)
        #print("Velocities sent to robot:", self.speed_robot)
            self.speed_robot_ant = self.speed_robot

    ########################################
    ## General laser computation
    ########################################
    def compute_omni_laser(self, lasers, robot):
        """
        Computes and returns a list of RoboComp Laser objects representing a
        360-degree angle coverage for an omnidirectional laser scanner. The function
        processes the depth images from each laser and computes the corresponding
        position and distance values in polar coordinates.

        Args:
            lasers (`RoboCompLaser` object(s).): 2D laser measurements taken by a
                robot with multiple laser scanners, which are then processed to
                generate a 360-degree polar representation of the robot's surroundings.
                
                		- `get_resolution()`: returns a tuple containing the resolution
                in x and y directions
                		- `get_perspective_angle()`: returns the perspective angle of
                the laser in radians
                		- `capture_depth()`: captures depth images using the laser
                		- `get_matrix()`: retrieves the intrinsic and extrinsic matrix
                of the laser
                		- `T`: converts a 2D array to a 1D array with shape `(N, 4)`
                where N is the number of rows in the input depth image
                		- `arctan2()`: calculates the arctangent of two elements in a vector
                		- `linalg.norm()`: computes the Euclidean norm of a vector
                		- `TData`: represents a 3D point with an RGB value representing
                the intensity of each channel
                
                	In summary, `lasers` is a list of laser objects with various
                properties and attributes, including resolution, perspective angle,
                matrix, etc.
            robot (3D Robot object.): 4x4 transformation matrix of the robot's
                orientation and position, which is used to transform the depth
                image coordinates to the robot's origin in homogeneous form.
                
                		- `m`: a 4D array representing the matrix of the robot's geometry,
                with dimensions `(4, 4)`
                		- `in_meters`: a boolean value indicating whether the depth image
                should be converted to meters or not
                		- `lasers`: an array of `Laser` objects, each representing a
                laser scanner mounted on the robot
                		- `semiwidth`: a scalar value representing the resolution of the
                laser scanners in x-direction
                		- `semiangle`: a scalar value representing the perspective angle
                of the laser scanners in radians
                		- `focal`: a scalar value representing the focal length of the
                laser scanners
                		- `data`: an array of depth images, each with shape `(2, 2)`
                		- `imat`: a 4D array representing the image matrix of the robot's
                coordinate system, with dimensions `(4, 4)`

        Returns:
            list: a list of 360 angular measurements and their corresponding
            distances from the robot's origin, measured using lasers positioned
            at regular intervals around the robot.

        """
        c_data = []
        coor = []
        for laser in lasers:
            semiwidth = laser.get_resolution()[0]/2
            semiangle = np.radians(laser.get_perspective_angle()/2)
            focal = semiwidth/np.tan(semiangle)
            data = laser.capture_depth(in_meters=True)
            m = laser.get_matrix(robot)     # these data should be read first
            imat = np.array([[m[0],m[1],m[2],m[3]],[m[4],m[5],m[6],m[7]],[m[8],m[9],m[10],m[11]],[0,0,0,1]])

            for i,d in enumerate(data.T):
                z = d[0]        # min if more than one row in depth image
                vec = np.array([-(i-semiwidth)*z/focal, 0, z, 1])
                res = imat.dot(vec)[:3]       # translate to robot's origin, homogeneous
                c_data.append([np.arctan2(res[0], res[1]), np.linalg.norm(res)])  # add to list in polar coordinates

        # create 360 polar rep
        c_data_np = np.asarray(c_data)
        angles = np.linspace(-np.pi, np.pi, 360)                          # create regular angular values
        positions = np.searchsorted(angles, c_data_np[:,0])               # list of closest position for each laser meas
        ldata = [RoboCompLaser.TData(a, 0) for a in angles]               # create empty 360 angle array
        pos , medians  = npi.group_by(positions).median(c_data_np[:,1])   # group by repeated positions
        for p, m in zip_longest(pos, medians):                            # fill the angles with measures
            ldata[p].dist = int(m*1000)   # to millimeters
        if ldata[0] == 0:
            ldata[0] = 200       #half robot width
        for i in range(0, len(ldata)):
            if ldata[i].dist == 0:
                ldata[i].dist = ldata[i-1].dist
        #ldata[0].dist = ldata[len(data)-1].dist

        return ldata
    
    def update_joystick(self, datos):
        """
        Updates the angular velocities of a robot based on input values from an
        axis data. It converts base speeds to radians and sets the updated angular
        velocities on the robot object.

        Args:
            datos (1-dimensional numpy array.): 3D robot position data, which
                contains the advanced, rotation, and side information of the robot
                that is used to convert the base speed to radians and set the
                robot's angular velocity.
                
                		- `axes`: An array of dictionaries, where each dictionary
                represents a linear or angular velocity component of the robot.
                The keys of each dictionary are "advance", "rotate", and "side",
                respectively.
                		- `value`: The value of the corresponding velocity component for
                the robot.

        """
        adv = 0.0
        rot = 0.0
        side = 0.0
        #linear_vel, ang_vel = self.robot_object.get_velocity()
        for x in datos.axes:
            if x.name == "advance":
                adv = x.value if np.abs(x.value) > 1 else 0
            if x.name == "rotate":
                rot = x.value if np.abs(x.value) > 0.01 else 0
            if x.name == "side":
                side = x.value if np.abs(x.value) > 1 else 0

        converted = self.convert_base_speed_to_radians(adv, side, rot)
        print("Joystick ", [adv, side, rot], converted)
        self.robot.set_base_angular_velocites(converted)

    def convert_base_speed_to_radians(self, adv, side, rot):
        # rot has to be neg so neg rot speeds go clock wise. It is probably a sign in Pyrep forward kinematics
        return [adv / self.ViriatoBase_WheelRadius, side / self.ViriatoBase_WheelRadius, rot * self.ViriatoBase_Rotation_Factor]


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
        return RoboCompCameraRGBDSimple.TRGBD(self.cameras[camera]["rgb"], self.cameras[camera]["depth"])

    #
    # getDepth
    #
    def CameraRGBDSimple_getDepth(self, camera):
        return self.cameras[camera]["depth"]
    #
    # getImage
    #
    def CameraRGBDSimple_getImage(self, camera):
        return self.cameras[camera]["rgb"]

    #######################################################
    #### Laser
    #######################################################

    #
    # getLaserAndBStateData
    #
    def Laser_getLaserAndBStateData(self):
        bState = RoboCompGenericBase.TBaseState()
        return self.ldata, bState

    #
    # getLaserConfData
    #
    def Laser_getLaserConfData(self):
        ret = RoboCompLaser.LaserConfData()
        return ret

    #
    # getLaserData
    #
    def Laser_getLaserData(self):
        return self.ldata

    ##############################################
    ## Omnibase
    #############################################

    #
    # correctOdometer
    #
    def OmniRobot_correctOdometer(self, x, z, alpha):
        pass

    #
    # getBasePose
    #
    def OmniRobot_getBasePose(self):
        #
        # implementCODE
        #
        """
        Retrieves the robot's base pose (x,z,α) based on the current state of the
        robot.

        Returns:
            float: an array containing the robot's x, z, and alpha positions.

        """
        x = self.bState.x
        z = self.bState.z
        alpha = self.bState.alpha
        return [x, z, alpha]

    #
    # getBaseState
    #
    def OmniRobot_getBaseState(self):
        return self.bState

    #
    # resetOdometer
    #
    def OmniRobot_resetOdometer(self):
        pass

    #
    # setOdometer
    #
    def OmniRobot_setOdometer(self, state):
        pass

    #
    # setOdometerPose
    #
    def OmniRobot_setOdometerPose(self, x, z, alpha):
        pass

    #
    # setSpeedBase
    #
    def OmniRobot_setSpeedBase(self, advx, advz, rot):
        self.speed_robot = self.convert_base_speed_to_radians(advz, advx, rot)

    #
    # stopBase
    #
    def OmniRobot_stopBase(self):
        pass

    # ===================================================================
    # CoppeliaUtils
    # ===================================================================
    def CoppeliaUtils_addOrModifyDummy(self, type, name, pose):
        """
        Modifies or creates a Coppelia dummy based on a given name, type, and pose.
        It sets the dummy's position, orientation, and parent frame object.

        Args:
            type (int): 1 of 3 possible types of dummy that is being created or
                referenced, and its value determines which set of properties are
                set on the dummy.
            name (str): 3D object name that is being assigned to the `dummy` variable.
            pose (3D homogeneous transformation matrix.): 3D position and orientation
                of the robot's end effector in world coordinates, which is used
                to set the position and orientation of the dummy object in CoppeliaSim.
                
                		- `x`, `y`, and `z` represent the 3D position of the dummy in meters.
                		- `rx`, `ry`, and `rz` represent the 3D orientation of the dummy
                in radians.
                		- The `type` parameter indicates the type of dummy being added
                or modified, which can be one of the following values:
                `RoboCompCoppeliaUtils.TargetTypes.Info`, `RoboCompCoppeliaUtils.TargetTypes.Hand`,
                or `RoboCompCoppeliaUtils.TargetTypes.HeadCamera`.
                		- The `name` parameter represents the name of the dummy being
                added or modified.

        """
        if not Dummy.exists(name):
            dummy = Dummy.create(0.1)
            # one color for each type of dummy
            if type==RoboCompCoppeliaUtils.TargetTypes.Info:
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
            #print("Coppelia ", name, pose.x/1000, pose.y/1000, pose.z/1000)
            dummy.set_position([pose.x / 1000., pose.y / 1000., pose.z / 1000.], parent_frame_object)
            dummy.set_orientation([pose.rx, pose.ry, pose.rz], parent_frame_object)


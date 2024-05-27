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

import sys, Ice, os

ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except KeyError:
    print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
    ROBOCOMP = '/opt/robocomp'

Ice.loadSlice("-I ./src/ --all ./src/CommonBehavior.ice")
import RoboCompCommonBehavior

Ice.loadSlice("-I ./src/ --all ./src/CameraRGBDSimple.ice")
import RoboCompCameraRGBDSimple 
Ice.loadSlice("-I ./src/ --all ./src/CameraRGBDSimplePub.ice")
import RoboCompCameraRGBDSimplePub 
Ice.loadSlice("-I ./src/ --all ./src/GenericBase.ice")
import RoboCompGenericBase 
Ice.loadSlice("-I ./src/ --all ./src/JoystickAdapter.ice")
import RoboCompJoystickAdapter 
Ice.loadSlice("-I ./src/ --all ./src/Laser.ice")
import RoboCompLaser 
Ice.loadSlice("-I ./src/ --all ./src/LaserPub.ice")
import RoboCompLaserPub 
Ice.loadSlice("-I ./src/ --all ./src/DifferentialRobot.ice")
import RoboCompDifferentialRobot
Ice.loadSlice("-I ./src/ --all ./src/CoppeliaUtils.ice")
import RoboCompCoppeliaUtils
Ice.loadSlice("-I ./src/ --all ./src/FullPoseEstimation.ice")
import RoboCompFullPoseEstimation
Ice.loadSlice("-I ./src/ --all ./src/Ultrasound.ice")
import RoboCompUltrasound
Ice.loadSlice("-I ./src/ --all ./src/BatteryStatus.ice")
import RoboCompBatteryStatus
Ice.loadSlice("-I ./src/ --all ./src/RSSIStatus.ice")
import RoboCompRSSIStatus


import camerargbdsimpleI 
import laserI 
import differentialrobotI
import joystickadapterI
import coppeliautilsI
import fullposeestimationI
import ultrasoundI
import batterystatusI
import rssistatusI

class GenericWorker():

    #kill = QtCore.Signal()

    def __init__(self, mprx):
        """
        Initializes a `GenericWorker` object by defining instance variables for a
        `CameraRGBDSimplePubPub` and `LaserPubPub` proxies, enabling communication
        between these systems.

        Args:
            mprx (Python Proxy object.): Proxy publication objects of the Camera
                RGBD Simple Pub and Laser Pub, which are used to interact with
                them respectively.
                
                		- `CameraRGBDSimplePubPub`: This property is a `pubsub.PublisherProxy`,
                which represents a Python object that allows interacting with a
                Matterport Proxy service for publishing camera RGB and depth images.
                		- `LaserPubPub`: This property is also a `pubsub.PublisherProxy`,
                representing a Python object that allows interacting with a
                Matterport Proxy service for publishing laser data.

        """
        super(GenericWorker, self).__init__()

        self.camerargbdsimplepub_proxy = mprx["CameraRGBDSimplePubPub"]
        self.laserpub_proxy = mprx["LaserPubPub"]

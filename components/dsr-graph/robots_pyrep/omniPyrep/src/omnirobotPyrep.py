#!/usr/bin/env python3
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

# \mainpage RoboComp::omnirobotPyrep
#
# \section intro_sec Introduction
#
# Some information about the component...
#
# \section interface_sec Interface
#
# Descroption of the interface provided...
#
# \section install_sec Installation
#
# \subsection install1_ssec Software depencences
# Software dependences....
#
# \subsection install2_ssec Compile and install
# How to compile/install the component...
#
# \section guide_sec User guide
#
# \subsection config_ssec Configuration file
#
# <p>
# The configuration file...
# </p>
#
# \subsection execution_ssec Execution
#
# Just: "${PATH_TO_BINARY}/omnirobotPyrep --Ice.Config=${PATH_TO_CONFIG_FILE}"
#
# \subsection running_ssec Once running
#
#
#

import sys, traceback, IceStorm, time, os, copy
from termcolor import colored

# Ctrl+c handling
import signal

#from PySide2 import QtCore

from specificworker import *

class CommonBehaviorI(RoboCompCommonBehavior.CommonBehavior):
    def __init__(self, _handler):
        self.handler = _handler
    def getFreq(self, current = None):
        self.handler.getFreq()
    def setFreq(self, freq, current = None):
        self.handler.setFreq()
    def timeAwake(self, current = None):
        """
        Returns the time a device has been awake.

        Args:
            current (int): current state of the device or system being monitored,
                which is used by the `handler.timeAwake()` method to determine the
                time the device has been awake.

        Returns:
            int: the current amount of time the user has been awake.

        """
        try:
            return self.handler.timeAwake()
        except:
            print('Problem getting timeAwake')
    def killYourSelf(self, current = None):
        self.handler.killYourSelf()
    def getAttrList(self, current = None):
        """
        Retrieves a list of attributes for a given handler object through its
        `handler` attribute.

        Args:
            current (exception object.): current attribute list that should be
                returned by the `handler.getAttrList()` method.
                
                	1/ `handler`: The `handler` attribute represents the Python class
                that was passed in during the deserialization process. It provides
                a means to access methods and other attributes defined within the
                class.
                	2/ `attrList`: This attribute lists the attributes of the current
                object, which can be accessed and manipulated through the ` handler`
                attribute.

        Returns:
            list: a list of attribute names.

        """
        try:
            return self.handler.getAttrList()
        except:
            print('Problem getting getAttrList')
            traceback.print_exc()
            status = 1
            return

#SIGNALS handler
def sigint_handler(*args):
    #QtCore.QCoreApplication.quit()
    pass
    
if __name__ == '__main__':
    #app = QtCore.QCoreApplication(sys.argv)
    params = copy.deepcopy(sys.argv)
    if len(params) > 1:
        if not params[1].startswith('--Ice.Config='):
            params[1] = '--Ice.Config=' + params[1]
    elif len(params) == 1:
        params.append('--Ice.Config=etc/config')
    ic = Ice.initialize(params)
    status = 0
    mprx = {}
    parameters = {}
    for i in ic.getProperties():
        parameters[str(i)] = str(ic.getProperties().getProperty(i))

    # Topic Manager
    proxy = ic.getProperties().getProperty("TopicManager.Proxy")
    obj = ic.stringToProxy(proxy)
    try:
        topicManager = IceStorm.TopicManagerPrx.checkedCast(obj)
    except Ice.ConnectionRefusedException as e:
        print(colored('Cannot connect to rcnode! This must be running to use pub/sub.', 'red'))
        exit(1)

    # Create a proxy to publish a CameraRGBDSimplePub topic
    topic = False
    try:
        topic = topicManager.retrieve("CameraRGBDSimplePub")
    except:
        pass
    while not topic:
        try:
            topic = topicManager.retrieve("CameraRGBDSimplePub")
        except IceStorm.NoSuchTopic:
            try:
                topic = topicManager.create("CameraRGBDSimplePub")
            except:
                print('Another client created the CameraRGBDSimplePub topic? ...')
    pub = topic.getPublisher().ice_oneway()
    camerargbdsimplepubTopic = RoboCompCameraRGBDSimplePub.CameraRGBDSimplePubPrx.uncheckedCast(pub)
    mprx["CameraRGBDSimplePubPub"] = camerargbdsimplepubTopic

    # Create a proxy to publish a LaserPub topic
    topic = False
    try:
        topic = topicManager.retrieve("LaserPub")
    except:
        pass
    while not topic:
        try:
            topic = topicManager.retrieve("LaserPub")
        except IceStorm.NoSuchTopic:
            try:
                topic = topicManager.create("LaserPub")
            except:
                print('Another client created the LaserPub topic? ...')
    pub = topic.getPublisher().ice_oneway()
    laserpubTopic = RoboCompLaserPub.LaserPubPrx.uncheckedCast(pub)
    mprx["LaserPubPub"] = laserpubTopic

    # Create a proxy to publish a OmniRobotPub topic
    topic = False
    try:
        topic = topicManager.retrieve("OmniRobotPub")
    except:
        pass
    while not topic:
        try:
            topic = topicManager.retrieve("OmniRobotPub")
        except IceStorm.NoSuchTopic:
            try:
                topic = topicManager.create("OmniRobotPub")
            except:
                print('Another client created the OmniRobotPub topic? ...')
    pub = topic.getPublisher().ice_oneway()
    omnirobotpubTopic = RoboCompOmniRobotPub.OmniRobotPubPrx.uncheckedCast(pub)
    mprx["OmniRobotPubPub"] = omnirobotpubTopic

    # Create a proxy to publish a HumanToDSRPub topic
    topic = False
    try:
        topic = topicManager.retrieve("HumanToDSRPub")
    except:
        pass
    while not topic:
        try:
            topic = topicManager.retrieve("HumanToDSRPub")
        except IceStorm.NoSuchTopic:
            try:
                topic = topicManager.create("HumanToDSRPub")
            except:
                print('Another client created the HumanToDSRPub topic? ...')
    pub = topic.getPublisher().ice_oneway()
    humantodsrpubTopic = RoboCompHumanToDSRPub.HumanToDSRPubPrx.uncheckedCast(pub)
    mprx["HumanToDSRPubPub"] = humantodsrpubTopic

    # Create a proxy to publish a JointMotorPub topic
    topic = False
    try:
        topic = topicManager.retrieve("JointMotorPub")
    except:
        pass
    while not topic:
        try:
            topic = topicManager.retrieve("JointMotorPub")
        except IceStorm.NoSuchTopic:
            try:
                topic = topicManager.create("JointMotorPub")
            except:
                print('Another client created the JointMotorPub topic? ...')
    pub = topic.getPublisher().ice_oneway()
    jointmotorpubTopic = RoboCompJointMotorPub.JointMotorPubPrx.uncheckedCast(pub)
    mprx["JointMotorPubPub"] = jointmotorpubTopic

    # Create a proxy to publish a KinovaArmPub topic
    topic = False
    try:
        topic = topicManager.retrieve("KinovaArmPub")
    except:
        pass
    while not topic:
        try:
            topic = topicManager.retrieve("KinovaArmPub")
        except IceStorm.NoSuchTopic:
            try:
                topic = topicManager.create("KinovaArmPub")
            except:
                print('Another client created the JointMotorPub topic? ...')
    pub = topic.getPublisher().ice_oneway()
    kinovaarmpubTopic = RoboCompKinovaArmPub.KinovaArmPubPrx.uncheckedCast(pub)
    mprx["KinovaArmPubPub"] = kinovaarmpubTopic

    if status == 0:
        worker = SpecificWorker(mprx)
        worker.setParams(parameters)
    else:
        print("Error getting required connections, check config file")
        sys.exit(-1)

    adapter = ic.createObjectAdapter('CameraRGBDSimple')
    adapter.add(camerargbdsimpleI.CameraRGBDSimpleI(worker), ic.stringToIdentity('camerargbdsimple'))
    adapter.activate()

    adapter = ic.createObjectAdapter('Laser')
    adapter.add(laserI.LaserI(worker), ic.stringToIdentity('laser'))
    adapter.activate()

    adapter = ic.createObjectAdapter('OmniRobot')
    adapter.add(omnirobotI.OmniRobotI(worker), ic.stringToIdentity('omnirobot'))
    adapter.activate()

    adapter = ic.createObjectAdapter('CoppeliaUtils')
    adapter.add(coppeliautilsI.CoppeliaUtilsI(worker), ic.stringToIdentity('coppeliautils'))
    adapter.activate()

    JoystickAdapter_adapter = ic.createObjectAdapter("JoystickAdapterTopic")
    joystickadapterI_ = joystickadapterI.JoystickAdapterI(worker)
    joystickadapter_proxy = JoystickAdapter_adapter.addWithUUID(joystickadapterI_).ice_oneway()

    subscribeDone = False
    while not subscribeDone:
        try:
            joystickadapter_topic = topicManager.retrieve("JoystickAdapter")
            subscribeDone = True
        except Ice.Exception as e:
            print("Error. Topic does not exist (creating)")
            time.sleep(1)
            try:
                joystickadapter_topic = topicManager.create("JoystickAdapter")
                subscribeDone = True
            except:
                print("Error. Topic could not be created. Exiting")
                status = 0
    qos = {}
    joystickadapter_topic.subscribeAndGetPublisher(qos, joystickadapter_proxy)
    JoystickAdapter_adapter.activate()

    signal.signal(signal.SIGINT, sigint_handler)
    #app.exec_()
    worker.compute()

    if ic:
        try:
            ic.destroy()
        except:
            traceback.print_exc()
            status = 1

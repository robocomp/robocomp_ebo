#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2024 by YOUR NAME HERE
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
from PySide2 import QtWidgets, QtCore

ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except KeyError:
    print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
    ROBOCOMP = '/opt/robocomp'

Ice.loadSlice("-I ./src/ --all ./src/CommonBehavior.ice")
import RoboCompCommonBehavior




class GenericWorker(QtCore.QObject):

    kill = QtCore.Signal()

    def __init__(self, mprx):
        """
        Initializes an instance of `GenericWorker`. It creates an instance of
        `EmotionalMotorProxy`, acquires a mutex using `QtCore.QMutex.Recursive`,
        sets the period to 30, and starts a timer using ` QtCore.QTimer()`.

        Args:
            mprx ("EmotionalMotorProxy" instance.): "EmotionalMotorProxy" object,
                which is used to access and manipulate the emotional state of an
                agent or actor.
                
                		- `EmotionalMotorProxy`: This property is an instance of
                `QtWidgets.QAbstractNetworkThread`, which provides a proxy for the
                emotional motor system in the brain.
                		- `Period`: This property holds the value of 30, indicating the
                period for which the `timer` will run.

        """
        super(GenericWorker, self).__init__()

        self.emotionalmotor_proxy = mprx["EmotionalMotorProxy"]

        self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
        self.Period = 30
        self.timer = QtCore.QTimer(self)


    @QtCore.Slot()
    def killYourSelf(self):
        rDebug("Killing myself")
        self.kill.emit()

    # \brief Change compute period
    # @param per Period in ms
    @QtCore.Slot(int)
    def setPeriod(self, p):
        """
        Updates the ` Period ` attribute and starts the timer using the new period
        value.

        Args:
            p (float): new period and is assigned to the ` Period ` attribute of
                the instance, before starting the timer using that same ` Period
                `.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

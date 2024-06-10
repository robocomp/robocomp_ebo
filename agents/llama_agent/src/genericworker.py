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
        Initializes an instance of `GenericWorker`. It sets up a mutex for thread-safe
        access, creates a timer with a 30-second interval, and defines an LLM proxy
        object.

        Args:
            mprx (object/instance of the class `QMutex`.): LLMProxy object, which
                provides an interface to the Language Model for this worker instance.
                
                		- `LLMProxy`: A Qt object that serves as an abstraction layer
                for interacting with the Lightning Layer Manager (LLM).
                		- `mutex`: A recursive mutex used to protect access to internal
                data structures.
                		- `Period`: The interval between timer ticks, set to 30 in this
                example.
                		- `timer`: A Qt timer that is used to schedule periodic execution
                of the worker's callback function.

        """
        super(GenericWorker, self).__init__()

        self.llm_proxy = mprx["LLMProxy"]

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
        Sets a new period duration, updates the instance variable `Period`, and
        starts a timer to execute the code in that period.

        Args:
            p (int): period of time after which the timer should start running,
                and it is used to set the timer's interval.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

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
        Initializes an instance of the `GenericWorker` class, creating a mutex and
        timer for periodic execution with a specified interval of 30 seconds.

        Args:
            mprx (`QtCore.QMutex` object.): mutex object used to protect access
                to the timer's function.
                
                	1/ `mutex`: A `QtCore.QMutex` object that is created in `recursive`
                mode, indicating that it can be acquired and released multiple times.
                	2/ `Period`: An integer value representing the interval between
                timer ticks in seconds (30 in this case).
                	3/ `timer`: A `QtCore.QTimer` instance that is owned by the current
                object.

        """
        super(GenericWorker, self).__init__()


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
        Sets a new period value for an instance of `Timer` and starts a timer with
        that period.

        Args:
            p (int): period of time to wait before starting the timer, and it is
                assigned to the `self.Period` instance variable and used to set
                the interval of the timer.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

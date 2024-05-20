#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2021 by YOUR NAME HERE
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
        Initializes a GenericWorker object, creating a recursive mutex and a timer
        with a 30-second period.

        Args:
            mprx (`QtCore.QMutex` instance.): QMutex lock to be created and managed
                by the instance of `GenericWorker`.
                
                		- `mutex`: A `QMutex` object that provides mutual exclusive
                access to the internal state of the worker.
                		- `Period`: The interval at which the worker will check for new
                tasks to process, with a value of 30 indicating a 30-second timeout.
                		- `timer`: An instance of `QTimer`, which will be used to schedule
                timer events for the worker to execute its task processing logic.

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
        Updates the period of a timer object and starts it running with the new period.

        Args:
            p (float): new period duration and assigns it to the instance attribute
                ` Period `.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

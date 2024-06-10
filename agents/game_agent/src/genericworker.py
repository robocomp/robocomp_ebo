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
        Sets up a recursor mutex and a timer with a period of 30 seconds for use
        by the `GenericWorker` class.

        Args:
            mprx (`QtCore.QMutex`.): QMutex that is used to synchronize access to
                the instance's internal state.
                
                		- `mutex`: A `QMutex` object for protecting the access to the
                worker's state. It is set to `Recursive`, indicating that it can
                be locked multiple times without causing any issues.
                		- `Period`: An integer value representing the interval between
                successive runs of the worker's task, set to 30 seconds in this case.

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
        Updates the `Period` attribute and starts a timer with the new period using
        the `timer.start()` method.

        Args:
            p (float): duration of the interval, and it is used to set the value
                of `self.Period`, which is then passed to the `timer.start()`
                method to schedule the interval's execution.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

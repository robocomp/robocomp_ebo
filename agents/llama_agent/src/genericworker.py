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
        Initializes an instance of `GenericWorker`. It creates a `LLMProxy`, a
        `QMutex` for synchronization, and sets the period of timer to 30 seconds.

        Args:
            mprx ("LLMProxy" QObject object.): LLMProxy object, which provides a
                connection to the Linux Little Endian Machine (LLM) for execution
                of tasks.
                
                		- `LLMProxy`: This is an attribute of `mprx` representing the
                LLMProxy object, which provides access to the LLM framework.
                		- ` Period`: An integer attribute representing the time interval
                (in seconds) between successive checks for dead clients in the LLM.

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
        Sets the period of a timer to a given value `p` and updates the internal
        state of the class `Timer`.

        Args:
            p (int): period of the timer, which is set as the value of the `Period`
                attribute of the `self` object.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

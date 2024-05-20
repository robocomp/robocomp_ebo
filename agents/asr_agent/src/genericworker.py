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
        Initializes an instance of `GenericWorker`, setting up a proxy for Automatic
        Speech Recognition (ASR), a mutex to regulate access to the ASR API, and
        a timer with a period of 30 seconds.

        Args:
            mprx ("ASRProxy".): `ASRProxy` instance, which is a proxy object for
                the Automatic Speech Recognition (ASR) service.
                
                		- `ASRProxy`: This property is an instance of `QtCore.QObject`.
                		- `Period`: This property is a positive integer value representing
                the time interval (in seconds) between ASR updates.

        """
        super(GenericWorker, self).__init__()

        self.asr_proxy = mprx["ASRProxy"]

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
        Sets the period of a timer, updating the `Period` attribute and starting
        the timer using the provided value.

        Args:
            p (float): period of the timer, and its value is used to set the timer's
                interval before starting it.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

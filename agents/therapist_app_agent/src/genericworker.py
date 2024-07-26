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


try:
    from ui_mainUI import *
except:
    print("Can't import UI file. Did you run 'make'?")
    sys.exit(-1)



class GenericWorker(QtWidgets.QWidget):

    """
    Manages a worker process with a periodic timer and provides methods to set the
    timer period and kill the process. It also displays a graphical user interface
    using the `QtWidgets.QWidget` and `Ui_guiDlg`.

    Attributes:
        kill (QtCoreSignal): Named kill. It is emitted by the `killYourSelf` method
            when it is called. This signal is used to kill the worker instance.
        ui (Ui_guiDlg): Initialized by calling the `setupUi` method on it, which
            presumably sets up a user interface for the widget.
        show (None): Inherited from its superclass `QtWidgets.QWidget`. It displays
            the widget on screen. In this context, it is called to make the widget
            visible when an instance of `GenericWorker` is created in its constructor.
        mutex (QtCoreQMutex): Initialized with a recursive mutex. This allows
            multiple threads to lock the same mutex recursively without causing deadlocks.
        Period (int): 30 by default, representing a time period in milliseconds.
            It is used as the interval for triggering events in the QTimer instance
            of the same class.
        timer (QtCoreQTimer|QtWidgetsQWidget): Set to start at a specific period
            defined by the Period attribute after the setPeriod method is called.

    """
    kill = QtCore.Signal()

    def __init__(self, mprx):
        """
        Initializes an instance of a worker, setting up its user interface and
        timer. It also creates a mutex for synchronization and sets various
        properties such as Period. The UI is set up with setupUi, and the window
        is made visible using show.

        Args:
            mprx (object): Passed to the class constructor. It represents an
                instance of some class, likely an object that provides some
                functionality or data needed by the `GenericWorker` object.

        """
        super(GenericWorker, self).__init__()

        # COMENTADO PARA INTENTAR LANZAR VARIAS VENTANAS
        self.ui = Ui_guiDlg()
        self.ui.setupUi(self)
        self.show()

        self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
        self.Period = 30
        self.timer = QtCore.QTimer(self)


    @QtCore.Slot()
    def killYourSelf(self):
        """
        Emits a signal named `self.kill` after logging a debug message, indicating
        an intention to terminate itself. This functionality is typically used for
        self-interruption or cancellation of the worker's task.

        """
        rDebug("Killing myself")
        self.kill.emit()

    # \brief Change compute period
    # @param per Period in ms
    @QtCore.Slot(int)
    def setPeriod(self, p):
        """
        Sets a new period and restarts a timer. The method takes an integer as
        input, prints a message indicating the change, updates the internal `Period`
        attribute, and then starts the timer with the updated period.

        Args:
            p (int): Not used directly. It will be assigned to the object's attribute
                `self.Period`. The `@QtCore.Slot(int)` decorator specifies that
                this slot expects an integer as its argument.

        """
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

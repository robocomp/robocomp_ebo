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
#

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        """
        Sets up an instance of the `SpecificWorker` class, initializing its
        `proxy_map`, `Period` and `timer`. It also performs a startup check or
        starts a timer depending on the value of `startup_check`.

        Args:
            proxy_map (int): mapping of proxy ports to original ports.
            startup_check (bool): functionality to check the status of the startup
                process when the timer starts.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        """
        Sets speed base for a robot proxy, updates transform values in an internal
        model, and prints out a vector containing the values of a pose transformation.

        Returns:
            int: a boolean value `True`.

        """
        print('SpecificWorker.compute...')
        # computeCODE
        # try:
        #   self.differentialrobot_proxy.setSpeedBase(100, 0)
        # except Ice.Exception as e:
        #   traceback.print_exc()
        #   print(e)

        # The API of python-innermodel is not exactly the same as the C++ version
        # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
        # z = librobocomp_qmat.QVec(3,0)
        # r = self.innermodel.transform('rgbd', z, 'laser')
        # r.printvector('d')
        # print(r[0], r[1], r[2])

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)



    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of getLastPhrase method from ASR interface
    #
    def ASR_getLastPhrase(self):
        """
        Generates a high-quality documentation string for given code.

        Returns:
            str: a string containing the last processed phrase.

        """
        ret = str()
        #
        # write your CODE here
        #
        return ret
    #
    # IMPLEMENTATION of listenMicro method from ASR interface
    #
    def ASR_listenMicro(self, timeout):
        """
        Listens for audio input from a microphone, returns it as a string, and
        provides no further functionality.

        Args:
            timeout (int): amount of time that the `str()` method call takes before
                returning an error.

        Returns:
            str: a string representation of the audio data.

        """
        ret = str()
        #
        # write your CODE here
        #
        return ret
    #
    # IMPLEMENTATION of listenVector method from ASR interface
    #
    def ASR_listenVector(self, audio):
    
        #
        # write your CODE here
        #
        pass


    #
    # IMPLEMENTATION of listenWav method from ASR interface
    #
    def ASR_listenWav(self, path):
    
        #
        # write your CODE here
        #
        pass


    #
    # IMPLEMENTATION of phraseAvailable method from ASR interface
    #
    def ASR_phraseAvailable(self):
        """
        Returns a boolean value indicating whether a speech recognition phrase is
        available for processing.

        Returns:
            bool: a boolean value indicating whether a phrase is available for
            speech recognition.

        """
        ret = bool()
        #
        # write your CODE here
        #
        return ret
    #
    # IMPLEMENTATION of resetPhraseBuffer method from ASR interface
    #
    def ASR_resetPhraseBuffer(self):
    
        #
        # write your CODE here
        #
        pass


    # ===================================================================
    # ===================================================================




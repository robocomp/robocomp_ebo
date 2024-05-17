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

import sys, os, Ice

ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except:
    print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
    ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
    raise RuntimeError('ROBOCOMP environment variable not set! Exiting.')


Ice.loadSlice("-I ./src/ --all ./src/ASR.ice")

from RoboCompASR import *

class ASRI(ASR):
    def __init__(self, worker):
        self.worker = worker


    def getLastPhrase(self, c):
        return self.worker.ASR_getLastPhrase()

    def listenMicro(self, timeout, c):
        return self.worker.ASR_listenMicro(timeout)

    def listenVector(self, audio, c):
        return self.worker.ASR_listenVector(audio)

    def listenWav(self, path, c):
        return self.worker.ASR_listenWav(path)

    def phraseAvailable(self, c):
        return self.worker.ASR_phraseAvailable()

    def resetPhraseBuffer(self, c):
        return self.worker.ASR_resetPhraseBuffer()

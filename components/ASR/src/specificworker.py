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

# audio managment
from multiprocessing import Process, Queue, Event
import numpy as np
import pyaudio
import wave

# voice detection with respeaker
from tuning import Tuning
import usb.core
import usb.util

# allows to execute commands
import subprocess
import os

#################################### PORCUPINE #####################################

ACCESS_KEY = "YhpQKilovfhz5/6XxLxq+Wmiz45bbtBUVruBptzYOdHqfyHhaUTpLw=="
PPN_PATH = "./src/audio-config/hello-shadow_en_linux_v3_0_0/hello-shadow_en_linux_v3_0_0.ppn"

############################### AUDIO DEVICE CONFIG ################################

####### initial configuration
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 1  # Cambia según tus ajustes
RESPEAKER_WIDTH = 2
FORMAT = pyaudio.paInt16  # calidad de audio. probar float32 o float64
OUTPUT_FILENAME = "record.wav"

# instancia
audio = pyaudio.PyAudio()

# print available audio devices 
# num_devices = audio.get_device_count()

# print("Lista de dispositivos de audio disponibles:")
# for i in range(num_devices):
#     device_info = audio.get_device_info_by_index(i)
#     device_name = device_info["name"]
#     print(f"Dispositivo {i}: {device_name}")

# searching its index
target_device_name = "ReSpeaker 4 Mic Array (UAC1.0): USB Audio" # our device name
target_device_index = 0
info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(numdevices):
    device_info = audio.get_device_info_by_host_api_device_index(0, i)
    if device_info.get('maxInputChannels') > 0:
        if target_device_name in device_info.get('name'):
            target_device_index = i

# opening audio stream if the device was found
if target_device_index is not None:
    stream = audio.open(
        format=audio.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        rate=RESPEAKER_RATE,
        input=True,
        input_device_index=target_device_index
    )
else:
    print(f"{target_device_name} was not found.")

############################### SILENCES AND PAUSES ################################

SILENCE_DURATION = 2  # silence duration required to finish the program
PAUSE_DURATION = 0.5  # pause duration required to transcript a record

################################# SPECIFICWORKER ###################################

class SpecificWorker(GenericWorker):

    ############################
    # initial configuration 
    ############################
    def __init__(self, proxy_map, startup_check=False):
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
        print('SpecificWorker.compute...')

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)



    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of getLastPhrase method from ASR interface
    #
    def ASR_getLastPhrase(self):
        ret = str()
        #
        # write your CODE here
        #
        return ret

    ############################
    # LISTEN MICRO INTERFACE
    ############################
    def generate_wav(self, file_name, record): 
        with wave.open(file_name, 'wb') as wf:
            wf.setnchannels(RESPEAKER_CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RESPEAKER_RATE)
            wf.writeframes(b''.join(record))

    def call_whisper(self, audio_file): 
        command = ["whisper", audio_file, "--model", "small", "--language", "Spanish"]
        subprocess.run(command, check=True)

    def transcript(self, frame): 
        self.generate_wav(OUTPUT_FILENAME, frame)
        self.call_whisper(OUTPUT_FILENAME)
        with open("user_response.txt", "a") as prompt_file:
            subprocess.run(["cat", "record.txt"], stdout=prompt_file)
    
    def manage_transcription(self):
        while not self.silence_detected.is_set():
            if not self.record_queue.empty():
                frame = self.record_queue.get()
                self.transcript(frame)

        # clean queue before finish
        while not self.record_queue.empty():
            frame = self.record_queue.get()
            self.transcript(frame)
        
    def terminate(self):
        stream.stop_stream()
        stream.close()
        audio.terminate()
        self.porcupine.delete()

    def delete_transcription(self):
        if os.path.exists("user_response.txt"):
            subprocess.run(["rm", "user_response.txt"])

    def ASR_listenMicro(self, timeout):
        user_response = str()
        


        print(user_response)
        return user_response
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




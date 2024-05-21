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
PAUSE_DURATION = 1  # pause duration required to transcript a record
BUFFER_DURATION = 0.5  # Duración del buffer en segundos
BUFFER_LENGTH = int(RESPEAKER_RATE * BUFFER_DURATION)

################################# SPECIFICWORKER ###################################

class SpecificWorker(GenericWorker):

    ############################
    # initial configuration 
    ############################
    def __init__(self, proxy_map, startup_check=False):
        """
        Initializes an instance of `SpecificWorker`, creating a proxy map and
        setting its period to 2000 milliseconds. It then performs startup checks
        or connects a timer for computation when the timer expires, depending on
        a given condition.

        Args:
            proxy_map (dict): mapping of proxy classes to their corresponding
                instance objects, which is used to initiate the worker object.
            startup_check (`object`.): functionality to check whether the worker
                is starting up or not and run any required code if necessary when
                the worker starts.
                
                		- `startup_check`: a boolean attribute that determines whether
                the worker should perform startup checks or not.

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
        Verifies if a provided value is specific and returns `True` if it is,
        otherwise returns `False`.

        Returns:
            True` value: `True`.
            
            		- The output is a `True` value, indicating that the computation was
            successful.
            
            	No further information or properties are provided beyond this single
            fact.

        """
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
        """
        Returns a string value representing the last phrase spoken by the user,
        as recorded by the Audio Stream Reader module.

        Returns:
            str: a string containing the last phrase spoken.

        """
        ret = str()
        #
        # write your CODE here
        #
        return ret

    ############################
    # LISTEN MICRO INTERFACE
    ############################
    def generate_wav(self, file_name, record): 
        """
        Modifies an existing file using the `wave` module and opens it in write
        mode (`'wb'`). It then sets the channel count, sample width, and frame
        rate to specified values before writing new audio data to the file.

        Args:
            file_name (str): file to be written with the modified audio data.
            record (bytes-typed array.): 3D audio data that is written to the file
                by the function, composed of multiple channels of sampled audio
                data at a specific frame rate.
                
                		- `b''.join(record)`: The `record` is a list of byte strings
                representing the audio samples in WAV format. Joining these byte
                strings with an empty string (`b''`) creates a single string that
                can be written to the output file using the `writeframes()` method.
                		- `RESPEAKER_CHANNELS`: The number of channels in the WAV file,
                which is set to 1 in this case.
                		- `RESPEAKER_RATE`: The frame rate at which the audio samples
                are written to the output file, which is set to 44.1 kHz in this
                case.

        """
        with wave.open(file_name, 'wb') as wf:
            wf.setnchannels(RESPEAKER_CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RESPEAKER_RATE)
            wf.writeframes(b''.join(record))

    def call_whisper(self, audio_file): 
        command = ["whisper", audio_file, "--model", "base", "--language", "Spanish", "--temperature", "0.2"]
        subprocess.run(command, check=True)

    def transcript(self, frame): 
        """
        Generates high-quality documentation for given code, including saving
        output to a file and reading user input from another file.

        Args:
            frame (int): frame number for which the audio will be generated in the
                output file.

        """
        self.generate_wav(OUTPUT_FILENAME, frame)
        self.call_whisper(OUTPUT_FILENAME)
        with open("user_response.txt", "a") as prompt_file:
            subprocess.run(["cat", "record.txt"], stdout=prompt_file)
    
    def manage_transcription(self):
        """
        Cleans and transcribes audio frames from a queue, transcribing each frame
        before cleaning the queue again.

        """
        while not self.silence_detected.is_set():
            if not self.record_queue.empty():
                frame = self.record_queue.get()
                self.transcript(frame)

        # clean queue before finish
        while not self.record_queue.empty():
            frame = self.record_queue.get()
            self.transcript(frame)
        
    def terminate(self):
        """
        Stops a running `Audio` stream, frees any associated resources, and ends
        the stream's playback.

        """
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def delete_transcription(self):
        if os.path.exists("user_response.txt"):
            subprocess.run(["rm", "user_response.txt"])

    def ASR_listenMicro(self, timeout):
        """
        1/ Deletes a previous transcription 2. Starts a transcription process 3.
        Listens for voice and pauses, checking for durations 4. Enqueues audio
        fragments for transcription when a pause is reached 5. Joins the transcription
        process when no voice is detected during a silence duration

        Args:
            timeout (float): maximum duration for which the program listens before
                considering it to be silence and ending the program.

        Returns:
            str: a sentence describing what the user has said, if they have spoken
            at all.

        """
        user_response = str()

        # clean the directory
        self.delete_transcription()

        #initialize params
        self.novoice_counter = 0
        self.silence_detected = Event()
        self.pause_detected = False
        self.record_queue = Queue()

        # start multiprocessing management
        transcription_process = Process(target=self.manage_transcription)
        transcription_process.start()

        # initialize detector of Reaspeaker
        mic_tunning = Tuning(usb.core.find(idVendor=0x2886, idProduct=0x0018))
        record = []  # save the recording after the wake word has been detected

        try:
            print("Listening...")

            while not self.silence_detected.is_set():
                # take an audio fragment
                pcm = stream.read(BUFFER_LENGTH, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)



                record.append(pcm.copy()) # add audio fragment if we have started the record

                # voice detection
                if mic_tunning.is_voice(): # if voice detected
                    self.novoice_counter = 0  # restart no voice detection
                    self.pause_detected = False
                else: 
                    self.novoice_counter += 1
                    
                    # check if a pause duration has been reached
                    if self.novoice_counter >= PAUSE_DURATION*4 and not self.pause_detected:
                        print("Pause")
                        self.pause_detected = True

                        if record:  # Check if the record list is not empty
                            # enqueue the fragment for transcription 
                            self.record_queue.put(record.copy())
                            record.clear()

                    # check if a silence duration has been reached to finish the program
                    if self.novoice_counter >= SILENCE_DURATION*4:
                        print("Silence")
                        self.silence_detected.set()

                        transcription_process.join()

                        if os.path.exists("user_response.txt"):
                            # read user_response.txt content
                            with open("user_response.txt", "r") as file:
                                user_response = file.read()
                        
                            if not user_response.strip():
                                user_response = "The user did not respond"
                        else: 
                            user_response = "The user did not respond"

        except KeyboardInterrupt:
            transcription_process.join()
            user_response = "Sorry, I couldn't listen to you."
            self.terminate()
            
        print("Lo que he escuchado ha sido: ", user_response)
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
        """
        Is an ambiguous reference to a method that can be either an integer or a
        boolean value. Its purpose is not provided, and its behavior is therefore
        unknown.

        Returns:
            bool: a boolean value indicating whether the phrase is available or not.

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




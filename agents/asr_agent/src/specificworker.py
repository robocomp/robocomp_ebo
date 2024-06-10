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

from pydsr import *


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

# NUEVOS IMPORTS
# Audio management
from multiprocessing import Process, Queue, Event
import numpy as np
import pyaudio
import wave

# Voice detection with respeaker
from tuning import Tuning
import usb.core
import usb.util

# Allows to execute commands
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
    def __init__(self, proxy_map, startup_check=False):
        """
        Sets up a worker's internal state, connecting signal handlers for graph
        updates and starting a timer for periodic computation. It also loads initial
        node values and performs an initial check for incorrect loading of those
        values.

        Args:
            proxy_map (dict): Python Agent that is being initialized, and it is
                used to store references to its various attributes and methods for
                easier access within the function.
            startup_check (bool): whether to call the `startup_check()` method
                after connecting the signals and before starting the timer, which
                checks if the graph is properly initialized and raises an error
                if it's not.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 6
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            #signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            #signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            #signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            #signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            #signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)
            
        # Se lee el nodo del grafo
        asr_node = self.g.get_node("ASR")

        # Se guardan los valores iniciales
        print("Cargando valores iniciales del atributo escuchando")
        self.last_state = asr_node.attrs["escuchando"].value

        # Comprobación de esta carga de valores iniciales del grafo
        if self.last_state == asr_node.attrs["escuchando"].value:
            print("Valores iniciales cargados correctamente")
        else:
            print(
                "Valores iniciales error al cargar (Puede afectar al inicio del programa, pero no es un problema grave)")
        

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
        #print('SpecificWorker.compute...')

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
        Is intended to take a string and return its last phrase.

        Returns:
            str: a string representation of the last spoken phrase.

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
        Modifies the wave file object `wf` by setting its channels, sample width,
        and framerate to the values specified for RESPEAKER format, then writes a
        list of audio samples to it.

        Args:
            file_name (str): file to be written, and its value determines the name
                of the output file created by the `wave.open()` function.
            record (str): audio data to be written to the wave file.

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
        Generates high-quality documentation for given code, writing output to a
        file named after the input frame and appending a response file containing
        a recording command.

        Args:
            frame (int): 2D image frame that is to be processed and generated into
                an audio file.

        """
        self.generate_wav(OUTPUT_FILENAME, frame)
        self.call_whisper(OUTPUT_FILENAME)
        with open("user_response.txt", "a") as prompt_file:
            subprocess.run(["cat", "record.txt"], stdout=prompt_file)

    def manage_transcription(self):
        """
        Clears the transcription queue when finished and removes frames from the
        queue until it is empty.

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
        Stops and closes a streaming process, effectively ending its execution.

        """
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def delete_transcription(self):
        if os.path.exists("user_response.txt"):
            subprocess.run(["rm", "user_response.txt"])

    def ASR_listenMicro(self, timeout):
        """
        Listen for voice input and detect silences and pauses, enqueuing audio
        fragments for transcription when a pause is detected. It also checks for
        user responses and updates the node with the result of the listening process.

        Args:
            timeout (float): duration of time the program should run before a
                "silence" condition is detected and the transcription process is
                finished, triggering the return of the user response.

        Returns:
            str: a string containing the audio input and user response, or an error
            message if the user didn't respond.

        """
        user_response = str()

        # clean the directory
        self.delete_transcription()

        # initialize params
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

                record.append(pcm.copy())  # add audio fragment if we have started the record

                # voice detection
                if mic_tunning.is_voice():  # if voice detected
                    self.novoice_counter = 0  # restart no voice detection
                    self.pause_detected = False
                else:
                    self.novoice_counter += 1

                    # check if a pause duration has been reached
                    if self.novoice_counter >= PAUSE_DURATION * 4 and not self.pause_detected:
                        print("Pause")
                        self.pause_detected = True

                        if record:  # Check if the record list is not empty
                            # enqueue the fragment for transcription
                            self.record_queue.put(record.copy())
                            record.clear()

                    # check if a silence duration has been reached to finish the program
                    if self.novoice_counter >= SILENCE_DURATION * 4:
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

        asr_node = self.g.get_node("ASR")

        if asr_node is None:
            print("No ASR")
            return False
        else:
            asr_node.attrs["texto"] = Attribute(user_response, self.agent_id)
            asr_node.attrs["escuchando"] = Attribute(False, self.agent_id)
            self.last_state = False
            self.g.update_node(asr_node)

        return user_response

    def hablar_escuchado(self,escuchado):
        """
        Modifies an attribute on a TTS node, `to_say`, with a new value specified
        by the `escuchado` variable and the `agent_id`.

        Args:
            escuchado (Attribute object.): audio output of the TTS node.
                
                		- `self.agent_id`: A string attribute representing the agent ID.
                
                	Therefore, when the function is called with the argument `
                escuchado`, it will modify the `to_say` attribute of the TTS node
                with the value of `escuchado`. The function also updates the TTS
                node in the graph using the `update_node()` method.

        Returns:
            Attribute` object: a modified TTS node with an updated `to_say` attribute.
            
            		- `tts_node`: The node representing the TTS functionality in the graph.
            		- `escritor`: The attribute containing the text to be spoken, which
            is assigned with the `Attribute` class and has the value of the
            `escuchado` variable.
            		- `self.agent_id`: The ID of the agent that the function belongs to.

        """
        tts_node = self.g.get_node("TTS")
        if tts_node is None:
            print("No TTS")
            return False
        else:
            tts_node.attrs["to_say"] = Attribute(escuchado, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(tts_node)

    ######################
    # From the RoboCompASR you can call this methods:
    # self.asr_proxy.getLastPhrase(...)
    # self.asr_proxy.listenVector(...)
    # self.asr_proxy.listenWav(...)
    # self.asr_proxy.phraseAvailable(...)
    # self.asr_proxy.resetPhraseBuffer(...)



    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        """
        Updates an audio input node's attribute "escuchando" based on its previous
        state, and performs an action based on the new state.

        Args:
            id (int): ID of the node to check the attribute value for.
            attribute_names ([str]): names of the attributes that are being monitored
                for changes in the specified node, and is used to print updates
                to these attributes in green text using the `console.print()` method.

        """
        asr_node = self.g.get_node("ASR")
        if asr_node.attrs["escuchando"].value != self.last_state:
            self.last_state = asr_node.attrs["escuchando"].value
            if asr_node.attrs["escuchando"].value == True:
                print("Empezando a escuchar")
                escuchado = self.ASR_listenMicro(2)
                #self.hablar_escuchado(escuchado) # TEST DE REPETIR LO ESCUCHADO

            else:
                print("No escuchando")
                pass
        else:
            pass
        #console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

    def update_node(self, id: int, type: str):
        console.print(f"UPDATE NODE: {id} {type}", style='green')

    def delete_node(self, id: int):
        console.print(f"DELETE NODE:: {id} ", style='green')

    def update_edge(self, fr: int, to: int, type: str):

        console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')

    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')

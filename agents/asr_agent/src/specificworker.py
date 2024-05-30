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
        Initializes an instance of `DSRGraph` with a unique agent ID and connects
        signals for updating node attributes and timed computations.

        Args:
            proxy_map (dict): mapping of nodes and edges in the graph to their
                corresponding proxies, allowing the agent to interact with the
                graph more efficiently.
            startup_check (`RuntimeError`.): execution of a specific check or
                action during the startup phase of the function.
                
                		- `signals`: This is an instance of the `Signals` class, which
                provides methods for connecting signals to the graph agent's update
                and event handlers.
                		- `Period`: This is the time period after which the agent will
                check if any updates are available.
                		- `agent_id`: This is a unique integer ID assigned to the agent
                in the deployment.
                		- `g`: This is an instance of the `DSRGraph` class, which
                represents the graph that the agent operates on.
                		- `startup_check`: This is a boolean value indicating whether
                the agent should perform a startup check. If `startup_check` is
                `True`, then the agent will call the `startup_check()` method;
                otherwise, it will not.

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
        Takes no arguments and returns a string value, which is the last phrase
        from a given input of text.

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
        Modifies a file to contain an audio signal with a specified number of
        channels, sample width, and framerate. It reads a sequence of bytes from
        the function argument and writes them to the file as audio data.

        Args:
            file_name (str): file name that contains audio data to be converted
                and written in a new format.
            record (list): 2D audio data as a list of signed 16-bit integer values,
                with each element representing one frame of the audio data.

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
        Generates high-quality documentation for code by calling a whisper function,
        writing the output to a file, and appending the input file contents to a
        user response file.

        Args:
            frame (int): frame number to be generated as a wave file, and is passed
                to the `self.call_whisper()` method for further processing.

        """
        self.generate_wav(OUTPUT_FILENAME, frame)
        self.call_whisper(OUTPUT_FILENAME)
        with open("user_response.txt", "a") as prompt_file:
            subprocess.run(["cat", "record.txt"], stdout=prompt_file)

    def manage_transcription(self):
        """
        Clears the record queue before finishing by consuming all frames in the
        queue and transcribing each one using the `transcript()` method.

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
        Stops the audio streaming process, releases any associated resources, and
        clears the object reference.

        """
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def delete_transcription(self):
        if os.path.exists("user_response.txt"):
            subprocess.run(["rm", "user_response.txt"])

    def ASR_listenMicro(self, timeout):
        """
        Performs real-time audio listening and speech recognition, detecting voice
        and pauses, enqueuing recordings for transcription, and providing a response
        to the user based on their spoken input.

        Args:
            timeout (list): duration of time the function will listen to the user
                before interrupting and ending the program, and it is used to
                determine when to stop listening and return a response.

        Returns:
            str: a transcribed audio response from a user.

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
        Modifies an TTS node's "to_say" attribute with a given value, then updates
        the node in the graph.

        Args:
            escuchado (Attribute.): attribute value that is being modified for the
                TTS node.
                
                		- `self.agent_id`: The identifier of the agent that generated
                the audio data.
                		- `escuchado`: The deserialized audio data.

        Returns:
            bool: a statement indicating whether TTS is available or not, followed
            by an update of the TTS node's attribute with the given text.

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
        Updates the state of a specific node in a graph based on an attribute's
        value, and performs actions depending on whether the node is listening or
        not.

        Args:
            id (int): identifier of the node whose attributes are being checked
                and updated in the function.
            attribute_names ([str]): names of the attributes to be printed in green
                color in the console for updates on the node's attributes.

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

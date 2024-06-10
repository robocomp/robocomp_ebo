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

##########################################################################
# AGENTE SOLO PARA EBO
# SI EBO NO ESTÁ ENCENDIDO, Y EL PC NO ESTA CONECTADO A EBO
# ESTE AGENTE NO FUNCIONARÁ
##########################################################################

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *

# Imports de MeloTTS
import subprocess
import sys

try:
	from Queue import Queue
except ImportError:
	from queue import Queue

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from genericworker import *
import time

# Nuevos imports
from melo.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import threading
import os
import random

max_queue = 100
charsToAvoid = ["'", '"', '{', '}', '[', '<', '>', '(', ')', '&', '$', '|', '#']

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        """
        Initializes an instance of `SpecificWorker` by creating a ProxyMap, setting
        the device and model for text-to-speech (TTS), and connecting signals to
        update node attributes and trigger the `compute` function every `Period`.

        Args:
            proxy_map (dict): Python agent object's instance attributes as methods
                for communication with other components through signaling, allowing
                the agent to interact with its environment and receive updates.
            startup_check (bool): Whether the function should check if the agent
                has started or not.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        #MeloTTS INITS
        self.audioenviado = False
        self.text_queue = Queue(max_queue)

        self.device = 'cuda:0'  # Usando la gráfica
        self.model = TTS(language='ES', device=self.device)
        self.speaker_ids = self.model.hps.data.spk2id
        self.speed = 1.0
        ###########################################
        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 5
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)


        # Se lee el nodo del grafo
        tts_node = self.g.get_node("TTS")

        # Se guardan los valores iniciales
        print("Cargando valores iniciales del atributo to_say")
        self.last_text = tts_node.attrs["to_say"].value

        # Comprobación de esta carga de valores iniciales del grafo
        if self.last_text == tts_node.attrs["to_say"].value:
            print("Valores iniciales cargados correctamente")
        else:
            print(
                "Valores iniciales error al cargar (Puede afectar al inicio del programa, pero no es un problema grave)")

        llm_node = self.g.get_node("LLM")
        print("Cargando valores iniciales del atributo out_llama")
        self.last_out = llm_node.attrs["out_llama"].value

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            #signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            #signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            #signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            #signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            #signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            #console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        self.emotionalmotor_proxy.expressJoy() # Pone a EBO contento al lanzar el agente, como de momento solo vamos a meter ASR, TTS y LLama que tenga buena cara.


    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    # Función que contiene y ejecuta todo lo necesario para generar el audio TTS a partir del texto y reproducirlo. Con la nueva voz del TTS.
    def new_tts(self, text):
        # Función para dividir el texto en partes más pequeñas
        """
        Takes a string `text` and splits it into parts, generating audio files for
        each part using an SSML-based TTS engine. The generated audio files are
        added to a queue, which is processed by another thread that plays the audio
        in order.

        Args:
            text (str): text to be divided into parts for speech synthesis.

        Returns:
            list: a list of audio file paths for each part of the given text.

        """
        def split_text(text):
            """
            Takes a string as input and returns an list of substrings, separated
            by a specified character (currently ".", "!", or "?") and found after
            a certain number of characters (75 or 150)

            Args:
                text (str): string that the function is called upon, which is
                    divided into parts based on the rules specified in the function.

            Returns:
                list: a list of substrings separated by dots, exclamation points,
                or questions marks.

            """
            parts = []
            start = 0
            end = 0
            while end < len(text):
                # Encontrar el final de la parte basado en las reglas especificadas
                if len(parts) == 0 or len(parts) == 1:
                    # Para la primera y segunda parte, encontrar el primer punto después de 75 caracteres
                    end = min(start + 75, len(text))
                    while end < len(text) and text[end] not in [".", "!", "?"]:
                        end += 1
                else:
                    # Para las siguientes partes, encontrar "." "!" o "?" después de 150 caracteres
                    end = min(start + 150, len(text))
                    while end < len(text) and text[end] not in [".", "!", "?"]:
                        end += 1

                # Agregar la parte al resultado
                parts.append(text[start:end + 1].strip())

                # Mover el inicio al siguiente punto de división
                start = end + 1 if end < len(text) else len(text)

            return parts

        # Función para generar audio y agregar las rutas de salida a la cola
        def generate_audio(queue):
            """
            Takes a list of text parts (`text_parts`) and uses a TTS model
            (`self.model`) to generate audio for each part, storing the output
            files in a queue (`queue`). When all parts are processed, the function
            marks the end of the queue by putting `None` in it.

            Args:
                queue (`object`.): output file path produced by the TTS model for
                    each part of the given text, which is put on the queue for
                    further processing.
                    
                    		- `queue`: A Python ` queue` object that stores files for
                    speech synthesis.
                    		- `put()` method: Used to add a file to the end of the queue.
                    		- `get()` method: Retrieves the next file from the front of
                    the queue and returns it.

            """
            for i, part in enumerate(text_parts):
                output_path = output_paths[i]
                self.model.tts_to_file(part, self.speaker_ids['ES'], output_path, speed=self.speed)
                queue.put(output_path)
            # Marcar el final de la cola
            queue.put(None)

        # Función para reproducir el audio en orden
        def play_audio(queue):
            """
            Processes audio segments from a queue, playing them through an Emotional
            Motor proxy when the talking flag is set to True and adding them to
            the queue when done.

            Args:
                queue (`queue.Queue`.): stream of output files to be processed by
                    the
                    function, with each file being pulled from the queue
                    
                    		- `queue`: A Queue class object, which represents a
                    first-in-first-out (FIFO) queue for handling tasks.
                    		- `get()`: Returns the next task from the queue or raises a
                    `queue.Empty` exception if the queue is empty.
                    		- `task_done()`: Calls the `__call__` method of an object,
                    which signifies that a task has been completed.
                    		- `release()`: Releases the semaphore associated with the
                    queue, allowing other tasks to access it.

            """
            while True:
                output_path = queue.get()
                if output_path is None:
                    break
                audio = AudioSegment.from_file(output_path)
                self.emotionalmotor_proxy.talking(True)
                play(audio)
                self.emotionalmotor_proxy.talking(False)
                queue.task_done()
                semaphore.release()

        # Obtener las partes del texto
        text_parts = split_text(text)

        # Ruta de salida
        output_paths = [f"es_{i}.wav" for i in range(len(text_parts))]
        # Cola para almacenar las rutas de salida de los archivos de audio generados
        output_queue = Queue()
        # Semáforo para sincronizar la generación y reproducción
        semaphore = threading.Semaphore(0)
        # Hilo para generar audio
        generate_thread = threading.Thread(target=generate_audio, args=(output_queue,))
        generate_thread.start()
        # Hilo para reproducir el audio
        play_thread = threading.Thread(target=play_audio, args=(output_queue,))
        play_thread.start()
        # Esperar a que todos los archivos de audio estén listos para reproducirse
        for _ in range(len(text_parts)):
            semaphore.acquire()
        # Esperar a que ambos hilos terminen
        generate_thread.join()
        play_thread.join()
        # Eliminar archivos temporales
        for output_path in output_paths:
            os.remove(output_path)
        
        ########################################################################
        # Modificar bool del ASR para que empiece a escuchar al terminar de hablar.
        asr_node = self.g.get_node("ASR")

        if asr_node is None:
            print("No ASR")
            return False
        else:
            asr_node.attrs["escuchando"] = Attribute(True, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(asr_node)
        ########################################################################

    @QtCore.Slot()
    def compute(self):
        """
        Determines if the text queue is empty, and if not, it retrieves a text
        item from the queue, creates a new TTS output, and then repeats the process.

        Returns:
            bool: `True`.

        """
        if self.text_queue.empty():
            #print("Cola vacía")
            pass
        else:
            text_to_say = self.text_queue.get()
            self.new_tts(text_to_say)
            pass

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)




    ######################
    # From the RoboCompEmotionalMotor you can call this methods:
    # self.emotionalmotor_proxy.expressAnger(...)
    # self.emotionalmotor_proxy.expressDisgust(...)
    # self.emotionalmotor_proxy.expressFear(...)
    # self.emotionalmotor_proxy.expressJoy(...)
    # self.emotionalmotor_proxy.expressSadness(...)
    # self.emotionalmotor_proxy.expressSurprise(...)
    # self.emotionalmotor_proxy.isanybodythere(...)
    # self.emotionalmotor_proxy.listening(...)
    # self.emotionalmotor_proxy.pupposition(...)
    # self.emotionalmotor_proxy.talking(...)

    def actualizar_to_say(self, nuevo):
        """
        Modifies an attribute in a node named `TTS`, updating its value with the
        one passed as an argument and printing the updated attribute name.

        Args:
            nuevo (`Attribute`.): new value that will be assigned to the `to_say`
                attribute of the `TTS` node.
                
                		- `nuevo`: A Python object representing a JSON-formatted data
                dictionary containing attributes related to TTS functionality,
                specifically the "to_say" attribute.

        Returns:
            Attribute` object: "Atributo modificado".
            
            		- `tts_node`: The node representing the TTS (Text-to-Speech) system
            in the scene graph.
            		- `nuevo`: A new attribute added to the `tts_node` with the value
            of `Attribute(nuevo, self.agent_id)`. This attribute represents the
            new audio content to be synthesized by the TTS system.

        """
        tts_node = self.g.get_node("TTS")
        if tts_node is None:
            print("No TTS")
            return False
        else:
            tts_node.attrs["to_say"] = Attribute(nuevo, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(tts_node)

    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        """
        Updates the attribute value of a node in a graph, based on a specified
        condition, and also appends the new text to a text queue for further processing.

        Args:
            id (int): GLTF node ID for which the attributes should be retrieved.
            attribute_names ([str]): list of names of attributes that need to be
                updated in the TTS and LLM nodes.

        """
        llm_node = self.g.get_node("LLM")
        if llm_node.attrs["out_llama"].value != self.last_out:
            self.last_out = llm_node.attrs["out_llama"].value
            self.actualizar_to_say(self.last_out)
        else:
            pass

        tts_node = self.g.get_node("TTS")
        if tts_node.attrs["to_say"].value != self.last_text:
            self.text_queue.put(tts_node.attrs["to_say"].value)
            self.last_text = tts_node.attrs["to_say"].value
            console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')
        else:
            pass


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

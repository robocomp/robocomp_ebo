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
        Initializes a MeloTTS worker, setting up various attributes and connections
        to signals for updates on the graph.

        Args:
            proxy_map (dict): mapping of graph nodes and edges to the TTS agent's
                internal state, allowing the TTS agent to interact with the external
                environment through its proxy node.
            startup_check (`object`.): Whether or not the TTS agent should perform
                an additional check during its startup process, which is currently
                commented out in the given code.
                
                	1/ `startup_check`: This is a boolean value indicating whether
                the agent has been started already or not. If it's `True`, the
                agent has already been started and no further initialization is
                required. If it's `False`, the agent has not been started yet, and
                the `startup_check` method needs to be called to perform the
                necessary initialization.
                	2/ `signals`: This is an instance of the `signals` class, which
                provides a way to connect signals to the agent's graph. The `signals`
                object has various methods for connecting and disconnecting signals
                to the agent's graph.
                	3/ `UPDATE_NODE_ATTR`, `UPDATE_NODE`, `DELETE_NODE`, `UPDATE_EDGE`,
                `UPDATE_EDGE_ATTR`, and `DELETE_EDGE`: These are various signal
                names that can be connected to the agent's graph using the `signals`
                object. These signals can be used to notify the agent of different
                events, such as node updates, edge updates, node deletion, etc.
                	4/ `compute`: This is a method that is called by the timer when
                the ` Period ` variable is reached. The `compute` method performs
                some computation or processing tasks.
                	5/ `timer`: This is an instance of the `timer` class, which
                provides a way to schedule the agent's execution at regular
                intervals. The `timer` object has various methods for starting and
                stopping the timer, as well as for updating the ` Period ` variable.
                	6/ `Period`: This is a variable that represents the interval
                between each iteration of the agent's computation. It is used to
                determine how often the agent should execute its `compute` method.

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
        
        # Se lee el ID de EBO del grafo
        id_ebo = self.g.get_id_from_name("EBO")

        # Se crea el nodo TTS (si no existe)y se almacenan tanto el nodo en si como su id
        if self.g.get_id_from_name("TTS") is not None:
            tts_node = self.g.get_node("TTS")
            id_tts = self.g.get_id_from_name("TTS")
        else:
            tts_node, id_tts = self.create_node("tts", "TTS")

        # Creación del edge
        self.create_edge(id_ebo, id_tts, "has")

        # Modificar atributo intento
        self.last_text = "¡Hola mundo!"
        tts_node.attrs["to_say"] = Attribute(self.last_text, self.agent_id)
        print("Atributo modificado")
        self.g.update_node(tts_node)
        print("Nodo actualizado")

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    # Crea al nodo pasándole strings que contienen el tipo del nodo y el nombre que aparecerá en el DSR;
    # y devuelve el nodo y su id (hay que almacenarlos: xxx_node, id_xxx = self.create_node("tipo", "nombre"))
    def create_node(self, type, name):
        """
        Takes in an instance of `Node`, creates a new node in the graph with the
        given `agent_id`, `type`, and `name`, and returns both the newly created
        node and its ID.

        Args:
            type (str): type of the newly created node in the graph.
            name (str): name of the new node that is being created in the graph.

        Returns:
            instance of `Node: a pair of nodes, where the first node represents
            the newly created node and the second node represents the ID of the
            newly created node.
            
            		- `new_node`: The created node object with its attributes (agent ID,
            type, and name).
            		- `id_node`: The ID of the newly created node in the graph.

        """
        new_node = Node(agent_id=self.agent_id, type=type, name=name)
        id_node = self.g.insert_node(new_node)
        print("Nodo ", name, " creado con ID: ", id_node)
        return new_node, id_node

    # Crea un edge introduciéndole origen, destino y tipo:
    # Ej: self.create_edge(x_id, y_id, "tipo")
    def create_edge(self, fr, to, type):
        """
        Inserts or assigns an edge into the graph based on the provided parameters.

        Args:
            fr (str): origin of the edge being created in the Graph.
            to (str): 2nd vertex of the new edge that is being created in the graph.
            type (str): type of edge being created, which can be one of the
                predefined edge types or a custom type defined by the user.

        """
        new_edge = Edge(to, fr, type, self.agent_id)
        cr_edge = self.g.insert_or_assign_edge(new_edge)
        print("Creado edge tipo ", type, " de ", fr, " a ", to)

    # Función que contiene y ejecuta todo lo necesario para generar el audio TTS a partir del texto y reproducirlo. Con la nueva voz del TTS.
    def new_tts(self, text):
        # Función para dividir el texto en partes más pequeñas
        """
        1) splits the input text into parts, 2) generates audio files for each
        part using a TTS model, and 3) adds the audio files to a queue for reproduction.

        Args:
            text (str): text to be split into parts for audio generation.

        Returns:
            list: a list of audio files generated from the given text, ready to
            be played.

        """
        def split_text(text):
            """
            Splits a given text into multiple parts based on specified rules,
            including finding the first dot, exclamation point, or question mark
            after 75 characters for the first and second part, and after 150
            characters for subsequent parts. It appends each part to a list and
            moves the starting position to the next point of division.

            Args:
                text (str): sequence of characters that the function will analyze
                    and partition into parts based on predetermined rules.

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
            Uses a list of text parts (`text_parts`) and a list of output paths
            (`output_paths`) to generate audio files using a TTS model and store
            them in the given output paths. It also marks the end of the queue
            when the last output path is processed.

            Args:
                queue (`queue.py`.): sequence of file paths where the generated
                    audio will be saved.
                    
                    		- ` queue`: A `queue.Queue` object that holds audio files
                    generated by the TTS system.
                    		- `put()` method: This method adds an item to the end of the
                    queue. In this case, it adds the output path of the audio file
                    generated by the model.
                    		- `get()` method: This method removes and returns an item
                    from the front of the queue. It is used to process the next
                    item in the queue.
                    		- `empty()` method: This method checks whether the queue is
                    empty or not. If the queue is empty, the `generate_audio`
                    function will exit.
                    		- Other attributes/properties: The `queue` object may have
                    other attributes and properties that are not explicitly mentioned
                    in this explanation, such as the maximum size of the queue,
                    the time to wait before removing an item from the queue, etc.

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
            Receives an audio file path from a queue, plays it using the `play`
            function, and then updates the emotional motor proxy's talking status
            to false. It also releases the semaphore and marks the task as done
            in the queue.

            Args:
                queue (`Queuelib.Queue`.): message queue where the function processes
                    messages to play audio from.
                    
                    		- `get()` method: Returns the next element in the queue, if
                    any. If the queue is empty, it raises a `queue.Empty` exception.
                    		- `is_empty`: A boolean attribute indicating whether the
                    queue is empty or not.
                    		- `size`: An integer attribute representing the number of
                    elements currently stored in the queue.
                    		- `tasks_done`: An integer attribute representing the number
                    of tasks that have been completed by the queue's worker thread.
                    		- `max_task_size`: An optional integer attribute specifying
                    the maximum size of a task that can be added to the queue, in
                    bytes.

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
        Checks if the text queue is empty, if not it removes a message from the
        queue and performs tts on it and adds it to the end of the queue, then
        returns True.

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



    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        """
        Updates the attributes of a node in a graph based on the value of an attribute.

        Args:
            id (int): identifier of the node for which the attributes are being updated.
            attribute_names ([str]): attribute names of the TTS node to be updated,
                which are then printed in green using the `console.print()` method.

        """
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

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
        new_node = Node(agent_id=self.agent_id, type=type, name=name)
        id_node = self.g.insert_node(new_node)
        print("Nodo ", name, " creado con ID: ", id_node)
        return new_node, id_node

    # Crea un edge introduciéndole origen, destino y tipo:
    # Ej: self.create_edge(x_id, y_id, "tipo")
    def create_edge(self, fr, to, type):
        new_edge = Edge(to, fr, type, self.agent_id)
        cr_edge = self.g.insert_or_assign_edge(new_edge)
        print("Creado edge tipo ", type, " de ", fr, " a ", to)

    # Función que contiene y ejecuta todo lo necesario para generar el audio TTS a partir del texto y reproducirlo. Con la nueva voz del TTS.
    def new_tts(self, text):
        # Función para dividir el texto en partes más pequeñas
        def split_text(text):
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
            for i, part in enumerate(text_parts):
                output_path = output_paths[i]
                self.model.tts_to_file(part, self.speaker_ids['ES'], output_path, speed=self.speed)
                queue.put(output_path)
            # Marcar el final de la cola
            queue.put(None)

        # Función para reproducir el audio en orden
        def play_audio(queue):
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

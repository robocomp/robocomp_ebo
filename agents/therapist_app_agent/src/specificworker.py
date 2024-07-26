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

from PySide2.QtCore import QTimer, QObject, Signal, Slot
from PySide2.QtWidgets import QApplication, QMessageBox, QWidget
from rich.console import Console
from genericworker import *
import interfaces as ifaces
from PyQt5.uic import loadUi
from therapist import Ui_Dialog


sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *
import random



# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

from PySide2.QtUiTools import QUiLoader

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False, parent=None):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        self.main_window = QWidget()


        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 9
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            #signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
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

        # Configuración selección usuario. A futuro leer de una BBDD.
        jugadores_test = ["Enrique", "Eustaquio", "Eufrasio", "Antonio", "Amelio"]
        for jugador in jugadores_test:
            self.ui.comboBoxJugadores.addItem(jugador)

        # Configuración selección juego.
        juegos = ["Conversacional", "Verdadero o Falso"]
        for juego in juegos:
            self.ui.comboBoxJuego.addItem(juego)

        # CONFIGURACIÓN BOTONES
        self.ui.iniciarJ.clicked.connect(self.iniciarJuego)

        #ther_node = self.g.get_node("Therapist")
        #ther_node.attrs['automatic_mode'] = Attribute(True, self.agent_id)
        #ther_node.attrs['game_active'] = Attribute(False, self.agent_id)
        #self.g.update_node(ther_node)

    def iniciarJuego(self):
        usuario = self.ui.comboBoxJugadores.currentText()
        juego = self.ui.comboBoxJuego.currentText()

        # Crear el cuadro de diálogo
        dlg = QDialog(self)
        dlg.setWindowTitle("¿Comenzar juego?")

        # Crear los elementos dentro del cuadro de diálogo
        label = QLabel(f"¿Quieres comenzar el juego '{juego}' con el usuario '{usuario}'?", dlg)
        btn_yes = QPushButton('Sí', dlg)
        btn_no = QPushButton('No', dlg)

        # Configurar el layout del cuadro de diálogo
        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(btn_yes)
        vbox.addWidget(btn_no)
        dlg.setLayout(vbox)

        # Conectar los botones a funciones
        btn_yes.clicked.connect(lambda: self.iniciarJuegoPulsado(usuario, juego, dlg))
        btn_no.clicked.connect(dlg.reject)  # Cerrar el cuadro de diálogo

        # Mostrar el cuadro de diálogo y esperar a que se cierre
        dlg.exec_()


    def iniciarJuegoPulsado(self, usuario, juego,dlg):
        # Llamar a la función para iniciar el juego y cerrar cuadro de diálogo
        self.iniciarJuegoConfirmado(usuario, juego)
        dlg.accept()

    def iniciarJuegoConfirmado(self, usuario, juego):
        print("INICIAR JUEGO CON: ", juego, usuario)
        self.lanzar_juego_dsr(juego)
        dialog = TherapistOnTheLoop(self.main_window)  # Pasar la ventana principal como padre
        dialog.exec_()  # Ejecutar el diálogo

    def lanzar_juego_dsr(self, juego):
        if juego == "Conversacional":
            prompt = "Prompt del juego conversacional"
        else:
            prompt = "Prompt del juego verdadero o Falso"

        llm_node = self.g.get_node("LLM")
        if llm_node is None:
            print("No LLM")
            return False
        else:
            llm_node.attrs["in_llama"] = Attribute(prompt, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(llm_node)




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
        #print('Specific')

        return True


    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)






    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

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

class TherapistOnTheLoop(QDialog):
    textoActualizado = Signal(str) #Se define la señal
    _next_agent_id = 75  # ID inicial

    @classmethod
    def _generate_agent_id(cls):
        """Generar un nuevo ID único para el agente"""
        agent_id = cls._next_agent_id
        cls._next_agent_id += 1
        return agent_id

    def __init__(self, parent=None):
        super(TherapistOnTheLoop, self).__init__(parent)

        self.agent_id = self._generate_agent_id()
        print("---------------------------------------------", self.agent_id, "---------------------------------------------")
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            # signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            # signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            # signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            # signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            # signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        loader = QUiLoader()
        ui_file = 'src/therapist.ui'
        self.ui = loader.load(ui_file, self)
        self.parent_window = parent

        self.ui.hablaButton.clicked.connect(self.enviarTTS)
        self.ui.escuchaButton.clicked.connect(self.enviarASR)
        self.ui.pushButton.clicked.connect(self.finJuego)

        self.ui.autoMode.stateChanged.connect(self.autoModeStateChanged)

        #Leer valores iniciales
        llm_node = self.g.get_node("LLM")
        self.last_tts = llm_node.attrs["out_llama"].value

        asr_node = self.g.get_node("ASR")
        self.last_asr = asr_node.attrs["texto"].value

        # Conectar la señal al slot
        self.textoActualizado.connect(self.actualizar_texto_plaintextedit)

        self.cuadro = ""
        self.automatico = False

        # Inicia desactivado los botones y demás
        self.ui.hablaButton.setEnabled(False)
        self.ui.textoHablado.setEnabled(False)
        self.ui.escuchaButton.setEnabled(False)
        self.ui.textoEscuchado.setEnabled(False)

        # Pone el juego como activo
        self.actualizar_nodo("Therapist", "game_active", True)

        #title = "PRUEBA PRUEBITA PRUEBA"
        #title = f"{juego} - {usuario}"
        #self.setWindowTitle(title)

    def enviarTTS(self):
        texto = self.ui.textoHablado.toPlainText()
        self.actualizar_nodo("TTS", "to_say", texto)
        print("TTS Pulsado y Valor modificado")
        self.ui.textoHablado.setPlainText("Esperando recepción de nuevo texto...")
        self.ui.hablaButton.setEnabled(False)
        self.ui.textoHablado.setEnabled(False)

    def enviarASR(self):
        texto = self.ui.textoEscuchado.toPlainText()
        self.actualizar_nodo("LLM", "in_llama", texto)
        print("ASR Pulsado y Valor modificado")
        self.ui.textoEscuchado.setPlainText("En espera de volver a escuchar...")
        self.ui.escuchaButton.setEnabled(False)
        self.ui.textoEscuchado.setEnabled(False)

    def finJuego(self):
        print("Juego finalizado")
        # Pone todos los atributos vaciós, y pone el juego como desactivado.
        self.actualizar_nodo("Therapist", "game_active", False)
        self.actualizar_nodo("Therapist", "automatic_mode", False)
        self.actualizar_nodo("LLM", "in_llama", "")
        self.actualizar_nodo("LLM", "out_llama", "")
        self.actualizar_nodo("ASR", "texto", "")
        self.actualizar_nodo("ASR", "escuchando", False)
        self.actualizar_nodo("TTS", "to_say", "")
        self.close()

    def autoModeStateChanged(self, state):
        if state == Qt.Checked:
            print("Modo Automático está activado")
            self.automatico = True
            self.actualizar_nodo("Therapist", "automatic_mode", True)
            self.ui.hablaButton.setEnabled(False)
            self.ui.textoHablado.setEnabled(False)
            self.ui.escuchaButton.setEnabled(False)
            self.ui.textoEscuchado.setEnabled(False)
        else:
            print("Modo Automático está desactivado")
            self.automatico = False
            self.actualizar_nodo("Therapist", "automatic_mode", False)

    def actualizar_nodo(self, nodo, atributo, valor):
        node = self.g.get_node(nodo)
        if node is None:
            print("No " + nodo)
            return False
        else:
            node.attrs[atributo] = Attribute(valor, self.agent_id)
            self.g.update_node(node)

    def nuevo_llm_recibido(self):
        self.ui.hablaButton.setEnabled(True)
        self.ui.textoHablado.setEnabled(True)
        self.cuadro = "textoHablado"
        self.actualizar_texto_llm()

    def nuevo_asr_recibido(self):
        self.ui.escuchaButton.setEnabled(True)
        self.ui.textoEscuchado.setEnabled(True)
        self.cuadro = "textoEscuchado"
        self.actualizar_texto_asr()
        pass

    def actualizar_texto_llm(self):
        llm_node = self.g.get_node("LLM")
        texto = llm_node.attrs["out_llama"].value
        self.textoActualizado.emit(texto)

    def actualizar_texto_asr(self):
        llm_node = self.g.get_node("ASR")
        texto = llm_node.attrs["texto"].value
        self.textoActualizado.emit(texto)

    @Slot(str)
    def actualizar_texto_plaintextedit(self, texto):
        if self.cuadro == "textoHablado":
            self.ui.textoHablado.setPlainText(texto)
        elif self.cuadro == "textoEscuchado":
            self.ui.textoEscuchado.setPlainText(texto)
        else:
            pass



    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        # Aquí se actualizan los valores que recibe del ASR y del LLM en la app
        ther_node = self.g.get_node("Therapist")
        if ther_node.attrs["automatic_mode"].value == False:
            llm_node = self.g.get_node("LLM")
            if llm_node.attrs["out_llama"].value != self.last_tts and llm_node.attrs["out_llama"].value != "":
                self.last_tts = llm_node.attrs["out_llama"].value
                # Definir llamada a función correspondiente
                self.nuevo_llm_recibido()
            else:
                pass

            asr_node = self.g.get_node("ASR")
            if asr_node.attrs["texto"].value != self.last_asr and asr_node.attrs["texto"].value != "":
                self.last_asr = asr_node.attrs["texto"].value
                # Definir llamada a función correspondiente
                self.nuevo_asr_recibido()
            else:
                pass
        else:
            llm_node = self.g.get_node("LLM")
            self.last_tts = llm_node.attrs["out_llama"].value
            asr_node = self.g.get_node("ASR")
            self.last_asr = asr_node.attrs["texto"].value

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



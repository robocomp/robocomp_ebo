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
    """
    Initializes a worker for a specific agent, connects signals and slots, starts
    a timer, sets up combo boxes, and provides methods for starting a game, launching
    the DSR graph, and handling node updates.

    Attributes:
        Period (int): 2000 by default, indicating the time interval in milliseconds
            after which the worker's compute method is called using a QTimer.
        main_window (QWidget): Initialized in the `__init__` method. It appears
            to be the main window of the application, but its role in the context
            of the `SpecificWorker` class is unclear without more information about
            the overall architecture.
        agent_id (int): 9 by default, set in the `__init__` method. It seems to
            be used as a unique identifier for this specific worker agent.
        g (DSRGraph): Initialized with a node ID of 0, a name of "pythonAgent",
            and the agent ID of 9. It seems to be used for managing nodes and edges
            in a graph.
        startup_check (bool): Used to perform a startup check operation when its
            value is True, which involves stopping the application after a delay
            of 200 milliseconds using `QTimer.singleShot`.
        timer (QTimer): Started with a period of `self.Period` (2000 milliseconds)
            in its `__init__` method. The `compute` method is connected to this
            timer, which means it will be executed periodically.
        compute (QtCoreSlot): Bound to a method with the same name. The method
            does not have any side effects, as it always returns True.
        ui (object): Not defined in this code snippet. It seems to be a UI element,
            possibly from PyQt or another GUI library, but its definition is missing.
        iniciarJuego (Callable[[QWidget],None]): Associated with a QPushButton in
            the UI. It gets triggered when the 'Iniciar J' button is clicked,
            prompting the user to start a game.

    """
    def __init__(self, proxy_map, startup_check=False, parent=None):
        """
        Initializes an instance with a proxy map, sets up GUI components, connects
        signals to methods for handling graph updates and game initialization, and
        starts a timer for periodic computations.

        Args:
            proxy_map (Dict[str, any]): Passed to the superclass method
                `super(SpecificWorker, self).__init__(proxy_map)`, indicating that
                it represents a mapping from proxy objects to their corresponding
                worker processes.
            startup_check (bool): Set to `False` by default. It determines whether
                the `startup_check` method should be called or not, effectively
                controlling the flow of execution.
            parent (QWidget | None): Passed as an argument when creating an instance
                of SpecificWorker. It represents the parent widget of the specific
                worker, which defaults to None if not provided.

        """
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
        """
        Initiates a game by displaying a modal dialog asking if the user wants to
        start the selected game with the chosen player. The dialog has two buttons:
        "Sí" (Yes) and "No".

        """
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
        """
        Initiates a game for a given user and game, confirms the initiation with
        a separate dialog box (`dlg`), and then accepts the confirmation through
        a call to `dlg.accept()`.

        Args:
            usuario (object): Passed to this method along with `juego` and `dlg`.
                It represents an instance of a user, likely used for identifying
                the player in the game.
            juego (object): Expected to be a reference to an instance of a class
                representing a game. It is used as input for initiating a game.
            dlg (QDialog): Passed as an argument to the function. It seems that
                `dlg` represents a dialog box that needs to be accepted after
                certain actions have been confirmed.

        """
        self.iniciarJuegoConfirmado(usuario, juego)
        dlg.accept()

    def iniciarJuegoConfirmado(self, usuario, juego):
        """
        Initiates a game with the specified juego and usuario, then launches a
        DS-R game mode using `lanzar_juego_dsr`. Following this, it executes a
        therapist-on-the-loop dialog in the main window.

        Args:
            usuario (object): Used to represent a user, which presumably plays or
                participates in the game `juego`. Its exact nature or properties
                are not specified within this code snippet.
            juego (str): Expected to represent the name or identifier of the game
                being initiated.

        """
        print("INICIAR JUEGO CON: ", juego, usuario)
        self.lanzar_juego_dsr(juego)
        dialog = TherapistOnTheLoop(self.main_window)  # Pasar la ventana principal como padre
        dialog.exec_()  # Ejecutar el diálogo

    def lanzar_juego_dsr(self, juego):
        """
        Determines the prompt for a game based on its type and sets an attribute
        "in_llama" on a node named "LLM" with the determined prompt, updating the
        graph if necessary.

        Args:
            juego (str | "Conversacional" | "Verdadero o Falso"): Used to determine
                which prompt should be assigned to the attribute.

        Returns:
            bool: `False` if there is no LLM node in the graph or if it fails to
            modify the attribute of the LLN node, otherwise it doesn't explicitly
            return any value.

        """
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
        """
        Sets parameters without handling exceptions, returning `True` regardless
        of success or failure. This approach can mask potential errors and make
        debugging more challenging.

        Args:
            params (Dict[any, any]): Used to set parameters within an object or
                class. The exact meaning and usage of this parameter depend on the
                context in which it is called.

        Returns:
            bool: `True`. This indicates that the operation was successful and
            there were no errors.

        """
        return True


    @QtCore.Slot()
    def compute(self):
        #print('Specific')

        """
        Returns a boolean value, indicating successful computation. The method is
        decorated with the `@QtCore.Slot()` decorator, implying that it's designed
        to be executed as a slot in the Qt framework, likely within a larger
        computational context.

        Returns:
            bool: 1 (True) when executed, indicating that the computation was successful.

        """
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
    """
    Implements a graphical user interface for a conversation game between a therapist
    and a patient using natural language processing (NLP) techniques. It manages
    nodes and edges in a graph data structure, updating node attributes and handling
    button clicks to facilitate the conversation flow.

    Attributes:
        textoActualizado (Signal[str]): Used to emit signals with a string value
            when there are changes in text attributes of nodes "LLM" or "ASR".
        _next_agent_id (int): 75 by default. It appears to be used as a counter
            for generating unique agent IDs when creating new instances of the class.
        agent_id (int): 75 by default, generated using the `_generate_agent_id` method.
        _generate_agent_id (int): 75 by default. It generates a new unique agent
            ID for each instance of the class and increments it for each subsequent
            call.
        g (DSRGraph): Initialized with parameters (0, "pythonAgent", self.agent_id)
            in the __init__ method.
        update_node_att (None|int|list[str]): Connected to the UPDATE_NODE_ATTR
            signal of the DSRGraph class. It updates node attributes based on the
            received signal.
        ui (QMainWindow): Loaded from a UI file named 'therapist.ui' using the
            QUiLoader class. It represents the graphical user interface (GUI) of
            the application.
        parent_window (QMainWindow|None): Set during the initialization of the
            class. It appears to represent the parent window of this dialog.
        enviarTTS (method): Called when the "Habla" button is clicked. It sends a
            text to the node "TTS" with the value of the text from the "Texto
            Hablado" field.
        enviarASR (None|self,noreturnvalue): Used to send the text from the UI's
            `textoEscuchado` plaintext edit to a node named "LLM" in the graph,
            updating its "in_llama" attribute.
        finJuego (None): Connected with the `finJuego` method, which gets called
            when the corresponding button is clicked in the UI. This method sets
            various nodes and attributes to their initial state and closes the dialog.
        autoModeStateChanged (voidQtCheckStateNone): Connected to the stateChanged
            signal of the ui.autoMode checkbox. It updates the automatic mode
            status in the graph and enables/disables buttons according to the new
            state.
        last_tts (str): Used to store the last text-to-speech (TTS) output from
            the LLM node in the DSRGraph.
        last_asr (str): Assigned the value of "ASR" node's "texto" attribute when
            it changes, indicating the last recognized speech. It keeps track of
            the most recent ASR output.
        actualizar_texto_plaintextedit (Slot[str]): Used to update a plain text
            edit with a given text. It sets the text of either `self.ui.textoHablado`
            or `self.ui.textoEscuchado` based on the value of `self.cuadro`.
        cuadro (str|None): Used to store the name of the text box where the received
            text should be displayed, which can either be "textoHablado" or "textoEscuchado".
        automatico (bool): Used to represent whether the game mode is set to
            automatic or not. It can be toggled on or off through the user interface,
            enabling or disabling certain functionality.
        actualizar_nodo (Nonebool): A method used to update the attributes of nodes
            in the graph.

    """
    textoActualizado = Signal(str) #Se define la señal
    _next_agent_id = 75  # ID inicial

    @classmethod
    def _generate_agent_id(cls):
        """Generar un nuevo ID único para el agente"""
        agent_id = cls._next_agent_id
        cls._next_agent_id += 1
        return agent_id

    def __init__(self, parent=None):
        """
        Initializes the object, generates an agent ID, creates a DSRGraph instance,
        connects signals for updating node attributes and handles UI elements'
        click events to send TTS and ASR requests, update text fields, and manage
        game state.

        Args:
            parent (TherapistOnTheLoop | None): Used to set the parent window for
                the current instance. It is passed as an argument when creating
                an object of this class.

        """
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
        """
        Updates a node with a text-to-speech (TTS) instruction, sets the UI to
        indicate waiting for new input, and disables buttons and text editing
        capabilities until new input is received.

        """
        texto = self.ui.textoHablado.toPlainText()
        self.actualizar_nodo("TTS", "to_say", texto)
        print("TTS Pulsado y Valor modificado")
        self.ui.textoHablado.setPlainText("Esperando recepción de nuevo texto...")
        self.ui.hablaButton.setEnabled(False)
        self.ui.textoHablado.setEnabled(False)

    def enviarASR(self):
        """
        Sends the text recognized by an Automatic Speech Recognition (ASR) system
        to a specified node, updates its internal state, disables some UI elements,
        and displays a waiting message.

        """
        texto = self.ui.textoEscuchado.toPlainText()
        self.actualizar_nodo("LLM", "in_llama", texto)
        print("ASR Pulsado y Valor modificado")
        self.ui.textoEscuchado.setPlainText("En espera de volver a escuchar...")
        self.ui.escuchaButton.setEnabled(False)
        self.ui.textoEscuchado.setEnabled(False)

    def finJuego(self):
        """
        Prints a message indicating the game's end, then updates several nodes
        with specific values and sets certain flags to False, before closing the
        dialog box.

        """
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
        """
        Updates the state of the automatic mode when the corresponding checkbox
        changes its state. If the mode is activated, it prints a message and
        enables/disables certain UI elements accordingly; if deactivated, it prints
        another message and updates the automatic mode state.

        Args:
            state (Qt.Checked | Qt.Unchecked): Passed to this method. It represents
                whether the automatic mode check box has been checked or unchecked,
                indicating its current state.

        """
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
        """
        Updates an existing node in a graph with a new attribute value. It retrieves
        a node by its identifier, sets the attribute if the node exists, and then
        updates the node in the graph.

        Args:
            nodo (str | int): Expected to be a valid node ID, either as a string
                or an integer, which identifies a node in the graph. It serves as
                an input for retrieving the corresponding node object from the graph.
            atributo (str | None): Used to specify the attribute name to be updated
                for the given `nodo`. It represents the key for the attribute-value
                pair to be added or modified in the node's attributes.
            valor (str | int | bool): Used to set an attribute value for a node.
                It represents the new value that will be assigned to the specified
                `atributo` of the `nodo`.

        Returns:
            bool: 0 (False). If the nodo does not exist in the graph, it prints a
            message and returns False; otherwise, it updates the node's attribute
            and returns without printing any messages.

        """
        node = self.g.get_node(nodo)
        if node is None:
            print("No " + nodo)
            return False
        else:
            node.attrs[atributo] = Attribute(valor, self.agent_id)
            self.g.update_node(node)

    def nuevo_llm_recibido(self):
        """
        Enables two user interface elements (hablaButton and textoHablado) and
        sets a variable cuadro to "textoHablado". It then calls another method
        actualizar_texto_llm() to update the text.

        """
        self.ui.hablaButton.setEnabled(True)
        self.ui.textoHablado.setEnabled(True)
        self.cuadro = "textoHablado"
        self.actualizar_texto_llm()

    def nuevo_asr_recibido(self):
        """
        Enables two UI components, sets a string variable to "textoEscuchado", and
        calls another method named `actualizar_texto_asr`. This function appears
        to be part of an audio recognition system, responding to new ASR (Automatic
        Speech Recognition) inputs.

        """
        self.ui.escuchaButton.setEnabled(True)
        self.ui.textoEscuchado.setEnabled(True)
        self.cuadro = "textoEscuchado"
        self.actualizar_texto_asr()
        pass

    def actualizar_texto_llm(self):
        """
        Retrieves the value of an attribute called "out_llama" from a node labeled
        as "LLM" within a graph, and then emits this value to a signal named `textoActualizado`.

        """
        llm_node = self.g.get_node("LLM")
        texto = llm_node.attrs["out_llama"].value
        self.textoActualizado.emit(texto)

    def actualizar_texto_asr(self):
        """
        Retrieves text from an attribute named "texto" within a node labeled "ASR"
        and emits this text as a signal to be handled by other parts of the application.

        """
        llm_node = self.g.get_node("ASR")
        texto = llm_node.attrs["texto"].value
        self.textoActualizado.emit(texto)

    @Slot(str)
    def actualizar_texto_plaintextedit(self, texto):
        """
        Updates the plain text content of either the `textoHablado` or `textoEscuchado`
        widgets, depending on the value of the `cuadro` attribute. If neither
        condition matches, it does nothing.

        Args:
            texto (str): Expected to be passed as an argument when this method is
                called, representing a string that will be set as plain text in
                one of the UI elements.

        """
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
        """
        Updates the values of last ASR and TTS outputs from LLM and ASR nodes,
        respectively, when the therapist node is not in automatic mode, and resets
        these values when it is in automatic mode.

        Args:
            id (int): Not used within the function. Its presence seems unnecessary,
                possibly indicating an incomplete or unfinished code.
            attribute_names ([str]): Not used within the function's logic. It seems
                to be an unused variable, possibly leftover from previous code
                revisions or for future implementation purposes.

        """
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



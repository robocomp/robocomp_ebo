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

import os
import time


sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        """
        Sets up an instance of a specific worker class, initializing its fields
        and connecting it to various signals for updating node attributes, nodes
        themselves, edges, edge attributes, and implementing startup checks and a
        timer for periodical computation.

        Args:
            proxy_map (dict): mapping of original agent IDs to new unique IDs,
                which are used for identifying the worker instance within the
                DSRGraph framework.
            startup_check (bool): functionality that should be performed when the
                agent is started, which may include initialization, configuration,
                or other custom logic.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

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
        
        self.aux=""

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
        Computes and implements code for various games within a framework. It
        offers different choices and executes specific activities depending on
        user input, such as showing a menu, requesting input, confirming selections,
        and performing various robotics-related tasks using the Python API
        "python-innermodel" and other libraries.

        Returns:
            bool: a boolean value indicating whether the computation was successful.

        """
        while True:
            self.mostrar_menu()
            opcion = input("Ingrese el número del juego que desea jugar: ").strip()
            
            if opcion == "1":
                if self.confirmar_seleccion("Secuencias de AVDB"):
                    self.aux=""
                    self.juego1()
                    
            elif opcion == "2":
                if self.confirmar_seleccion("El verdadero o falso de las AVDB"):
                    self.aux=""
                    self.juego2()
                    
            elif opcion == "3":
                if self.confirmar_seleccion("La compra"):
                    self.aux=""
                    self.juego3()
                    
            else:
                self.clear_screen()
                self.aux = "Opción no válida. Por favor, intente de nuevo."
        # computeCODE
        # try:
        #   self.differentialrobot_proxy.setSpeedBase(100, 0)
        # except Ice.Exception as e:
        #   traceback.print_exc()
        #   print(e)

        # The API of python-innermodel is not exactly the same as the C++ version
        # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
        # z = librobocomp_qmat.QVec(3,0)
        # r = self.innermodel.transform('rgbd', z, 'laser')
        # r.printvector('d')
        # print(r[0], r[1], r[2])

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)
    
    
    def clear_screen(self):
        os.system('clear')
        
    def cerrar_juego(self):
        """
        Prints a message and sleeps for 5 seconds before clearing the screen.

        """
        print("Cerrando el juego, por favor, espere")
        time.sleep(5)
        self.clear_screen()


    def actualizar_prompt(self, prompt):
        """
        Updates an LLM node's `in_llama` attribute with the provided prompt and
        agent ID, and prints a message indicating the modification was made to the
        LLM node.

        Args:
            prompt (`Attribute`.): attribute value that will be assigned to the
                `in_llama` attribute of the `LLM` node.
                
                		- `prompt`: A dictionary containing the data to be updated in
                the LLM node. The key-value pair structure is represented as a
                serialized JSON object.
                		- `self.agent_id`: An integer value representing the agent ID
                of the LLM owner. It is used as an attribute in the updated `llm_node`.

        Returns:
            bool: "Atributo modificado".

        """
        llm_node = self.g.get_node("LLM")
        if llm_node is None:
            print("No LLM")
            return False
        else:
            llm_node.attrs["in_llama"] = Attribute(prompt, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(llm_node)
        

    def juego1(self):
        """
        Initializes and displays a simple game with a prompt, and then terminates
        the game and clears the screen after user input.

        """
        self.clear_screen()
        print("Bienvenido al Juego: Secuencias de AVDB")
        
        prompt = "Aquí iría el prompt del juego"
        self.actualizar_prompt(prompt)
        
        input("Juego en curso, pulsa Enter para cerrarlo y volver al menú...")
        self.clear_screen()
        self.cerrar_juego()
        

    def juego2(self):
        """
        Clears the screen, displays a prompt, updates the prompt, and then closes
        the game after the user presses enter.

        """
        self.clear_screen()
        print("Bienvenido al Juego: El verdadero o falso de las AVDB")
        
        prompt = "Aquí iría el prompt del juego"
        self.actualizar_prompt(prompt)
        
        input("Presiona Enter para volver al menú...")
        self.clear_screen()
        self.cerrar_juego()

    def juego3(self):
        """
        Clears the screen, displays a prompt, and prompts the user to press enter
        to return to the menu.

        """
        self.clear_screen()
        print("Bienvenido al Juego: La compra")
        
        prompt = "Aquí iría el prompt del juego"
        self.actualizar_prompt(prompt)
        
        input("Presiona Enter para volver al menú...")
        self.clear_screen()
        self.cerrar_juego()


    def confirmar_seleccion(self, juego):
        """
        Is a simple program that prompts the user to select a game and then checks
        if they want to continue or exit the menu. If the user chooses to continue,
        it returns `True`, otherwise it returns `False`.

        Args:
            juego (str): selected game for which the function will print the chosen
                game's name and then prompt the user to start or return to the menu.

        Returns:
            True` value: `True` when the user presses Enter, and `False` otherwise.
            
            	1/ `decision`: This variable stores the user's input, which is either
            "entrer" for confirming the selection or "salir" for returning to the
            menu.
            	2/ `return_value`: The value returned by the function, which indicates
            whether the selection was confirmed or not. If the user chose "salir",
            this variable will be `False`, otherwise it will be `True`.

        """
        self.clear_screen()
        print(f"Has elegido {juego}.")
        decision = input("Pulsa Enter para iniciar o escribe 'salir' para volver al menú: ").strip().lower()
        if decision == 'salir':
            return False
        return True

    def mostrar_menu(self):
        """
        Prints a menu with options for the user to select a game to play.

        """
        self.clear_screen()
        print(self.aux)
        print("Seleccione un juego:")
        print("1. Secuencias de AVDB")
        print("2. El verdadero o falso de las AVDB")
        print("3. La compra")






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

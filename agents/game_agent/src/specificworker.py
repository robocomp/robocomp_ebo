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
        Sets up an instance of the `SpecificWorker` class, defining its Period and
        agent ID, and connecting signals to update various node and edge attributes
        in a DSRGraph.

        Args:
            proxy_map (`object`.): map of proxies that will be used to access the
                DSRGraph, allowing for the creation of agents that can communicate
                with other agents and nodes in the graph using different proxy addresses.
                
                		- ` proxy_map`: This is a dictionary-like object that maps proxy
                IDs to their corresponding agent ID.
                		- `Period`: This is an integer representing the time interval
                between updates in milliseconds.
                		- `agent_id`: This is an integer that represents the unique ID
                of the agent. It must be set to a valid unique value in your deployment.
            startup_check (int): initialization of the agent, where the agent will
                perform an additional check during the startup phase.

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
        Manages user input, calls specific games depending on the input option and
        updates the robot's transform values using the InnerModel API.

        Returns:
            True: a boolean value indicating whether the given command was successful.
            
            		- `True`: This is the value returned by the `compute` function
            indicating that the computation was successful.
            		- `self.mostrar_menu()`: This is a call to a method within the `
            compute` function that displays a menu for the user to select a game
            to play.
            		- `opcion`: This variable is set to the input value selected by the
            user from the menu displayed earlier.
            		- `if self.confirmar_seleccion("Secuencias de AVDB")` : This is a
            conditional statement that checks if the user has confirmed their
            selection of the "Sequences of AVDB" option. If confirmed, the
            `self.juego1()` method is called.
            		- `elif opcion == "2"` : This is an optional conditional statement
            that checks if the user has selected the "True or False: AVDB" option.
            If confirmed, the `self.juego2()` method is called.
            		- ` elif opcion == "3"` : This is an optional conditional statement
            that checks if the user has selected the "Buy" option. If confirmed,
            the `self.juego3()` method is called.
            		- `else` : This statement is executed if none of the above conditions
            are true. In this case, the `self.clear_screen()` method is called and
            the variable `self.aux` is set to the message "Invalid selection.
            Please try again."
            
            	Overall, the output returned by the `compute` function reflects the
            user's input and the subsequent actions that are taken based on that
            input.

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
        Ends the game by displaying a message and sleeping for 5 seconds before
        clearing the screen.

        """
        print("Cerrando el juego, por favor, espere")
        time.sleep(5)
        self.clear_screen()


    def actualizar_prompt(self, prompt):
        """
        Modifies the `in_llama` attribute of an LLM node based on a given prompt
        and agent ID, updates the LLM node in the graph, and prints "Atributo modificado".

        Args:
            prompt ("Attribute" object.): attribute name that is assigned to the
                LLM node upon modification.
                
                		- `prompt`: The input deserialized from JSON.
                		- `self.agent_id`: A string attribute representing the unique
                identifier of the agent that modified the attribute.

        Returns:
            bool: a message indicating that an attribute has been modified and the
            LLM node has been updated in the graph.

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
        Clears the screen, displays a welcome message, updates the prompt, and
        requests the user to press Enter to close the game and return to the menu.

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
        Clears the screen, displays a prompt, updates the prompt, and ends the
        game with an input prompt.

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
        Displays a welcome message, updates the game prompt, and returns the player
        to the menu after entering "Enter".

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
        Allows the user to confirm their selection and proceed with the game or
        exit the menu. It takes no arguments and returns a boolean value based on
        the user's input.

        Args:
            juego (str): game that the user has chosen, which is used to determine
                the outcome of the function.

        Returns:
            int: a boolean value indicating whether the user has confirmed their
            selection.

        """
        self.clear_screen()
        print(f"Has elegido {juego}.")
        decision = input("Pulsa Enter para iniciar o escribe 'salir' para volver al menú: ").strip().lower()
        if decision == 'salir':
            return False
        return True

    def mostrar_menu(self):
        """
        Presents a menu with three options to the user: "Secuencias de AVDB", "El
        verdadero o falso de las AVDB", and "La compra".

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

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


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        """
        Initializes a SpecificWorker class instance, creating a graph and setting
        its attributes, connecting signals for updating node and edge attributes,
        and starting a timer for periodic computation.

        Args:
            proxy_map (dict): 2-tuple (Graph, agent ID), where Graph is an instance
                of the `DSRGraph` class and agent ID is a unique integer that
                identifies the particular instance of the `SpecificWorker` class
                in the deployment.
            startup_check (`object`.): functionality to perform when the agent is
                started for the first time.
                
                		- `startup_check`: A boolean property that determines whether
                the function should perform a check during startup. Its default
                value is `True`.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 11
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)

        # Se lee el nodo del grafo
        llm_node = self.g.get_node("LLM")

        # Se guardan los valores iniciales
        print("Cargando valores iniciales del atributo escuchando")
        self.last_in = llm_node.attrs["in_llama"].value
        self.last_out = llm_node.attrs["out_llama"].value

        # Comprobación de esta carga de valores iniciales del grafo
        if self.last_in == llm_node.attrs["in_llama"].value and self.last_out == llm_node.attrs["out_llama"].value:
            print("Valores iniciales cargados correctamente")
        else:
            print("Error al cargar los valores iniciales")

        asr_node = self.g.get_node("ASR")
        self.last_texto = asr_node.attrs["texto"].value

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


    ######################
    # From the RoboCompLLM you can call this methods:
    # self.llm_proxy.generateResponse(...)

    # Actualiza llama_out con la respuesta generada
    def actualizar_out(self,respuesta_gen):
        """
        Modifies the attribute "out_llama" for a given LLM node in the graph, based
        on the input `respuesta_gen`.

        Args:
            respuesta_gen (Attribute value.): attribute value to be assigned to
                the "out_llama" attribute of the LLM node.
                
                		- `respuesta_gen`: A deserialized Python object with attributes
                representing the output of an LLM model. The exact structure and
                properties of this object depend on the specific implementation
                and architecture of the LLM model used in the `actualizar_out` function.
                
                	Without further context or information, it is not possible to
                provide a comprehensive summary or analysis of `respuesta_gen`.
                As such, this answer remains limited to less than 100 words and
                focuses on explaining the structure and properties of `respuesta_gen`
                as provided in the input to the function.

        Returns:
            Attribute` object, which represents an modified attribute value of the
            LLM node: "Atributo modificado".
            
            	1/ `respuesta_gen`: This is an Attribute instance, which represents
            the response generated by the agent.
            	2/ `self.agent_id`: This is an integer value that identifies the agent
            responsible for generating the response.

        """
        llm_node = self.g.get_node("LLM")
        if llm_node is None:
            print("No LLM")
            return False
        else:
            llm_node.attrs["out_llama"] = Attribute(respuesta_gen, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(llm_node)

    # Pone vacío llama_in; esto es por si acaso se repite una respuesta del jugador (Dos veces de seguido Verdadero por ejemplo)
    def borrar_in(self):
        """
        Updates an LLM node's attribute "in_llama" with a new value, and then
        prints a message indicating that the attribute has been modified. If the
        LLM node is not found, it returns False.

        Returns:
            bool: a string indicating whether the LLM was successfully updated or
            not.

        """
        llm_node = self.g.get_node("LLM")
        if llm_node is None:
            print("No LLM")
            return False
        else:
            llm_node.attrs["in_llama"] = Attribute("", self.agent_id)
            print("Atributo modificado")
            self.g.update_node(llm_node)

    def actualizar_in(self,nuevo):
        """
        Updates an attribute "in_llama" in a specific node (representing an LLM)
        based on a nuevo value provided, and prints a message to confirm the update
        has been made to the graph.

        Args:
            nuevo (`Attribute` object.): new attribute value for the LLM node.
                
                		- `self.agent_id`: The identifier of the agent that owns the LLM
                node.
                		- `nuevo`: A dictionary-like object representing the new attributes
                to be updated in the LLM node.

        Returns:
            bool: "Atributo modificado".

        """
        llm_node = self.g.get_node("LLM")
        if llm_node is None:
            print("No LLM")
            return False
        else:
            llm_node.attrs["in_llama"] = Attribute(nuevo, self.agent_id)
            print("Atributo modificado")
            self.g.update_node(llm_node)


    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        """
        Updates the attributes of a node based on the value of an internal attribute.
        It compares the current value of the node's internal attribute with the
        previous value, and if they differ, it sets the new value as the last used
        value for that attribute and calls the `actualizar_in` function to update
        the internal state. If the internal attribute value does not change, the
        function simply passes.

        Args:
            id (int): ID of the node being updated, which is used to identify the
                node in the graph.
            attribute_names ([str]): names of the attributes to update in the
                nodes, which are retrieved from the graph's node objects through
                the `get_node()` method.

        """
        asr_node = self.g.get_node("ASR")
        if asr_node.attrs["texto"].value != self.last_texto:
            self.last_texto = asr_node.attrs["texto"].value
            self.actualizar_in(self.last_texto)
        else:
            pass

        llm_node = self.g.get_node("LLM")
        if llm_node.attrs["in_llama"].value != self.last_in:
            if llm_node.attrs["in_llama"].value != "":
                self.last_in = llm_node.attrs["in_llama"].value
                #respuesta = "Funciona"# Incluir aquí función para generar respuesta, que lo almacene en una variable
                #self.actualizar_out(respuesta)
                self.borrar_in()
            else:
                pass

        else:
            pass
        #console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

    def update_node(self, id: int, type: str):
        """
        Updates the last output value of a node based on its attributes, and then
        passes it to the next node for processing.

        Args:
            id (int): current state of the node, which is used to determine whether
                the `actualizar_to_say()` method should be called or not.
            type (str): type of text being processed in the `ASR` node, which
                determines whether or not to update the output of the function.

        """
        asr_node = self.g.get_node("ASR")
        if asr_node.attrs["texto"].value != self.last_texto:
            self.last_out = llm_node.attrs["out_llama"].value
            self.actualizar_to_say(self.last_out)
        else:
            pass

    def delete_node(self, id: int):
        console.print(f"DELETE NODE:: {id} ", style='green')

    def update_edge(self, fr: int, to: int, type: str):

        console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')

    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')

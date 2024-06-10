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
        Initializes a `DSRGraph` object, setting the agent ID and graph topology.
        It also reads initial node attributes, sets up signal connections for
        attribute updates and timer for automatic computation.

        Args:
            proxy_map (`object`.): graph structure of the original code, which is
                used to create the DSRGraph object in the function.
                
                	1/ `self.Period`: The period of time in milliseconds to update
                the graph.
                	2/ `self.agent_id`: A unique integer ID for this agent in the deployment.
                	3/ `self.g`: A DSRGraph object representing the graph.
                	4/ `llm_node`: A Node object representing the LLama node in the
                graph.
                	5/ `asr_node`: A Node object representing the ASR node in the graph.
                	6/ `signals`: An instance of Signal class, which can be used to
                connect signals to the graph.
            startup_check (bool): Whether the check should run during startup,
                which if set to `True`, will execute the `startup_check()` method
                and perform the necessary initializations and checks, otherwise
                it will omit this step.

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
        Updates an LLM node's `out_llama` attribute with a new value and prints a
        message indicating that the attribute has been modified.

        Args:
            respuesta_gen (Attribute object.): attribute value to be assigned to
                the "out_llama" attribute of the LLM node in the graph.
                
                		- `respuesta_gen`: A Python object that contains the generated
                response for the LLM node. It is an instance of the `Attribute`
                class with several attributes, including `self.agent_id`.

        Returns:
            Attribute` object: a modified LLM node with an updated "out_llama" attribute.
            
            		- `print("Atributo modificado")`: This statement is used to print a
            message indicating that the "out_llama" attribute of the LLM node has
            been modified.
            		- `llm_node.attrs["out_llama"] = Attribute(respuesta_gen, self.agent_id)`:
            This line sets the value of the "out_llama" attribute of the LLM node
            to an instance of the `Attribute` class, which represents the response
            generated by the agent. The `self.agent_id` variable is used to provide
            the id of the agent that generated the response.
            		- `self.g.update_node(llm_node)`: This line updates the LLM node in
            the graph with the modified attribute value.

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
        Modifies the attribute "in_llama" of the LLM node and updates the node in
        the graph.

        Returns:
            False` value: "Atributo modificado".
            
            	1/ `print("Atributo modificado")`: This statement is used to print a
            message indicating that an attribute has been modified in the LLM node.
            	2/ `self.g.update_node(llm_node)`: This statement updates the LLM
            node in the graph with the modified attributes.
            
            	The output returned by the `borrar_in` function is a boolean value
            indicating whether the LLM node was found and modified.

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
        Modifies the "in_llama" attribute of an LLM node in the graph, based on a
        new value provided as input.

        Args:
            nuevo (`Attribute`.): new value of the "in_llama" attribute for the
                LLM node in the graph.
                
                		- `nuevo`: A dictionay-like object representing the updated LLM
                attributes.
                		- `self.agent_id`: The ID of the agent that is modifying the
                LLM's attributes.

        Returns:
            False: a statement indicating that an attribute has been modified,
            followed by the update of the `LLM` node in the graph.
            
            		- `print("Atributo modificado")` - Indicates that an attribute has
            been modified in the LLM node.
            		- `llm_node.attrs["in_llama"] = Attribute(nuevo, self.agent_id)` -
            Modifies the "in_llama" attribute of the LLM node with a new value.
            		- `self.g.update_node(llm_node)` - Updates the node in the graph
            with the modified attributes.

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
        Updates the attributes of a node based on the values of other nodes in the
        graph, storing the new values in instance variables and calling an included
        function to generate a response.

        Args:
            id (int): node ID being processed by the function.
            attribute_names ([str]): names of the attributes that will be retrieved
                from the nodes in the graph for update operations.

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
        Updates a node based on its attributes, including `texto`, and passes any
        necessary output to the `actualizar_to_say` function.

        Args:
            id (int): ID of the ASR (Automatic Speech Recognition) node, which is
                used to retrieve the appropriate node from the graph.
            type (str): type of output to be generated by the function, which is
                then used to update the `last_out` attribute accordingly.

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

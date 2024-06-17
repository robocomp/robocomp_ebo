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

##################### Imports del LLM: #########################
from huggingface_hub import hf_hub_download
from langchain.llms.llamacpp import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
##########################################################################

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
        Initializes a SpecificWorker class instance, creating a DSRGraph object,
        setting its period, agent ID, and connecting signals for node and edge
        updates and deletions.

        Args:
            proxy_map (int): mapping of original nodes to proxies, which allows
                the agent to handle messages intended for different nodes in the
                graph.
            startup_check (bool): initial validation of the agent's startup state,
                which checks if the agent has already started its computation cycle
                before initiating the timeout loop.

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

        # Initialize LLM and conversation history
        self.init_llm()


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

    def format_docs(self, docs):
        """
        Concatenates page content from a list of `Docs` objects, separated by
        newline characters.

        Args:
            docs (sequence or collection of Page objects.): list of documents whose
                page contents are to be concatenated into a string.
                
                	* `docs`: A list of dict objects representing documentation pages.
                Each page is represented by a dictionary containing the following
                attributes:
                		+ `page_content`: The content of the documentation page as a string.

        Returns:
            undefined: a list of page contents from given documentation documents,
            separated by newlines.

        """
        text = ""
        for d in docs:
            text += f"- {d.page_content}\n"

        return text

    def init_llm(self):
        # Download model from Huggingface
        """
        Initializes a LLaMA model for generating text based on given input, and
        loads an embedding model to be used as the first stage in the chain for
        generating responses.

        """
        model_path = hf_hub_download(
            repo_id="lmstudio-community/Llama3-ChatQA-1.5-8B-GGUF",
            filename="ChatQA-1.5-8B-Q8_0.gguf",
            force_download=False
        )

        # Load the model
        self.llm = LlamaCpp(
            model_path=model_path,
            stop=["<|begin_of_text|>"],
            n_gpu_layers=-1,
            n_ctx=2048,
            max_tokens=2048,
            temperature=0.3,
            streaming=True
        )

        model_name = "mixedbread-ai/mxbai-embed-large-v1"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}

        embeddings_model = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        # Initialize conversation history
        self.db = Chroma(embedding_function=embeddings_model)

        retriever = self.db.as_retriever()

        self.db.add_texts([""])

        # create the prompt template
        template = """System: This is a chat in Spanish between a user and an artificial intelligence assistant that generate true/false sentences about activities of daily life. Your propositions must be like this: "Lavarse las manos con agua sola elimina los gérmenes. ¿verdadero falso?" and you must wait for the answer, then you have to explain why.

        {context}

        User: {Question}

        Assistant: 
        """

        prompt = PromptTemplate.from_template(template)

        # create the chain
        output_parser = StrOutputParser()

        setup_and_retrieval = RunnableParallel(
            {"context": retriever | self.format_docs, "Question": RunnablePassthrough()}
        )

        self.chain = setup_and_retrieval | prompt | self.llm | output_parser

    ######################
    # From the RoboCompLLM you can call this methods:
    # self.llm_proxy.generateResponse(...)

    ############################
    # GENERATE RESPONSE
    ############################

    def LLM_generateResponse(self, user_response):
        # Interacting with model
        """
        Takes a user response and generates a corresponding assistant response
        using a language model chain, adding the responses to a chroma database
        for future use.

        Args:
            user_response (str): human response to the given prompt or query, which
                is used as input to the LLM model to generate the corresponding
                assistant response.

        Returns:
            undefined: a natural language response generated based on user input.

        """
        llm_response = self.chain.invoke(user_response)
        print("Assistant's response:")

        # updating chroma database
        self.db.add_texts(["User: " + user_response, "Assistant: " + llm_response])

        return llm_response

    # Actualiza llama_out con la respuesta generada
    def actualizar_out(self,respuesta_gen):
        """
        Updates an LLM node's "out_llama" attribute with the response generated
        by a `respuesta_gen` function and then updates the node in the graph.

        Args:
            respuesta_gen (Attribute object.): attribute value that will be assigned
                to the `out_llama` attribute of the LLM node in the graph.
                
                	* `respuesta_gen`: A `pydantic.BaseModel` object containing
                information about an LLM node.
                	* `self.agent_id`: The ID of the agent that is being updated.
                
                	Therefore, `actualizar_out` modifies the attribute `out_llama`
                of the LLM node with the deserialized input `respuesta_gen`, and
                updates the node in the graph using the `update_node()` method.

        Returns:
            undefined: a string indicating that an attribute has been modified and
            the LLM node has been updated in the graph.
            
            	* `print("Atributo modificado")`: This line prints a message indicating
            that an attribute has been modified.
            	* `llm_node.attrs["out_llama"] = Attribute(respuesta_gen, self.agent_id)`:
            This line sets the value of the `out_llama` attribute of the `LLM`
            node to an instance of the `Attribute` class, along with the ID of the
            agent that made the modification.

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
        Updates the attribute `in_llama` of a LLM node with the value of an agent's
        ID and prints a message indicating that the attribute has been modified.

        Returns:
            undefined: a formal and neutral passage of no more than 100 words,
            without repeating the question or using first-person statements.

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
        Modifies an attribute in an LLM node based on a provided value and agent
        ID, updates the node in the graph, and prints "Atributo modificado".

        Args:
            nuevo (`Attribute`.): new attribute value that will be assigned to the
                "in_llama" attribute of the LLM node in the graph.
                
                	* `self.agent_id`: This is an attribute that contains the unique
                identifier of the agent that is performing the action.
                	* ` Attribute(nuevo, self.agent_id)`: This is a constructor
                function that creates a new instance of the `Attribute` class,
                taking `nuevo` as input and `self.agent_id` as an additional
                argument. The `Attribute` class represents a custom attribute that
                can be attached to a node in the graph.
                	* `llm_node`: This is a reference to the node representing the
                LLM in the graph.
                	* `self.g`: This is a reference to the Graph object, which contains
                the graph structure and various functions for manipulating it.

        Returns:
            undefined: "Atributo modificado".
            
            	* `print("Atributo modificado")`: This line prints a message to the
            console indicating that an attribute has been modified.
            	* `self.g.update_node(llm_node)`: This line updates the node in the
            graph with the modified attribute. The exact effect of this line depends
            on the specific implementation of the `self.g` object, but it is
            typically used to update the node's attributes or links based on user
            input or other events.

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
        Updates the attributes of a node based on its current state and previous
        values, storing the response generated by the LLM in a variable for later
        use.

        Args:
            id (int): ID of the node that needs to be updated, which is passed to
                the function as an argument for reference and updating purposes.
            attribute_names ([str]): attribute names of the nodes being updated,
                which are displayed in green text in the console for logging purposes.

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
                #respuesta = self.LLM_generateResponse(self.last_in)
                #self.actualizar_out(respuesta)
                #self.borrar_in()
            else:
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

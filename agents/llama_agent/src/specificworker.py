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
    """
    Initializes a DSRGraph object and sets up connections for signal handling,
    then runs a timer-based computation task. It also defines methods for updating
    node attributes, generating responses, and managing edges in the graph.

    Attributes:
        Period (int): 2000 milliseconds by default. It represents a time interval
            for triggering periodic computations by the `compute` method.
        agent_id (int): 11 by default. It seems to be used as a unique identifier
            for the worker agent, possibly in the context of a graph or network.
        g (DSRGraph): Initialized with the values 0, "pythonAgent", and self.agent_id.
            It is used to interact with nodes and edges in a graph structure.
        last_in (Attribute[str,int]): Initially loaded from the "in_llama" value
            of a node named "LLM". It stores the last received input text for processing.
        last_out (str|None): Initialized with the value obtained from the "out_llama"
            node attribute of the DSRGraph. It represents the last output generated
            by the LLM (Large Language Model).
        last_texto (str): Associated with a node named "ASR". It stores the last
            text received from the ASR (Automatic Speech Recognition) system.
        update_node_att (None): Called when a node's attributes are updated. It
            checks if the node "Therapist" is in automatic mode, updates the "ASR"
            node and the "LLM" node accordingly.
        startup_check (bool): Set to True when initializing the worker, which
            triggers a startup check that will quit the application after a short
            delay (200 milliseconds).
        timer (QTimer): Used to schedule a function call (in this case, the `compute`
            method) at a specific interval (`self.Period`).
        compute (QtCoreSlot|bool): Responsible for computing something when called,
            presumably based on the timer's periodic timeout event. It does not
            have any visible effect on the code but returns True.
        init_llm (NoneNone): Used to initialize the Large Language Model (LLM)
            component by loading a pre-trained model, setting parameters for text
            processing, and defining the embedding function.

    """
    def __init__(self, proxy_map, startup_check=False):
        """
        Initializes an instance by setting attributes, loading initial values from
        a graph, connecting signals, and starting a timer or performing startup
        checks depending on a flag.

        Args:
            proxy_map (object): Passed to the superclass (`SpecificWorker`) when
                initializing an instance of this class. The purpose of `proxy_map`
                is not explicitly stated in the code, but it appears to be related
                to graph nodes or attributes.
            startup_check (bool): False by default. It determines whether to perform
                startup checks or start computing immediately. If set to True, it
                triggers the `startup_check` method; otherwise, it starts the timer
                and begins computing.

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
        """
        Sets parameters and returns a boolean value indicating success (True). The
        commented-out exception handling code suggests that this function may have
        been designed to handle potential errors, but currently does nothing with
        them.

        Args:
            params (object): Expected to hold parameters that are meant to be set
                or updated within the context of the current class instance.

        Returns:
            bool: `True`. This indicates that the function has executed successfully
            without any errors and exceptions.

        """
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

        """
        Computes and returns `True`. The method does not contain any computation
        logic, only comments indicating where a computation should be performed
        and error handling for Ice.Exception.

        Returns:
            bool: True.

        """
        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    def format_docs(self, docs):
        """
        Concatenates page contents from a list of documents (`docs`) into a single
        string, using dashes and line breaks to format each document content as a
        separate item.

        Args:
            docs (List[str]): Expected to contain one or more documents, where
                each document is represented as a string containing page content.

        Returns:
            str: A formatted string consisting of a list of documents, where each
            document is represented as a bullet point followed by its page content,
            with each entry separated by a newline character.

        """
        text = ""
        for d in docs:
            text += f"- {d.page_content}\n"

        return text

    def init_llm(self):
        # Download model from Huggingface
        """
        Initializes a large language model (LLM) and a text database. It downloads
        an LLM, configures it for use with a specific dataset, and creates a
        retriever to index the data. The method also defines a template for user
        prompts and sets up a pipeline for processing input and output.

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
        Generates an assistant's response to a user's input by invoking the chain
        and adds the conversation history to a database before returning the response.

        Args:
            user_response (str | None): Expected to be the user's input or message
                that triggers the response from the language model (LLM).

        Returns:
            str: The response generated by the Language Model (LLM) for a given
            user input. The returned value is then printed to the console and also
            stored in a database along with the corresponding user input.

        """
        llm_response = self.chain.invoke(user_response)
        print("Assistant's response:")

        # updating chroma database
        self.db.add_texts(["User: " + user_response, "Assistant: " + llm_response])

        return llm_response

    # Actualiza llama_out con la respuesta generada
    def actualizar_out(self,respuesta_gen):
        """
        Updates an LLM node's attribute "out_llama" with a new Attribute object,
        passing a response and agent ID as parameters. If the LLM node is not
        found, it prints an error message and returns False.

        Args:
            respuesta_gen (object): Expected to contain data that represents the
                generated response. The exact structure and nature of this object
                are not specified.

        Returns:
            bool: False if the node "LLM" is not found, and None otherwise.

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
        Modifies an attribute called "in_llama" of a node named "LLM" in a graph.
        If the node does not exist, it prints a message and returns False. Otherwise,
        it updates the node with the modified attribute.

        Returns:
            bool: False if no LLM node exists or the modification to the attribute
            fails, and an unspecified value (not necessarily True) otherwise.

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
        Updates an attribute "in_llama" of a node named "LLM" in a graph. If the
        node does not exist, it prints an error message and returns False. Otherwise,
        it sets the attribute to a new value and updates the node in the graph.

        Args:
            nuevo (str | int): Expected to be new value for the attribute "in_llama"
                of the node "LLM".

        Returns:
            bool: False if a node "LLM" cannot be found, and True otherwise after
            modifying an attribute on that node and updating it in the graph.

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
        Updates node attributes and performs specific actions based on their values.
        It checks for changes in ASR and LLM nodes' attributes, updating last text
        and input values, and potentially triggering response generation and output
        updates if necessary.

        Args:
            id (int): Not used within the scope of this code snippet. Its presence
                seems unnecessary, implying that it might be intended for future
                use or debugging purposes.
            attribute_names ([str]): Not used within the function body, indicating
                that it is either unused or intended for future implementation.
                Its purpose remains unclear from this code snippet.

        """
        ther_node = self.g.get_node("Therapist")
        if ther_node.attrs["automatic_mode"].value == True:
            asr_node = self.g.get_node("ASR")
            if asr_node.attrs["texto"].value != self.last_texto and asr_node.attrs["texto"].value != "":
                self.last_texto = asr_node.attrs["texto"].value
                self.actualizar_in(self.last_texto)
            else:
                pass
        else:
            pass

        llm_node = self.g.get_node("LLM")
        if llm_node.attrs["in_llama"].value != self.last_in and llm_node.attrs["in_llama"].value != "":
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

        """
        Updates an edge between two nodes with a specified type, printing a message
        to the console indicating the operation. The nodes are identified by
        integers fr and to, and the type is represented as a string.

        Args:
            fr (int): Assigned an integer value representing the from node or edge
                identifier. It is used to identify the starting point of the edge
                being updated.
            to (int): Referred to as the edge's target node or destination. It
                represents the node that the edge connects to the source node
                represented by the `fr` parameter.
            type (str): Used to specify the type of edge being updated, likely
                representing information about the relationship between nodes fr
                and to.

        """
        console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')

    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')

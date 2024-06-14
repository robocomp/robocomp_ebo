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

from huggingface_hub import hf_hub_download
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 10
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
        print('SpecificWorker.compute...')

        # testing LLM
        print(self.LLM_generateResponse(input("Talk to me:\n")))

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    # =============== Methods for Component Implements ==================
    # ===================================================================


    def format_docs(self, docs):
        text = ""
        for d in docs:
            text += f"- {d.page_content}\n"

        return text
    
    def init_llm(self):
        # Download model from Huggingface
        model_path = hf_hub_download(
            repo_id="TheBloke/Mistral-7B-OpenOrca-GGUF",
            filename="mistral-7b-openorca.Q8_0.gguf",
            force_download=False
        )

        # Load the model
        self.llm = LlamaCpp(
            model_path=model_path,
            stop=["<|im_end|>"],
            n_gpu_layers=-1,
            n_ctx=2048*4,
            max_tokens=2048,
            temperature=0.3, 
            streaming=True, 
            top_p=0.8
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
        template = """<|im_start|>system: you speak fluent Spanish and you are able to generate good true/false questions about the topic the user mentions. 
        {system_message}<|im_end|>
        <|im_start|>user
        {prompt}<|im_end|>
        <|im_start|>assistant
        """

        prompt = PromptTemplate.from_template(template)

        # create the chain
        output_parser = StrOutputParser()

        setup_and_retrieval = RunnableParallel(
            {"system_message": retriever | self.format_docs, "prompt": RunnablePassthrough()}
        )

        self.chain = setup_and_retrieval | prompt | self.llm | output_parser

    ############################
    # GENERATE RESPONSE
    ############################

    def LLM_generateResponse(self, user_response):
        # Interacting with model
        llm_response = self.chain.invoke(user_response)
        print("Assistant's response:")

        # updating chroma database
        self.db.add_texts([" - User: " + user_response + " - Assistant: " + llm_response])

        return llm_response
    # ===================================================================
    # ===================================================================


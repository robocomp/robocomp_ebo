#!/usr/bin/python3

from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# download the model from HF
model_path = hf_hub_download(
    repo_id="lmstudio-community/Llama3-ChatQA-1.5-8B-GGUF",
    filename="ChatQA-1.5-8B-Q4_K_M.gguf",
    force_download=False
)

# load the model
llm = Llama(
    model_path=model_path,
    stop=["<|begin_of_text|>"],
    n_gpu_layers=-1,
    n_ctx=2048,
    max_tokens=2048,
    temperature=0.0,
    streaming=True
)

# create the embeddings
model_name = "mixedbread-ai/mxbai-embed-large-v1"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}

embeddings_model = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# create the vector db and the retriever
db = Chroma(embedding_function=embeddings_model)

retriever = db.as_retriever()

db.add_texts(["harrison has one apple and two orange",
              "bears has two apples and one banana"])

# create the prompt
template = (
    "System: You are an AI assistant that speaks Spanish fluently with the following context:"
    "\n\n{context}"
    "\n\nUser: {question}"
    "\n\nAssistant:"
    )

prompt = PromptTemplate.from_template(template)

print(prompt)

# create the chain
output_parser = StrOutputParser()


def format_docs(docs):

    text = ""

    for d in docs:
        text += f"- {d.page_content}\n"

    return text


setup_and_retrieval = RunnableParallel(
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
)

chain = setup_and_retrieval | prompt | llm | output_parser

# prompt the LLM
print(chain.invoke("what do harrison and bears have?"))

# prompt the LLM
print(chain.invoke("what does color this fruits?"))
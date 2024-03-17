from pyppeteer import launch
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import re
import json
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.messages import AIMessage, HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

os.environ["AZURE_OPENAI_API_KEY"] = "0d2153d2cafb42ad973cb929b605b7cf"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://egs-marigold-backend-model.openai.azure.com/"

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="embedding",
    openai_api_version="2023-05-15",
)


vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embeddings, collection_name = "ESG")

llm = AzureChatOpenAI(
    openai_api_version="2023-05-15",
    azure_deployment="llm",
)

template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. These question are related to an organisation named as WellsFargo.  
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template,)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

retriever = vectordb.as_retriever(k=5)
qa = ConversationalRetrievalChain.from_llm(
    llm,
    retriever=retriever,
    memory=memory,
)

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)
contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

def contextualized_question(input: dict):
    if input.get("chat_history"):
        return contextualize_q_chain
    else:
        return input["question"]


rag_chain = (
    RunnablePassthrough.assign(
        context=contextualized_question | retriever
    )
    | QA_CHAIN_PROMPT
    | llm
)


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def getAnswer(data):

    message = data["current_question"]
    chat_history = []
    for hist in data["history"]:
        chat_history.extend([hist[0],hist[1]])
    ai_msg = rag_chain.invoke({"question": message, "chat_history": chat_history})
    paragraph = ai_msg.content
    data = []
    citations = []
    additional_info = []
    docs = vectordb.similarity_search(message,k=3)
    for d in docs:
        citations.append([d.metadata["source"] + " pg." + str(d.metadata["page"]),""])
        print(d)
        print(d.page_content)
        additional_info.append(d.page_content)

    response = {}

    response["paragraph"] = paragraph
    response["data"] = data
    response["citations"] = citations
    response["additional_info"] = additional_info
    response["question"] = message
    response["labels"] = []
    response["label"] = []
    response["reportYear"] = 2021
    response["chartType"] = ""
    
    return response

def addNewPdf(filePath):

    loaders = []
    loaders.append(PyPDFLoader(filePath))
    print(filePath)

    print("PDF Read")
    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 150
    )

    print("Chunks Created")
    new_docs = text_splitter.split_documents(docs)
    print(len(new_docs))

    vectordb.add_documents(
        new_docs
    )

    vectordb.persist()

    print(vectordb._collection.count())
    return True

def getQuestion(filePath):
    
    print(filePath)
    loader = PyPDFLoader(filePath)
    pages = loader.load()
    questionnare = ""
    for page in pages:
        questionnare += page.page_content

    pattern = r'\((C-*\w*\d+\.\d+\w*)\)\s*(.*?)\s*Response options\s*(.*?)(?=\(C-*\w*\d+\.\d+\w*\)|$)'

    matches = re.findall(pattern, questionnare, re.DOTALL)

    questions = []
    # Print extracted questions and response options
    for match in matches:
        question_number = match[0].strip()
        question = question_number + " " + match[1].strip()
        response_options = match[2].strip()    
        questions.append(question_number + " " + question + " " + response_options)
    
    return questions

def addQuestionPDF(path):

    questions = getQuestion(path)
    responses = []
    chatHistory = []
    for question in questions:
        ai_msg = rag_chain.invoke({"question": question, "chat_history": chatHistory})
        paragraph = ai_msg.content
        data = []
        citations = []
        additional_info = []
        docs = vectordb.similarity_search(question,k=3)
        for d in docs:
            citations.append([d.metadata["source"] + " pg." + str(d.metadata["page"]),""])
            additional_info.append(d.page_content)

        response = {}

        response["paragraph"] = paragraph
        response["data"] = data
        response["citations"] = citations
        response["additional_info"] = additional_info
        response["question"] = question
        response["labels"] = []
        response["label"] = []
        response["reportYear"] = 2021
        response["chartType"] = ""

        responses.append(response)
        chatHistory.extend([HumanMessage(content=question), ai_msg])
    
    return responses

async def html_to_pdf(html_content, output_path):
    browser = await launch()
    page = await browser.newPage()

    # Set content and wait for network idle
    await page.setContent(html_content, waitUntil='networkidle0')

    # Generate PDF
    await page.pdf({'path': output_path, 'format': 'A4'})

    # Close browser
    await browser.close()
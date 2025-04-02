# importing all the necassary libraries
import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain import hub
from pydantic import SecretStr


# loading environment file
load_dotenv(override=True)


huggingface_api_key = SecretStr(os.getenv("HUGGINGFACE_API_KEY"))

# intializing embedding model
embeddor = HuggingFaceInferenceAPIEmbeddings(
    api_key=huggingface_api_key, model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# creating vector database
vector_db = Chroma(persist_directory="Streamlit_db", embedding_function=embeddor)

# intializing openai model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def streamlit_helper(message, chat_history):
    """This function is useful when you want to retrieve data about streamlit"""

    qa_template = """You are an streamlit documentation assistant.
    Use the following context to answer the question as accurately as possible:

    Chat History:
    {chat_history}

    Retrieved Context:
    {context}

    Guidelines:
    - Wish user if he wishes you also if they ask about you say so
    - Answer based on the retrieved context and chat history
    - If the answer isn't in the context, say "I don't know"
    - Keep your response concise (3 sentences maximum)
    - Provide context-aware and relevant answers

    Question: {input}
    """

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_template),
        ("human", "{input}")
    ])

    history_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

    # Create a history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm,
        vector_db.as_retriever(),
        prompt=history_prompt,  # Separate prompt for contextualizing the query
    )

    # Combine documents chain
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Full retrieval chain
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    result = rag_chain.invoke({"input": message, "chat_history": chat_history})

    return result["answer"]


if __name__ == "__main__":
    print(streamlit_helper('who is mahatma gandhi', chat_history=[]))

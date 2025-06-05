import os
from pathlib import Path

import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Use client functions from the existing MCP client
from client.client import discover_tools, call_tool, DEFAULT_SERVER

DATA_DIR = Path(__file__).parent / "data"
DB_DIR = Path(__file__).parent / "db"
DB_DIR.mkdir(exist_ok=True)


@st.cache_resource(show_spinner=False)
def load_vectorstore():
    texts = []
    for file in DATA_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            texts.append(f.read())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.create_documents(texts)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=str(DB_DIR))
    return vectordb


def maybe_call_mcp(query: str):
    """If query contains a known MCP command, call the MCP server via the client."""
    parts = query.split()
    if not parts:
        return None

    command = parts[0]
    username = parts[1] if len(parts) > 1 else None
    try:
        tools = discover_tools(DEFAULT_SERVER)["tools"]
    except Exception:
        return None
    if command in tools and username:
        try:
            result = call_tool(DEFAULT_SERVER, tools[command]["endpoint"], {"username": username})
            return str(result)
        except Exception:
            return None
    return None


def validate(query: str, response: str) -> bool:
    """Simple validation: fail if the LLM says it does not know."""
    if not response:
        return False
    bad_phrases = ["I don't know", "I'm not sure"]
    for phrase in bad_phrases:
        if phrase.lower() in response.lower():
            return False
    return True


def main():
    st.title("LangChain RAG App")
    vectordb = load_vectorstore()
    retriever = vectordb.as_retriever()

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(temperature=0.1),
        retriever=retriever,
        memory=memory,
    )

    user_query = st.text_input("Ask a question or run a command:")
    if st.button("Submit") and user_query:
        external_info = maybe_call_mcp(user_query)
        if external_info:
            st.write("Retrieved from MCP:", external_info)
            user_query = f"{user_query}\nAdditional context:\n{external_info}"

        result = None
        for _ in range(10):
            result = chain({"question": user_query})["answer"]
            if validate(user_query, result):
                break
        st.write(result)


if __name__ == "__main__":
    main()

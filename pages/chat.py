import streamlit as st
import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Import from main app
from app import API_BASE_URL, init_session

class ChatHistory(BaseModel):
    id: int = Field(default_factory=int)
    question: str = Field(default_factory=str)
    answer: Optional[str] = None

class KnowledgeStore(BaseModel):
    id: int
    name: str
    type: str
    documentIds: List[int]

class QueryRequest(BaseModel):
    id: int
    question: str
    knowledgeStoreList: List[KnowledgeStore]
    historyList: List[ChatHistory] = Field(default_factory=list)

def initialize_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "knowledge_stores" not in st.session_state:
        st.session_state.knowledge_stores = []

def add_to_chat_history(question: str, answer: str):
    chat_entry = ChatHistory(
        id=len(st.session_state.chat_history),
        question=question,
        answer=answer
    )
    st.session_state.chat_history.append(chat_entry)

def send_chat_request(question: str) -> Optional[str]:
    try:
        # Create knowledge store from user's documents
        knowledge_store = KnowledgeStore(
            id=st.session_state.user_id,
            name=f"User_{st.session_state.user_id}_Store",
            type="document",
            documentIds=[st.session_state.user_id]  # Using user_id as document ID for simplicity
        )
        
        query_request = QueryRequest(
            id=st.session_state.user_id,
            question=question,
            knowledgeStoreList=[knowledge_store],
            historyList=st.session_state.chat_history
        )
        
        response = requests.post(
            f"{API_BASE_URL}/document/doc_chat",
            json=query_request.dict()
        )
        
        if response.status_code == 200:
            return response.json().get("answer", "No answer received")
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error sending chat request: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Document Chat",
        page_icon="💬",
        layout="wide"
    )
    
    init_session()
    initialize_chat_history()
    
    if not st.session_state.is_authenticated:
        st.warning("Please login to access this page")
        st.stop()
    
    st.title("Document Chat")
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat.question)
            with st.chat_message("assistant"):
                st.write(chat.answer)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_chat_request(prompt)
                if response:
                    st.write(response)
                    add_to_chat_history(prompt, response)
                else:
                    st.error("Failed to get response from the server")

if __name__ == "__main__":
    main() 
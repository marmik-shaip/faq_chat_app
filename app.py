import streamlit as st
import requests
from pathlib import Path
import json
import os
from datetime import datetime
import hashlib

# Constants
API_BASE_URL = "http://localhost:8000"  # Update this with your FastAPI server URL
SESSION_FILE = "session.json"

def init_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

def login(username: str, password: str) -> bool:
    # In a real application, you would validate against a database
    # For demo purposes, we'll use a simple check
    if username and password:
        # Generate a simple user ID based on username
        user_id = int(hashlib.md5(username.encode()).hexdigest()[:8], 16)
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.is_authenticated = True
        return True
    return False

def logout():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_authenticated = False

def main():
    st.set_page_config(
        page_title="Document Q&A System",
        page_icon="📚",
        layout="wide"
    )
    
    init_session()
    
    # Sidebar for navigation and authentication
    with st.sidebar:
        st.title("Document Q&A System")
        
        if not st.session_state.is_authenticated:
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            st.write(f"Welcome, {st.session_state.username}!")
            if st.button("Logout"):
                logout()
                st.rerun()
            
            st.divider()
            st.subheader("Navigation")
            page = st.radio("Go to", ["Document Upload", "Chat"])
            
            if page == "Document Upload":
                st.switch_page("pages/upload.py")
            else:
                st.switch_page("pages/chat.py")

if __name__ == "__main__":
    main() 
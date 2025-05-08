import streamlit as st
import requests
from typing import List, Dict, Optional, Any
import json
import os
import time

# App configuration
st.set_page_config(
    page_title="Document QA System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your FastAPI server URL

# Session state initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "knowledge_stores" not in st.session_state:
    st.session_state.knowledge_stores = []
if "selected_knowledge_store" not in st.session_state:
    st.session_state.selected_knowledge_store = None
if "documents" not in st.session_state:
    st.session_state.documents = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# CSS for better styling and responsiveness
st.markdown("""
<style>
    /* General styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        font-size: 2.8rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #0D47A1;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .chat-container {
        border-radius: 10px;
        background-color: #f9f9f9;
        padding: 20px;
        margin-bottom: 15px;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.1);
    }
    .user-message {
        background-color: #E3F2FD;
        padding: 12px 18px;
        border-radius: 20px;
        margin: 8px 0;
        text-align: right;
        max-width: 75%;
        margin-left: auto;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(30, 136, 229, 0.2);
        word-wrap: break-word;
    }
    .bot-message {
        background-color: #FFFFFF;
        padding: 12px 18px;
        border-radius: 20px;
        margin: 8px 0;
        text-align: left;
        max-width: 75%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        font-size: 1rem;
        word-wrap: break-word;
    }
    .file-upload-container {
        border: 2px dashed #1E88E5;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        margin-top: 15px;
        background-color: #f0f7ff;
        transition: background-color 0.3s ease;
    }
    .file-upload-container:hover {
        background-color: #d9eaff;
    }
    .login-container {
        max-width: 420px;
        margin: 2rem auto;
        padding: 30px;
        border-radius: 12px;
        background-color: #f9f9f9;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1565c0 !important;
    }
    .document-card {
        background-color: #f0f0f0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        transition: box-shadow 0.3s ease;
    }
    .document-card:hover {
        box-shadow: 0 6px 14px rgba(0,0,0,0.1);
    }
    .source-document {
        background-color: #EFF7FF;
        border-left: 4px solid #1E88E5;
        padding: 12px;
        margin: 6px 0;
        font-size: 0.95rem;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(30, 136, 229, 0.1);
        word-wrap: break-word;
    }
    .sidebar .sidebar-content {
        padding: 1rem 1rem 1rem 1rem;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .sub-header {
            font-size: 1.2rem;
        }
        .user-message, .bot-message {
            max-width: 90%;
            font-size: 0.9rem;
        }
        .document-card {
            padding: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)


# API functions with session handling
def api_request(method, endpoint, data=None, files=None, params=None):
    """Make an API request with authentication handling"""
    if not st.session_state.user_id:
        st.session_state.current_page = "login"
        st.error("Please login to access this page")
        st.rerun()
        return None

    headers = {
        "Content-Type": "application/json"
    }

    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            if files:
                # Remove Content-Type for multipart/form-data
                headers.pop("Content-Type", None)
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            st.error(f"Unsupported method: {method}")
            return None

        if response.status_code == 401:
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.current_page = "login"
            st.error("Session expired. Please log in again.")
            st.rerun()
            return None

        return response
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the server. Please check if the server is running.")
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def login(username, password):
    """Handle user login"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            response_data = response.json()
            # Store user info in session state
            st.session_state.user_id = response_data.get("user_id")
            st.session_state.username = response_data.get("username")
            st.session_state.current_page = "document_upload"  # Set initial page after login
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False


def logout():
    """Handle user logout"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/logout")
        if response.status_code == 200:
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.current_page = "login"
            # Clear other session data
            st.session_state.chat_history = []
            st.session_state.knowledge_stores = []
            st.session_state.selected_knowledge_store = None
            st.session_state.documents = []
            st.session_state.chat_input = ""
    except Exception as e:
        st.error(f"Logout error: {str(e)}")


def get_knowledge_stores():
    """Fetch knowledge stores from API"""
    response = api_request("GET", "/document/knowledge_stores")
    if response and response.status_code == 200:
        return response.json()
    return []


def get_documents():
    """Fetch documents from API"""
    response = api_request("GET", "/document/list")
    if response and response.status_code == 200:
        return response.json()
    return []


def upload_document(file, index_id=None, name=None, doc_type=None, operation=None):
    """Upload document (including audio) to API"""
    try:
        # Document input metadata
        document_input = {
            "id": index_id,
            "name": name,
            "operation": operation or "upload",
            "type": doc_type,
            "data": []
        }

        # Send document_input as a form field (not raw JSON header)
        data = {
            "document_input": json.dumps(document_input)
        }

        files = {"files": (file.name, file, file.type)}

        response = api_request(
            "POST",
            "/document/qa",
            data=data,
            files=files
        )

        if response and response.status_code == 200:
            return True, "Document uploaded successfully!"
        else:
            error_msg = "Upload failed"
            if response:
                error_msg = f"{error_msg}: {response.text}"
            return False, error_msg

    except Exception as e:
        return False, f"Error uploading document: {str(e)}"


def send_chat_message(question, knowledge_store_id):
    """Send chat message to API"""
    try:
        # Prepare knowledge store
        knowledge_store = next((ks for ks in st.session_state.knowledge_stores if ks["id"] == knowledge_store_id), None)
        if not knowledge_store:
            return False, "Knowledge store not found", None

        knowledge_store_obj = {
            "id": knowledge_store["id"],
            "name": knowledge_store["name"],
            "type": knowledge_store["type"],
            "documentIds": knowledge_store.get("documentIds", [])
        }

        # Prepare history
        history_list = []
        for entry in st.session_state.chat_history:
            history_list.append({
                "id": entry.get("id", len(history_list)),
                "question": entry.get("question", ""),
                "answer": entry.get("answer", "")
            })

        # Prepare request as per required format
        query_request = {
            "id": int(time.time()),
            "question": question,
            "knowledgeStoreList": [knowledge_store_obj],
            "historyList": history_list
        }

        # Make API call
        response = api_request("POST", "/document/doc_chat", data=query_request)

        if response and response.status_code == 200:
            response_data = response.json()
            # Add to history
            new_entry = {
                "id": len(st.session_state.chat_history),
                "question": question,
                "answer": response_data.get("answer", "No answer provided"),
                "sources": response_data.get("sourceDocuments", [])
            }
            st.session_state.chat_history.append(new_entry)
            return True, "Message sent successfully", response_data
        else:
            error_msg = "Failed to send message"
            if response:
                error_msg = f"{error_msg}: {response.text}"
            return False, error_msg, None

    except Exception as e:
        return False, f"Error sending message: {str(e)}", None


def delete_document(doc_id):
    """Delete document from API"""
    response = api_request("DELETE", f"/document/{doc_id}")
    if response and response.status_code == 200:
        return True, "Document deleted successfully"
    return False, "Failed to delete document"


# UI Components
def render_login_page():
    """Render login page"""
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-header'>📚 Document QA System</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Login</h2>", unsafe_allow_html=True)

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", use_container_width=True):
        if username and password:
            with st.spinner("Logging in..."):
                if login(username, password):
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:
            st.warning("Please enter your username and password")
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown("# Document QA System")
        st.markdown("---")

        # Navigation using radio to preserve session state better
        page = st.radio(
            "Navigation",
            options=["Document Upload", "Chat"],
            index=0 if st.session_state.current_page == "document_upload" else 1,
            key="sidebar_nav"
        )

        if page == "Document Upload":
            st.session_state.current_page = "document_upload"
        elif page == "Chat":
            st.session_state.current_page = "chat"
            # Refresh knowledge stores when navigating to chat
            st.session_state.knowledge_stores = get_knowledge_stores()
            if st.session_state.knowledge_stores and not st.session_state.selected_knowledge_store:
                st.session_state.selected_knowledge_store = st.session_state.knowledge_stores[0]

        st.markdown("---")

        # Knowledge Store Selection (for chat page)
        if st.session_state.current_page == "chat":
            st.markdown("### Knowledge Store")

            if st.session_state.knowledge_stores:
                selected_ks_names = [ks["name"] for ks in st.session_state.knowledge_stores]
                selected_ks_name = st.selectbox(
                    "Select Knowledge Store",
                    options=selected_ks_names,
                    index=0
                )

                st.session_state.selected_knowledge_store = next(
                    (ks for ks in st.session_state.knowledge_stores if ks["name"] == selected_ks_name),
                    st.session_state.knowledge_stores[0]
                )

                # Refresh button
                if st.button("🔄 Refresh Stores", use_container_width=True):
                    st.session_state.knowledge_stores = get_knowledge_stores()
                    st.rerun()
            else:
                st.info("No knowledge stores available")
                if st.button("🔄 Refresh", use_container_width=True):
                    st.session_state.knowledge_stores = get_knowledge_stores()
                    st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()


def render_upload_page():
    """Render document upload page"""
    st.markdown("<h1 class='main-header'>Document Upload</h1>", unsafe_allow_html=True)

    # Upload section
    with st.container():
        st.markdown("<div class='file-upload-container'>", unsafe_allow_html=True)
        st.markdown("### Upload Documents")
        st.markdown("Upload documents to be processed by the QA system.")

        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "csv", "xlsx", 'pptx']
        )
        index_id = st.text_input("Project ID", placeholder="Enter a unique Project ID")
        name = st.text_input("Project Name", placeholder="Enter a unique Project Name")
        doc_type = st.selectbox('Document Type', ('file', 'url'))
        operation = st.selectbox('Operation', ('add', 'update', 'upload'))

        if uploaded_files:
            if st.button("Upload Selected Files"):
                progress_bar = st.progress(0)
                success_count = 0
                for i, file in enumerate(uploaded_files):
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    success, message = upload_document(file, index_id=index_id, name=name, doc_type=doc_type, operation=operation)
                    if success:
                        success_count += 1
                        st.success(f"Uploaded: {file.name}")
                    else:
                        st.error(f"Failed to upload {file.name}: {message}")

                if success_count > 0:
                    # Refresh document list
                    st.session_state.documents = get_documents()

                progress_bar.empty()

        st.markdown("</div>", unsafe_allow_html=True)

    # Document list
    with st.container():
        st.markdown("### Uploaded Documents")

        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.session_state.documents = get_documents()
                st.rerun()

        if not st.session_state.documents:
            st.session_state.documents = get_documents()

        if not st.session_state.documents:
            st.info("No documents uploaded yet.")
        else:
            for doc in st.session_state.documents:
                with st.container():
                    st.markdown(f"<div class='document-card'>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**{doc.get('name', 'Unnamed document')}**")

                    with col2:
                        st.markdown(f"Type: {doc.get('type', 'Unknown')}")

                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{doc.get('id')}"):
                            success, message = delete_document(doc.get('id'))
                            if success:
                                st.success(message)
                                # Remove from local list
                                st.session_state.documents = [d for d in st.session_state.documents if
                                                              d.get('id') != doc.get('id')]
                                st.rerun()
                            else:
                                st.error(message)

                    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_page():
    """Render chat page"""
    st.markdown("<h1 class='main-header'>Document Chat</h1>", unsafe_allow_html=True)

    if not st.session_state.knowledge_stores:
        st.session_state.knowledge_stores = get_knowledge_stores()

    if not st.session_state.selected_knowledge_store:
        if st.session_state.knowledge_stores:
            st.session_state.selected_knowledge_store = st.session_state.knowledge_stores[0]
        else:
            st.warning("No knowledge stores available. Please create one by uploading documents.")
            return

    # Display selected knowledge store
    st.markdown(f"**Selected Knowledge Store:** {st.session_state.selected_knowledge_store.get('name', 'Unknown')}")

    # Chat history
    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.markdown("*No chat history yet. Start a conversation by sending a message.*")
        else:
            for message in st.session_state.chat_history:
                # User message
                st.markdown(f"<div class='user-message'>{message.get('question', '')}</div>", unsafe_allow_html=True)

                # Bot message
                st.markdown(f"<div class='bot-message'>{message.get('answer', '')}</div>", unsafe_allow_html=True)

                # Source documents if available
                sources = message.get('sources', [])
                if sources:
                    st.markdown("<details><summary>Source Documents</summary>", unsafe_allow_html=True)
                    for source in sources:
                        st.markdown(f"""
                        <div class='source-document'>
                            <strong>{source.get('name', 'Unknown document')}</strong><br>
                            {source.get('excerpt', 'No excerpt available')}
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</details>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Message input
    user_input = st.text_input("Ask a question about your documents:", key="chat_input", value=st.session_state.chat_input)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("Send", use_container_width=True):
            if user_input:
                with st.spinner("Getting answer..."):
                    success, message, response_data = send_chat_message(
                        user_input,
                        st.session_state.selected_knowledge_store.get('id')
                    )

                    if success:
                        # Auto-clear input
                        st.session_state.chat_input = ""
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("Please enter a question.")

    with col3:
        if st.button("Clear History", use_container_width=True):
            if st.confirm("Are you sure you want to clear the chat history?"):
                st.session_state.chat_history = []
                st.rerun()


# Main app
def main():
    """Main app function"""
    # Ensure session state is initialized properly
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

    # Debug info to check session state (can be removed in production)
    # st.write(f"DEBUG: user_id = {st.session_state.user_id}")
    # st.write(f"DEBUG: current_page = {st.session_state.current_page}")

    # Check if user is logged in
    if st.session_state.user_id is None:
        st.session_state.current_page = "login"
        render_login_page()
        return

    # Render sidebar and appropriate page
    render_sidebar()

    # Render the appropriate page based on the current page state
    if st.session_state.current_page == "document_upload":
        render_upload_page()
    elif st.session_state.current_page == "chat":
        render_chat_page()


if __name__ == "__main__":
    main()

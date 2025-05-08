import streamlit as st
import requests
import os
from pathlib import Path
import tempfile
from typing import List, Optional
from pydantic import BaseModel

# Import from main app
from app import API_BASE_URL, init_session

class FileData(BaseModel):
    fileId: int
    fileName: Optional[str] = None
    filePath: str

class DocumentInput(BaseModel):
    id: int
    name: str
    operation: str
    type: str
    data: Optional[List[FileData]] = None

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary directory and return the path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def upload_document(file_path: str, file_name: str, user_id: int) -> bool:
    """Upload document to FastAPI endpoint"""
    try:
        file_data = FileData(
            fileId=user_id,
            fileName=file_name,
            filePath=file_path
        )
        
        document_input = DocumentInput(
            id=user_id,
            name=file_name,
            operation="upload",
            type="document",
            data=[file_data]
        )
        
        response = requests.post(
            f"{API_BASE_URL}/document/qa",
            json=document_input.model_dump()
        )
        
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="Document Upload",
        page_icon="📤",
        layout="wide"
    )
    
    init_session()
    
    if not st.session_state.is_authenticated:
        st.warning("Please login to access this page")
        st.stop()
    
    st.title("Document Upload")
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'doc', 'docx', 'xlsx', 'pptx', 'csv', 'json', 'png'],
    )
    
    if uploaded_files:
        st.write("Selected files:")
        for uploaded_file in uploaded_files:
            st.write(f"- {uploaded_file.name}")
        
        if st.button("Upload Documents"):
            progress_bar = st.progress(0)
            success_count = 0
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Save file temporarily
                file_path = save_uploaded_file(uploaded_file)
                
                # Upload to API
                if upload_document(file_path, uploaded_file.name, st.session_state.user_id):
                    success_count += 1
                
                # Clean up temporary file
                os.unlink(file_path)
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            if success_count == len(uploaded_files):
                st.success(f"Successfully uploaded {success_count} documents!")
            else:
                st.warning(f"Uploaded {success_count} out of {len(uploaded_files)} documents")

if __name__ == "__main__":
    main() 
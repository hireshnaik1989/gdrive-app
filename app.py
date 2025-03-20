import streamlit as st
import os
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

def authenticate():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

def create_folder(drive, parent_folder_id, folder_name):
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [{'id': parent_folder_id}]
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']

def upload_file(drive, file, folder_id, file_name):
    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(file)
    file_drive.Upload()
    return file_drive['alternateLink']

# Streamlit UI
st.title("Google Drive File Uploader")
drive = authenticate()
st.success("Authenticated Successfully!")

parent_folder_id = '1qVj7L-DISqjWNU8OqKTFkXJihgXlUpgz'

# Create folders based on current month and day
current_month = datetime.now().strftime('%Y-%m')
current_day = datetime.now().strftime('%d')

month_folder_id = create_folder(drive, parent_folder_id, current_month)
day_folder_id = create_folder(drive, month_folder_id, current_day)
st.write(f"Created folders: {current_month}/{current_day}")

# File uploader
uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True)

if uploaded_files:
    st.write("Uploading Files...")
    progress_bar = st.progress(0)
    links = []

    for i, file in enumerate(uploaded_files):
        temp_file_path = os.path.join('temp', file.name)
        with open(temp_file_path, 'wb') as f:
            f.write(file.read())
        
        file_name = f"DN{i+1}"
        link = upload_file(drive, temp_file_path, day_folder_id, file_name)
        links.append(link)
        os.remove(temp_file_path)
        
        progress_bar.progress((i + 1) / len(uploaded_files))

    st.success("Files Uploaded Successfully!")
    for i, link in enumerate(links):
        st.write(f"File {i+1}: [Download Link]({link})")

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import BACKUP_FOLDER_PATH, CREDS_PATH, SCOPES, DRIVE_FOLDER_NAME
from google.oauth2 import service_account
import notify2

def fetch_oauth_credentials():
    return service_account.Credentials.from_service_account_file(CREDS_PATH)

def folder_exists_on_drive(drive_service, folder_name):
    folder_id = get_folder_id(drive_service, folder_name)
    if folder_id is None:
        return False
    else:
        return True

def file_exists_on_drive(drive_service, file_name):
    file_id = get_file_id(drive_service, file_name)
    if file_id is None:
        return False
    else:
        return True

# Returns None if a folder with the name 'folder_name' is not found
def get_folder_id(drive_service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, fields='files(id)').execute()
    folders = response.get('files', [])
    if folders:
        return folders[0]['id']
    else:
        return None

def get_file_id(drive_service, file_name):
    query = f"name='{file_name}' and trashed=false"
    response = drive_service.files().list(q=query).execute()
    files = response.get('files', [])
    if files:
        return files[0]['id']
    else:
        return None 

def update_file_on_drive(drive_service, existing_file_id, media):
    drive_service.files().update(fileId=existing_file_id, media_body=media).execute()

def create_file_on_drive(drive_service, filename, folder_id, media):
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    drive_service.files().create(body=file_metadata, media_body=media).execute()

def create_folder_on_drive(drive_service, folder_name, parent_folder_id):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    drive_service.files().create(body=folder_metadata).execute()

def upload_file(drive_service, filename, drive_folder_id, path):
    media = MediaFileUpload(os.path.join(path, filename), resumable=True)
    if file_exists_on_drive(drive_service, filename):
        existing_file_id = get_file_id(drive_service, filename)
        update_file_on_drive(drive_service, existing_file_id, media)
    else:
        create_file_on_drive(drive_service, filename, drive_folder_id, media)

# Uploads files in subfolders through recursion
def upload_files_in_folder(drive_service, drive_folder_id, folder_path):
    for entry in os.listdir(folder_path):
        if os.path.isdir(os.path.join(folder_path, entry)):
            if not folder_exists_on_drive(drive_service, entry):
                create_folder_on_drive(drive_service, entry, drive_folder_id)
            subfolder_id = get_folder_id(drive_service, entry)
            upload_files_in_folder(drive_service, subfolder_id, os.path.join(folder_path, entry))
        else:
            upload_file(drive_service, entry, drive_folder_id, folder_path)

# Creates an os notification
def alert(message):
    notify2.init("Alert")
    notification = notify2.Notification("Alert", message)
    notification.show()

# Performs the backup of the local folder located at backup_folder_path to the 
# folder named drive_folder_name to Google Drive
def backup_to_folder_in_drive(drive_service, drive_folder_name, backup_folder_path):
    if not folder_exists_on_drive(drive_service, drive_folder_name):
        alert('Error: the destination folder does not exist on the drive')
    else:
        drive_folder_id = get_folder_id(drive_service, drive_folder_name)
        upload_files_in_folder(drive_service, drive_folder_id, backup_folder_path)

if __name__ == '__main__':
    creds = fetch_oauth_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    backup_to_folder_in_drive(drive_service, DRIVE_FOLDER_NAME, BACKUP_FOLDER_PATH)

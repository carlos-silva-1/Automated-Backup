import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import BACKUP_FOLDER_PATH, CREDS_PATH, SCOPES, DRIVE_FOLDER_NAME
from google.oauth2 import service_account
import logging

# Allows interaction with google Drive API
DRIVE_SERVICE = None

def folder_exists_on_drive(folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        return False
    else:
        return True

def file_exists_on_drive(file_name):
    file_id = get_file_id(file_name)
    if file_id is None:
        return False
    else:
        return True

# Returns None if a folder with the name 'folder_name' is not found
def get_folder_id(folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = DRIVE_SERVICE.files().list(q=query).execute()
    folders = response.get('files', [])
    if folders:
        return folders[0]['id']
    else:
        return None

def get_file_id(file_name):
    query = f"name='{file_name}' and trashed=false"
    response = DRIVE_SERVICE.files().list(q=query).execute()
    files = response.get('files', [])
    if files:
        return files[0]['id']
    else:
        return None 

def update_file_on_drive(existing_file_id, media):
    try:
        DRIVE_SERVICE.files().update(fileId=existing_file_id, media_body=media).execute()
    except HttpError as e:
        logging.error(f'An HTTP error occurred while trying to update the file {filename}: {e}')
        raise Exception() # Stops further execution
    except Exception as e:
        logging.error(f'An error occurred while trying to update the file {filename}: {e}')
        raise Exception() # Stops further execution

def create_file_on_drive(filename, parent_folder_id, media):
    file_metadata = {'name': filename, 'parents': [parent_folder_id]}
    try:
        DRIVE_SERVICE.files().create(body=file_metadata, media_body=media).execute()
    except HttpError as e:
        logging.error(f'An HTTP error occurred while trying to create the file {filename}: {e}')
        raise Exception() # Stops further execution
    except Exception as e:
        logging.error(f'An error occurred while trying to create the file {filename}: {e}')
        raise Exception() # Stops further execution

def create_folder_on_drive(folder_name, parent_folder_id):
    folder_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_folder_id]}
    try:
        DRIVE_SERVICE.files().create(body=folder_metadata).execute()
    except HttpError as e:
        logging.error(f'An HTTP error occurred while trying to create the folder {folder_name}: {e}')
        raise Exception() # Stops further execution
    except Exception as e:
        logging.error(f'An error occurred while trying to create the folder {folder_name}: {e}')
        raise Exception() # Stops further execution

def upload_file(filename, parent_folder_id, path):
    media = MediaFileUpload(os.path.join(path, filename), resumable=True)
    if file_exists_on_drive(filename):
        existing_file_id = get_file_id(filename)
        update_file_on_drive(existing_file_id, media)
    else:
        create_file_on_drive(filename, parent_folder_id, media)

# Uploads files in subfolders through recursion
def upload_files_in_folder(drive_folder_id, folder_path):
    for entry in os.listdir(folder_path):
        if os.path.isdir(os.path.join(folder_path, entry)):
            if not folder_exists_on_drive(entry):
                create_folder_on_drive(entry, drive_folder_id)
            subfolder_id = get_folder_id(entry)
            upload_files_in_folder(subfolder_id, os.path.join(folder_path, entry))
        else:
            upload_file(entry, drive_folder_id, folder_path)

# Performs the backup of the local folder located at backup_folder_path to the 
# folder named drive_folder_name to Google Drive
def backup_to_folder_in_drive(drive_folder_name, backup_folder_path):
    if not folder_exists_on_drive(drive_folder_name):
        logging.error(f'THE BACKUP WAS NOT PERFORMED! A folder named {drive_folder_name} must exist in the drive prior to the execution of this script.') 
    else:
        drive_folder_id = get_folder_id(drive_folder_name)
        upload_files_in_folder(drive_folder_id, backup_folder_path)

def fetch_oauth_credentials():
    creds = None
    try:
        creds = service_account.Credentials.from_service_account_file(CREDS_PATH)
    except FileNotFoundError as e:
        logging.exception(f'Credentials to authenticate the account with Google API were not found. The script expected to find them at {CREDS_PATH}')
        raise Exception() # Stops further execution
    return creds

def config_logger():
    logging.basicConfig(filename='backup.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    config_logger()
    creds = fetch_oauth_credentials()
    DRIVE_SERVICE = build('drive', 'v3', credentials=creds)
    backup_to_folder_in_drive(DRIVE_FOLDER_NAME, BACKUP_FOLDER_PATH)

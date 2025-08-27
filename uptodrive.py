from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

# Quyền truy cập
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Load credentials từ client.json
def get_credentials():
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)
    return creds

FOLDER_ID = "1odt7l2k_vUSQG766H0bRehMFWV9Jtsfc"
"""Upload trực tiếp file PNG lên Google Drive"""
creds = get_credentials()
service = build('drive', 'v3', credentials=creds)
def upload_to_drive(file_path):
    filename = os.path.basename(file_path)
    file_metadata = {
        'name': filename,
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype='image/png')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get("id")

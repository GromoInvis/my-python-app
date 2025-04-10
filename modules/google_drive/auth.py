import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_FILE = 'token.pickle'
CLIENT_SECRET_FILE = 'client_secret.json'

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                scopes=SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            print('Перейдіть за посиланням для авторизації:', auth_url)
            code = input('Введіть код авторизації: ')
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds
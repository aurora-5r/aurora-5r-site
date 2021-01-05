"""
Some init functions for Loging and gdrive access


"""
import json
import logging
import logging.config
import os
import pickle
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
#from oauth2client import client, file, tools
#from httplib2 import Http
from googleapiclient.discovery import build

#from apiclient import discovery

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def setup_logging(default_path='logging.json',
                  default_level=logging.DEBUG,
                  env_key='LOG_CFG'):
    """initialize logging

    Args:
        default_path (str, optional). Defaults to 'logging.json'.
        default_level ( optional):  Defaults to logging.DEBUG.
        env_key (str, optional): Defaults to 'LOG_CFG'.
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as config_file:
            config = json.load(config_file)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_credentials():
    """Initalize service to connect to gdrive

    Returns:
        service
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.secret.pickle"):
        with open("token.secret.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "gsuiteFromPython.cred.secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.secret.pickle", "wb") as token:
            pickle.dump(creds, token)
    service = build("drive", "v3", credentials=creds)
    return service


def get_config(default_path='config.json', ):
    """Get configuration

    """
    path = default_path
    search = os.getenv("SEARCH_GOOGLE", None)

    if os.path.exists(path):
        with open(path, 'rt') as config_file:
            config = json.load(config_file)
            if search == "YES":
                config["googleSearch"] = "YES"
            else:
                config["googleSearch"] = "NO"
            return config

    else:
        logging.error("Config File not found (%s)", path)
        sys.exit(2)

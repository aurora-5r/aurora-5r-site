#!/home/laurent/.platformio/penv/bin/python
# coding: utf8

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import Counter

import logging
import myLog

myLog.setup_logging()
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def print_result(foldersList):
    occurences=Counter(foldersList)
    for key,val in occurences.items():
        logger.info("%d files in %s", val, key)

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.secret.pickle'):
        with open('token.secret.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.secret.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    
    get_folder_tree("0By9FaGhQFbEVZnNqcXpkdVltQnc", service)

def listFilesForOwner(service):    
    page_token = None
    foldersList=[]

    while True:
        #response = service.files().list(q="'admin@soitec.com' in owners and  '0B-60sgr6nbBkd0pKOGdLUzhMeW8' in parents",
        # response = service.files().list(q="mimeType='application/vnd.google-apps.folder'  and trashed = false",
        #                                     spaces='drive',
        #                                     fields='nextPageToken, files(id, name)',
        #                                     pageToken=page_token).execute()
        
        response = service.files().list(q="'admin@soitec.com' in owners ",
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name, parents)',
                                            pageToken=page_token).execute()
        
        for file in response.get('files', []):
            
            #print ('Found file: %s (%s) in %s' % (file.get('name'), file.get('id'), file.get('parents')))
            p=file.get('parents')
            logger.debug(p)
            if not p :
                p=["None"]
            
            foldersList=foldersList+p
        logging.info("- - - - - - found %d files", len(foldersList))
        print_result(foldersList)    
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    print_result(foldersList)
    
    

def check_for_subfolders(folder_id, service, folder_tree):
    new_sub_patterns = {}
    folders = service.files().list(q="mimeType='application/vnd.google-apps.folder' and parents in '"+folder_id+"' and trashed = false",fields="nextPageToken, files(id, name)",pageSize=400).execute()
    all_folders = folders.get('files', [])
    #all_files = check_for_files(folder_id, service)
    all_files=[]
    n_files = len(all_files)
    n_folders = len(all_folders)
    old_folder_tree = folder_tree
    if n_folders != 0:
        for i,folder in enumerate(all_folders):
            folder_name =  folder['name']
            subfolder_pattern = old_folder_tree + '/'+ folder_name
            new_pattern = subfolder_pattern
            new_sub_patterns[subfolder_pattern] = folder['id']
            logger.debug('New Pattern: %s', new_pattern)
            #all_files = check_for_files(folder['id'], service)
            all_files=[]
            n_files =len(all_files)
            new_folder_tree = new_pattern 
            if n_files != 0:
                for file in all_files:
                    file_name = file['name']
                    new_file_tree_pattern = subfolder_pattern + "/" + file_name
                    new_sub_patterns[new_file_tree_pattern] = file['id']
                    logger.debug("Files added :%s", file_name)
            else:
                logger.debug('No Files Found')
    else:
        #all_files = check_for_files(folder['id'])
        all_files=[]
        n_files = len(all_files)
        if n_files != 0:
            for file in all_files:
                file_name = file['name']
                subfolders[folder_tree + '/'+file_name] = file['id']
                new_file_tree_pattern = subfolder_pattern + "/" + file_name
                new_sub_patterns[new_file_tree_pattern] = file['id']
                logger.debug("Files added :%s", file_name)
    return new_sub_patterns 
def check_for_files(folder_id, service):
    other_files = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and parents in '"+folder_id+"' and trashed = false",fields="nextPageToken, files(id, name)",pageSize=400).execute()
    all_other_files = other_files.get('files', [])   
    return all_other_files
def get_folder_tree(folder_id, service):
    folder_tree ="."
    sub_folders = check_for_subfolders(folder_id, service,folder_tree)
    for i,sub_folder_id in enumerate(sub_folders.values()):
        folder_tree = list(sub_folders.keys() )[i]
        logger.debug('Current Folder Tree : %s', folder_tree)
        #folder_ids.update(sub_folders)
        logger.debug('****************************************Recursive Search Begins**********************************************')
        try:
            get_folder_tree(sub_folder_id, service,folder_tree)
        except:
            logger.debug('---------------------------------No furtherance----------------------------------------------')
    return folder_tree     
    
    
    
    
if __name__ == '__main__':
    main()

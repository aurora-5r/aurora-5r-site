#!/home/laurent/.platformio/penv/bin/python
# coding: utf8
"""
test of search-parent method
"""
from __future__ import print_function

import argparse
import json
import logging
import os.path
import pickle
import time
from collections import Counter
from enum import Enum

from apiclient import discovery
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools
import myTorsimany
import myLog

myLog.setup_logging()
logger = logging.getLogger(__name__)


def get_credentials():
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
                "gsuiteFromPythonCred.secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.secret.pickle", "wb") as token:
            pickle.dump(creds, token)
    service = build("drive", "v3", credentials=creds)
    return service


class FileType(Enum):
    """
    file type
    """

    FILE = 0
    FOLDER = 1


class Node:
    """
    class for Google Drive item
    """

    def __init__(self, path, basename, depth, file_type, file_id):
        self.path = path
        self.basename = basename
        self.depth = depth
        self.file_type = file_type
        self.file_id = file_id
        self.children = []

    def print_children(self):
        """
        print all children
        """
        print(
            "{0}{1}    (ID: {2}    file_type: {3})".format(
                "  " * self.depth,
                os.path.basename(self.path),
                self.file_id,
                self.file_type,
            )
        )
        for child in self.children:
            child.print_children()

    def count_children(self):
        """
        count all children
        """
        num_files = 0
        num_folders = 0
        for child in self.children:
            if child.file_type == FileType.FILE:
                num_files += 1
            if child.file_type == FileType.FOLDER:
                num_folders += 1
            a, b = child.count_children()
            num_files += a
            num_folders += b
        return (num_files, num_folders)

    def complement_children_path_depth(self):
        """
        generate children's path and depth information from basename
        """
        for child in self.children:
            child.path = "{0}/{1}".format(self.path, child.basename)
            child.depth = self.depth + 1
            child.complement_children_path_depth()


def get_whole_tree(drive_service):
    MAX_PAGE_SIZE_PER_REQUEST = 100
    email_address = (
        drive_service.about()
        .get(fields="user(emailAddress)")
        .execute()
        .get("user")["emailAddress"]
    )
    root_id = (
        drive_service.files()
        .get(
            fileId="root",
            supportsTeamDrives=False,
            fields="id",
        )
        .execute()
        .get("id")
    )
    root = Node(
        path="root",
        basename="root",
        depth=0,
        file_type=FileType.FOLDER,
        file_id=root_id,
    )
    nodes = {root_id: (root, None)}
    page_token = None

    while True:
        response = (
            drive_service.files()
            .list(
                corpus="user",
                includeTeamDriveItems=False,
                orderBy="name",
                pageSize=MAX_PAGE_SIZE_PER_REQUEST,
                pageToken=page_token,
                q="trashed=false and mimeType='application/vnd.google-apps.folder'",
                spaces="drive",
                supportsTeamDrives=False,
                fields="nextPageToken, files(id, name, mimeType, parents)",
            )
            .execute()
        )
        items = response.get("files", [])
        for item in items:
            file_name = item["name"]
            file_id = item["id"]
            p = item.get("parents")
            if not p:
                p = ["None"]
            parent_id = p[0]
            if item["mimeType"] == "application/vnd.google-apps.folder":
                file_type = FileType.FOLDER
            else:
                file_type = FileType.FILE
            node = Node(
                path=None,
                basename=file_name,
                depth=None,
                file_type=file_type,
                file_id=file_id,
            )
            nodes[file_id] = (node, parent_id)
            logger.debug(
                "file_name: {0}, file_id: {1}, parent_id: {2}".format(
                    file_name, file_id, parent_id
                )
            )

        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

        # connect to parent
    for file_id, (node, parent_id) in nodes.items():
        if parent_id is None:  # root node
            continue
        nodes[parent_id][0].children.append(node)

    root.complement_children_path_depth()
    return root


def do_all_files():
    drive_service = service
    MAX_PAGE_SIZE_PER_REQUEST = 100
    email_address = (
        drive_service.about()
        .get(fields="user(emailAddress)")
        .execute()
        .get("user")["emailAddress"]
    )
    root_id = (
        drive_service.files()
        .get(
            fileId="root",
            supportsTeamDrives=False,
            fields="id",
        )
        .execute()
        .get("id")
    )
    root = Node(
        path="root",
        basename="root",
        depth=0,
        file_type=FileType.FOLDER,
        file_id=root_id,
    )
    nodes = {root_id: (root, None)}
    page_token = None

    while True:
        response = (
            drive_service.files()
            .list(
                corpus="user",
                includeTeamDriveItems=False,
                orderBy="name",
                pageSize=MAX_PAGE_SIZE_PER_REQUEST,
                pageToken=page_token,
                q="trashed=false and mimeType='application/vnd.google-apps.folder'",
                spaces="drive",
                supportsTeamDrives=False,
                fields="nextPageToken, files(id, name, mimeType, parents)",
            )
            .execute()
        )
        items = response.get("files", [])
        for item in items:
            file_name = item["name"]
            file_id = item["id"]
            p = item.get("parents")
            if not p:
                p = ["None"]
            parent_id = p[0]
            if item["mimeType"] == "application/vnd.google-apps.folder":
                file_type = FileType.FOLDER
            else:
                file_type = FileType.FILE
            node = Node(
                path=None,
                basename=file_name,
                depth=None,
                file_type=file_type,
                file_id=file_id,
            )
            nodes[file_id] = (node, parent_id)
            logger.debug(
                "file_name: {0}, file_id: {1}, parent_id: {2}".format(
                    file_name, file_id, parent_id
                )
            )

        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break

        # connect to parent
    for file_id, (node, parent_id) in nodes.items():
        if parent_id is None:  # root node
            continue
        nodes[parent_id][0].children.append(node)

    root.complement_children_path_depth()
    return root


def gdocToMarkdown(file):
    logger.debug("Begin")

    service = discovery.build(
        "docs", "v1", http=creds.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC
    )
    logger.debug("result")

    # Do a document "get" request and print the results as formatted JSON
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    logger.debug("dumps")
    with open("data.json", "w") as outfile:
        json.dump(doc, outfile)
    logger.debug("END")


if __name__ == "__main__":

    service = get_credentials()

    start_time = time.time()
    gdocToJson("1j83LoMiRQDuqBvGSxwgOaYiGhcdn6CLuKsFel4EvhNY")

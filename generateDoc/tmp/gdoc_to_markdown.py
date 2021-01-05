#!/usr/bin/env python
# coding: utf8
"""
test of search-parent method
"""
from __future__ import print_function
import re
import unicodedata
import json
import logging
import os.path
import time
from .settings import LoadSettingsFile
from .settings import ValidateSettings
from .settings import SettingsError
from .settings import InvalidConfigError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

my_init.setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

FILETYPE = {
    "DOC": ("application/vnd.google-apps.document", "Google Doc"),
    "FOLDER": ("application/vnd.google-apps.folder", "Folder")
}


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def mime_to_filetype(mime_string):
    """convert mimi type in simple string

    Args:
        mime_string (string)

    Returns:
        string : [description]
    """
    for label, carac in FILETYPE.items():
        if carac[0] == mime_string:
            return label
    logger.warning("Unknown mime type : %s", mime_string)
    return "UNKNOWN"


class Node:
    """
    class for Google Drive item
    """

    def __init__(self, path, basename, depth, file_type, file_id, content):
        self.path = path
        self.basename = basename
        self.depth = depth
        self.file_type = file_type
        self.file_id = file_id
        self.content = content

        self.children = []
        self.files = []

    def print_children(self):
        """
        return all children
        """
        message = "{0}{1}    (ID: {2} NAME : {3} file_type: {4})\n".format(
            "  " * self.depth*4,
            os.path.basename(self.path),
            self.file_id,
            self.basename,
            self.file_type,
        )

        for child in self.children:
            message = message+child.print_children()
        return message

    def list_children(self):
        """
        list all children
        """
        list_files = set()
        list_folders = set()

        for child in self.children:
            if child.file_type == "DOC":
                list_files.add(child.file_id)

            if child.file_type == "FOLDER":
                list_folders.add(child.file_id)
                child_files, child_folders = child.list_children()

                if child_files:
                    list_files = list_files.union(child_files)
                if child_folders:
                    list_folders = list_folders.union(child_folders)
        return (list_files, list_folders)

    def complement_children_path_depth(self):
        """
        generate children's path and depth information from basename
        """
        for child in self.children:
            # logger.debug("%s %s %d", self.path, child.basename, self.depth)
            child.path = "{0}/{1}".format(self.path, child.basename)
            child.depth = self.depth + 1
            child.complement_children_path_depth()


def query_drive(service, drive_id="", root_drive="", query="trashed=false"):
    """Launch a query

    Args:
        service
        drive_id . Defaults to "".
        root_drive (Node, optional) default to ""
        query (str, optional):. Defaults to "trashed=false".
    """
    logger.debug("Query : %s", query)
    if root_drive:
        nodes = {drive_id: (root_drive, None)}
    else:
        nodes = {}
    page_token = None
    while True:
        if drive_id != "":
            response = (
                service.files()
                .list(
                    corpora="drive",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    driveId=drive_id,
                    orderBy="name",
                    pageSize=100,
                    pageToken=page_token,
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, parents,content)",
                )
                .execute()
            )
        else:
            response = (
                service.files()
                .list(
                    corpora="user",
                    orderBy="name",
                    pageSize=100,
                    pageToken=page_token,
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, parents,content)",
                )
                .execute()
            )
        items = response.get("files", [])
        for item in items:
            file_name = item["name"]
            file_id = item["id"]
            content = item.get("content")
            item_parents = item.get("parents")
            if not item_parents:
                item_parents = ["None"]
            parent_id = item_parents[0]

            node = Node(
                path=None,
                basename=file_name,
                depth=None,
                file_type=mime_to_filetype(item["mimeType"]),
                file_id=file_id,
                content=content
            )
            nodes[file_id] = (node, parent_id)

        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break
    return nodes


def list_all_files(service, drive_id="", root_folder_id="root"):
    """
    Generate folder structure with files
    Args:
        drive_service (service)
        drive_id : drive id in case of shared drive
        root_folder_id (string): id of the root folder
    Returns:
        Node: tree
    """
    logger.debug("Start")

    root_drive = Node(
        path="/",
        basename="root",
        depth=0,
        file_type="FOLDER",
        file_id=drive_id,
        content=""
    )
    nodes = query_drive(service, drive_id=drive_id, root_drive=root_drive,
                        query="trashed=false and mimeType='application/vnd.google-apps.folder'")
    # connect to parent
    for file_id, (node, parent_id) in nodes.items():
        if file_id == root_folder_id:
            root_folder = node
        if parent_id is None:
            continue
        nodes[parent_id][0].children.append(node)
    root_folder.depth = 0
    root_folder.complement_children_path_depth()
    # get all files
    files, folders = root_folder.list_children()
    parents_id = ' or '.join("'{!s}' in parents".format(key)
                             for key in folders)
    query_for_files = "trashed=false and mimeType='application/vnd.google-apps.document' and (" + \
        parents_id+")"
    all_files = query_drive(service, drive_id=drive_id, root_drive=root_drive,
                            query=query_for_files)
    for file_id, (node, parent_id) in all_files.items():
        if parent_id is None:
            continue
        nodes[parent_id][0].children.append(node)
    root_drive.complement_children_path_depth()

    return root_folder


def gdoc_to_markdown(doc_id):
    """Generate markdown from gdoc

    Args:
        doc_id (string)
    """
    logger.debug("Begin")


if __name__ == "__main__":
    logger.debug("Begin")
    # service_drive = my_init.get_credentials()
    # logger.debug(".")
    # document = query_drive(service_drive, drive_id="", root_drive="",
    #                        query="trashed=false and name ='fichier de test'")
    # tree = list_all_files(service_drive, "0AIZGD5MSHiIcUk9PVA",
    #                       "1HiByc1Lu3MmhinDzxlWtdPvox1RDILPE")
    # result = tree.print_children()
    # print(result)
    gauth = GoogleAuth()
# Creates local webserver and auto handles authentication.
    gauth.LocalWebserverAuth()

    # Create GoogleDrive instance with authenticated GoogleAuth instance
    drive = GoogleDrive(gauth)

# Auto-iterate through all files in the root folder.
    file_list = drive.ListFile(
        {'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        print('title: %s, id: %s' % (file1['title'], file1['id']))

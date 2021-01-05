# -*- coding: utf-8 -*-
import unicodedata
import re

from generateDoc.gstomd.settings import LoadSettingsFile
from generateDoc.gstomd.settings import ValidateSettings
from generateDoc.gstomd.settings import SettingsError
from generateDoc.gstomd.settings import InvalidConfigError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import zipfile
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import uuid
from markdownify import markdownify as md


logger = logging.getLogger(__name__)
FILETYPE = {
    "DOC": ("application/vnd.google-apps.document", "Google Doc"),
    "FOLDER": ("application/vnd.google-apps.folder", "Folder")
}


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
    value = re.sub(r'[^\w\s-]', '', value)
    return re.sub(r'[-\s]+', '', value).strip('-_')


class Node:
    """
    class for Google Drive item
    """

    def __init__(self, path, basename,  node_type, node_id, content="", depth=1):
        self.path = path
        self.basename = basename
        self.depth = depth
        self.type = node_type
        self.id = node_id
        self.content = content

        self.children = []
        self.files = []

    def __str__(self):
        if self.type == "FOLDER":
            return "type : %s, id : %s, basename : %s, unixname: %s, path: %s , children %s" % (self.type, self.id, self.basename, self.unix_name(), self.path, self.print_children())
        else:
            return "type : %s, id : %s, basename : %s,  unixname: %s, path: %s\n content: %s" % (self.type, self.id, self.basename, self.unix_name(), self.path, self.content)

    def print_short(self):
        if self.type == "FOLDER":
            return "type : %s, id : %s, basename : %s,  unixname: %s, path: %s" % (self.type, self.id, self.basename, self.unix_name(), self.path)
        else:
            return "type : %s, id : %s, basename : %s,  unixname: %s, path: %s\n content: %s" % (self.type, self.id, self.basename, self.unix_name(), self.path, self.content)

    def unix_name(self):
        return slugify(self.basename)

    def print_children(self):
        """
        return all children
        """
        if self.depth:
            message = "{0} {1}".format(
                "  " * self.depth*4, self.print_short()
            )
        else:
            logger.warning("depth not set")
            message = " "

        if self.children:
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
            if child.type == "DOC":
                list_files.add(child.id)

            if child.type == "FOLDER":
                list_folders.add(child.id)
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
        logger.debug(self)
        for child in self.children:
            child.path = "{0}/{1}".format(self.path, child.unix_name())
            child.depth = self.depth + 1
            child.complement_children_path_depth()

    def create_folders(self):
        """
        create folders
        """
        if self.type == "FOLDER":
            logger.debug("create folder %s", self.path)

            os.makedirs(self.path)
            if self.children:
                for child in self.children:
                    child.create_folders()

    def create_files(self):
        """
        create files
        """
        if self.type == "DOC":
            os.makedirs(self.path)
            zip_path = self.path+"/"+os.path.basename(self.path)+".zip"
            md_path = self.path+"/"+os.path.basename(self.path)+".md"

            logger.debug("write file %s", zip_path)
            f_zip = open(zip_path, "wb")
            f_zip.write(self.content_zip)
            f_zip.close()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:

                files_names = zip_ref.namelist()
                for file_name in files_names:
                    if file_name.endswith('.html'):
                        f_md = open(md_path, "w")
                        html = zip_ref.read(file_name)
                        parsed_html = BeautifulSoup(html)
                        body = "%s" % (parsed_html.body)
                        logger.debug("parsed :%s", parsed_html)

                        logger.debug("body :%s", body)
                        body_md = md(body)
                        f_md.write(body_md)
                        f_md.close()
                    else:
                        zip_ref.extract(file_name, os.path.dirname(md_path))
            os.remove(zip_path)

        if self.children:
            for child in self.children:
                child.create_files()


class Gdoc(Node):
    def __init__(self,  path, basename, depth, id, content):

        super().__init__(path, basename, depth, "DOC", id, content)

    def to_md(self):
        logger.debug("in")


class Corpus():
    DEFAULT_SETTINGS = {
        'pydrive_settings': 'pydrive_settings.yaml',
        'dest_folder': './data'
    }

    def __init__(self, pydrive_settings='pydrive_settings.yaml', drive_id='', root_folder_id='root', dest_folder='./data', root_folder_name='root'):
        """Create an instance of Corpus.
        :param settings_file: path of settings file. 'settings.yaml' by default.
        :type settings_file: str.
        """
        self.drive_id = drive_id
        self.root_folder_id = root_folder_id
        self.dest_folder = dest_folder
        self.root_folder_name = root_folder_name

        self.ga = GoogleAuth(pydrive_settings)
        self.drive = GoogleDrive(self.ga)
        self.gscontent = {}

    def get_source(self):
        """
        Generate folder structure with files

        Returns:
            Node: tree
        """

        logger.debug("Start")
        drive_id = self.drive_id
        root_folder_id = self.root_folder_id
        dest_folder = self.dest_folder
        root_folder_name = self.root_folder_name
        root_drive = Node(
            path="./",
            basename="root",
            depth=0,
            node_type="FOLDER",
            node_id=drive_id,
            content=""
        )
        root_folder = root_drive

        nodes = {root_drive.id: (root_drive, None)}
        query = "trashed=false and mimeType='application/vnd.google-apps.folder'"
        if drive_id != "":
            param = {
                'corpora': "drive",
                'supportsAllDrives': True,
                'includeItemsFromAllDrives': True,
                'driveId': drive_id,
                'q': query,

            }
        else:
            param = {
                'corpora': "user",
                'q': query,
            }
        folders_list = self.drive.ListFile(
            param).GetList()
        for item in folders_list:
            file_name = item["title"]
            file_id = item["id"]
            content = item.get("content")
            item_parents = item.get("parents")
            # logger.debug(item_parents)
            if not item_parents:
                parent_id = root_drive.id
            else:
                parent_id = item_parents[0]['id']

            node = Node(
                path=None,
                basename=file_name,
                depth=1,
                node_type=mime_to_filetype(item["mimeType"]),
                node_id=file_id,
                content=content
            )
            nodes[file_id] = (node, parent_id)

        for file_id, (node, parent_id) in nodes.items():
            if file_id == root_folder_id:
                root_folder = node
                logger.debug("root_folder found :%s", root_folder)
            if parent_id is None:
                continue
            if parent_id in nodes.keys():

                nodes[parent_id][0].children.append(node)
            else:
                logger.warning("parent id %s not found", parent_id)
        root_folder.depth = 1
        now = datetime.now()
        date_time = now.strftime("%Y.%m.%d.%H.%M.%S")
        root_folder.path = "%s/%s/%s" % (dest_folder,
                                         root_folder_name, date_time)

        root_folder.complement_children_path_depth()
        # get all files
        files, folders = root_folder.list_children()
        parents_id = ' or '.join(
            "'{!s}' in parents".format(key) for key in folders)
        parents_id = "%s or '%s' in parents" % (parents_id, root_folder_id)
        query_for_files = "trashed=false and mimeType='application/vnd.google-apps.document' and (" + \
            parents_id+")"
        param['q'] = query_for_files
        files_list = self.drive.ListFile(
            param).GetList()

        for item in files_list:
            file_name = item["title"]
            file_id = item["id"]
            content = item.get("content")
            item_parents = item.get("parents")
            is_root = item.get("isRoot")
            if not item_parents:
                parent_id = "None"
            else:
                if is_root:
                    parent_id = "root"
                else:
                    parent_id = item_parents[0]['id']

                node = Node(
                    path=None,
                    basename=file_name,
                    depth=1,
                    node_type=mime_to_filetype(item["mimeType"]),
                    node_id=file_id,
                )
                if node.type == "DOC":
                    logger.debug("fetch content for %s", node)
                    logger.debug("item metadata  %s", item.metadata)
                    item.FetchContent(mimetype='text/html')
                    node.content_md = md(item.content.getvalue())
                    item.FetchContent(
                        mimetype='application/zip', remove_bom=True)
                    node.content_zip = item.content.getvalue()
                else:
                    logger.debug("NO fetch content for %s", node)
                # logger.debug(node)

                # logger.debug(parent_id)
                if parent_id in nodes.keys():

                    nodes[parent_id][0].children.append(node)
                else:
                    logger.warning("parent id %s not found", parent_id)
        root_folder.complement_children_path_depth()
        # for file_id, (node, parent_id) in nodes.items():
        #    logger.debug("%s, (parent : %s)", node, parent_id)
        # logger.debug(node.print_children())
        self.gscontent = root_folder
        return root_folder

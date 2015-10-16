from django.db import models
from xml.dom.minidom import parse
import xml.dom.minidom
import os.path

BASE = os.path.dirname(os.path.abspath(__file__))


class Project:
    def __init__(self, title, date, version, summary='No summary.'):
        self.title = title
        self.date = date
        self.version = version
        self.summary = summary
        self.documents = {}  # File path as key.

    def add_document(self, document):
        self.documents[document.path] = document


class Document:
    def __init__(self, name, size, file_type, path):
        self.name = name
        self.size = size
        self.file_type = file_type
        self.path = path
        self.versions = {}  # Revision number as key.

    def add_version(self, version):
        self.versions[version.revision_num] = version


class Version:
    def __init__(self, revision_num, author, info, date):
        self.revision_num = revision_num
        self.author = author
        self.info = info
        self.date = date


class SVNParser:
    def __init__(self):
        self.projects = {}

    def parse_project(self, path_to_list):
        entries = self.get_entries(path_to_list)
        for entry in entries:
            if entry.hasAttribute("kind"):
                if entry.getAttribute("kind") == 'dir':
                    name_node = entry.getElementsByTagName('name')[0]
                    title = str(name_node.childNodes[0].data)
                    if "/" not in title:  # Top level directory means projects.
                        version = str(entry.getElementsByTagName('commit')[0].getAttribute('revision'))
                        date = str(entry.getElementsByTagName('date')[0].childNodes[0].data)
                        p = Project(title, date, version)
                        self.projects[title] = p

    def get_entries(self, path_to_list):
        dom_tree = xml.dom.minidom.parse(path_to_list)
        lists = dom_tree.documentElement
        entries = lists.getElementsByTagName("entry")
        return entries

    def parse_document(self, path_to_list):
        entries = self.get_entries(path_to_list)
        for entry in entries:
            if entry.hasAttribute("kind"):
                if entry.getAttribute("kind") == 'file':
                    name_node = entry.getElementsByTagName('name')[0]
                    path = str(name_node.childNodes[0].data)
                    size = str(entry.getElementsByTagName('size')[0].childNodes[0].data)
                    project_name = path.split('/')[0]
                    if project_name in self.projects:
                        name = str(path.split('/')[-1])
                        file_type = name.split('.')[-1]
                        d = Document(name, size, file_type, str(path))
                        self.projects[project_name].add_document(d)

    def parse_version(self, path_to_log):
        log_entries = self.get_logentries(path_to_log)

        for log_entry in log_entries:
            revision = str(log_entry.getAttribute('revision'))
            paths = log_entry.getElementsByTagName('path')
            msg_node = log_entry.getElementsByTagName('msg')[0]
            msg = "No information."
            if msg_node.hasChildNodes():
                msg = str(log_entry.getElementsByTagName('msg')[0].childNodes[0].data)
            author = str(log_entry.getElementsByTagName('author')[0].childNodes[0].data)
            date = str(log_entry.getElementsByTagName('date')[0].childNodes[0].data)
            self.add_versions(author, date, msg, paths, revision)

    def add_versions(self, author, date, msg, paths, revision):
        for path_node in paths:
            path = '/'.join(path_node.childNodes[0].data.split('/')[2:])
            project_name = path.split('/')[0]
            if project_name in self.projects:
                project = self.projects[project_name]
                if project.version == revision:
                    project.summary = msg
                if path in project.documents:
                    self.projects[project_name].documents[path].add_version(Version(revision, author, msg, date))

    def get_logentries(self, path_to_log):
        dom_tree = xml.dom.minidom.parse(path_to_log)
        log = dom_tree.documentElement
        log_entries = log.getElementsByTagName("logentry")
        return log_entries

    def parse_all(self):
        self.parse_project(BASE + "/static/portfolio/svn_list.xml")
        self.parse_document(BASE + "/static/portfolio/svn_list.xml")
        self.parse_version(BASE + "/static/portfolio/svn_log.xml")
        return self.projects





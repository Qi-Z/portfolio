from django.shortcuts import render
from django.http import HttpResponse
from .models import SVNParser


def index(request):
    svn_parser = SVNParser()
    context = {'projects': svn_parser.parse_all()}
    return render(request, 'portfolio/index.html', context)


def detail(request, project_name):
    svn_parser = SVNParser()
    context = {'files': svn_parser.parse_all()[str(project_name)].documents, 'project': str(project_name)}
    return render(request, 'portfolio/project.html', context)


def file_detail(request, file_path):
    svn_parser = SVNParser()
    file_path = str('/'.join(file_path.split('/')[0:-2]))
    context = {'file': file_path.split('/')[-1], 'versions': svn_parser.parse_all()[file_path.split('/')[0]].documents[file_path].versions}
    context['path'] = "https://subversion.ews.illinois.edu/svn/fa15-cs242/qizhang4/"+file_path
    return render(request, 'portfolio/file.html', context)

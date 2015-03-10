import os
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer

def make_renderer(path):
    return Renderer(FileSystemLoader(path))

def dump(args):
    r = make_renderer(os.getcwd())

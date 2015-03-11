import os
import yaml
import json
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer


def make_renderer(path):
    return Renderer(FileSystemLoader(path))


def load_definition(path):
    with open(path) as f:
        return yaml.safe_load(f)


def dump(args):
    definition = load_definition(args.cloud_definition)
    template = definition[args.name]['templates'][args.template]
    r = make_renderer(os.getcwd())
    return json.dumps(r.render_template((args.template, template)))

import os
import yaml
import json
import argparse
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer


def make_renderer(path):
    return Renderer(FileSystemLoader(path))


def load_definition(path):
    with open(path) as f:
        return yaml.safe_load(f)


def dump(args):
    definitions = load_definition(args.yamlfile)
    template = definitions[args.definition_name]['templates'][args.template_name]
    r = make_renderer(os.getcwd())
    return json.dumps(r.render_template((args.template_name, template)))


def cloudplate():
    parser = argparse.ArgumentParser()
    dump_p = parser.add_subparsers('dump', func=dump)
    dump_p.add_argument('yamlfile', description='The file to read the Cloudplate definitions from', required=True)
    dump_p.add_argument('definition_name', description='The definition name', required=True)
    dump_p.add_argument('template_name', description='The template name')

    parser.parse_args()
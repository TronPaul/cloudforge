import os
import yaml
import json
import argparse
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer


class DefinitionLookupError(LookupError):
    def __init__(self, definition_name, yamlfile):
        self.definition_name = definition_name
        self.yamlfile = yamlfile

    def __str__(self):
        return 'Definition {} not found in {}'.format(self.definition_name, self.yamlfile)


class TemplateLookupError(LookupError):
    def __init__(self, template_name, definition_name):
        self.template_name = template_name
        self.definition_name = definition_name

    def __str__(self):
        return 'Template {} not found in {}'.format(self.template_name, self.definition_name)


def make_renderer(path):
    return Renderer(FileSystemLoader(path))


def load_definition(path):
    with open(path) as f:
        return yaml.safe_load(f)


def dump(args):
    definitions = load_definition(args.yamlfile)
    if args.definition_name not in definitions:
        raise DefinitionLookupError(args.definition_name, args.yamlfile)
    definition = definitions[args.definition_name]
    if args.template_name not in definition['templates']:
        raise TemplateLookupError(args.template_name, args.definition_name)
    template = definitions[args.definition_name]['templates'][args.template_name]
    r = make_renderer(os.getcwd())
    return json.dumps(r.render_template((args.template_name, template)))


def cloudplate():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    dump_p = subparsers.add_parser('dump')
    dump_p.set_defaults(func=dump)
    dump_p.add_argument('yamlfile', help='The file to read the Cloudplate definitions from')
    dump_p.add_argument('definition_name', help='The definition name')
    dump_p.add_argument('template_name', help='The template name')

    args = parser.parse_args()
    args.func(args)
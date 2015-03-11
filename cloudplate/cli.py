import os
import yaml
import json
import argparse
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer
from cloudplate.cloudforge import forge_stack


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


def cp_definition(yamlfile, definition_name):
    definitions = load_definition(yamlfile)
    if definition_name not in definitions:
        raise DefinitionLookupError(definition_name, yamlfile)
    return definitions[definition_name]


def cf_template(definition_name, definition, template_name):
    if template_name not in definition['templates']:
        raise TemplateLookupError(template_name, definition_name)
    template_def = definition['templates'][template_name]
    r = make_renderer(os.getcwd())
    return json.dumps(r.render_template((template_name, template_def)))


def dump(args):
    definition = cp_definition(args.yamlfile, args.definition_name)
    return cf_template(args.definition_name, definition, args.template_name)


def create(args):
    definition = cp_definition(args.yamlfile, args.definition_name)
    template = cf_template(args.definition_name, definition, args.template_name)
    forge_stack(template)


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

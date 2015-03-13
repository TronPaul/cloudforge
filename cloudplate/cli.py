import argparse
import os
import yaml
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer
from cloudplate.cloudforge import Forge, make_template_body
from cloudplate.util import connect_to_cf


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


def dump(args):
    definition = cp_definition(args.yamlfile, args.definition_name)
    if args.template_name not in definition['templates']:
        raise TemplateLookupError(args.template_name, args.definition_name)
    return make_template_body(make_renderer(os.getcwd()), definition['templates'][args.template_name])


def create(args):
    definition = cp_definition(args.yamlfile, args.definition_name)
    template_body = cf_template_body(args.definition_name, definition, args.template_name)
    ctcf_opts = {}
    role = definition.get('role')
    if role:
        ctcf_opts['role_arn'] = role.pop('role_arn')
        ctcf_opts['role_session_name'] = role.pop('role_session_name')
        ctcf_opts['role_opts'] = role
    connection = connect_to_cf(definition['region'], **ctcf_opts)
    forge_stack(connection, args.template_name, template_body)


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

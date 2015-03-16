import argparse
import os
import yaml
from cloudforge.render import make_renderer
from cloudforge.forge import Forge, make_template_body
from cloudforge.aws import connect


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


def read_yamlfile(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_definition(yamlfile, definition_name):
    definitions = read_yamlfile(yamlfile)
    if definition_name not in definitions:
        raise DefinitionLookupError(definition_name, yamlfile)
    return definitions[definition_name]


def dump(args):
    definition = load_definition(args.yamlfile, args.definition_name)
    if args.template_name not in definition['templates']:
        raise TemplateLookupError(args.template_name, args.definition_name)
    return make_template_body(make_renderer(), definition['templates'][args.template_name])


def create(args):
    definition = load_definition(args.yamlfile, args.definition_name)
    connection = connect(definition)
    forge = Forge(connection, make_renderer())
    forge.forge_definition(args.definition_name, definition)


def cloudforge():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    dump_p = subparsers.add_parser('dump')
    dump_p.set_defaults(func=dump)
    dump_p.add_argument('yamlfile', help='The file to read the Cloudplate definitions from')
    dump_p.add_argument('definition_name', help='The definition name')
    dump_p.add_argument('template_name', help='The template name')

    args = parser.parse_args()
    args.func(args)

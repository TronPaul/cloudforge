import argparse
import json
import os
import yaml
from cloudforge.render import make_renderer
from cloudforge.forge import Forge, make_template_body
from cloudforge.aws import connect, dry_run_connection


class DefinitionLookupError(LookupError):
    def __init__(self, definition_name, yamlfile):
        self.definition_name = definition_name
        self.yamlfile = yamlfile

    def __str__(self):
        return 'Definition {} not found in {}'.format(self.definition_name, self.yamlfile)


class StackLookupError(LookupError):
    def __init__(self, stack_name, definition_name):
        self.stack_name = stack_name
        self.definition_name = definition_name

    def __str__(self):
        return 'Stack {} not found in {}'.format(self.stack_name, self.definition_name)


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
    if args.stack_name not in definition['stacks']:
        raise StackLookupError(args.stack_name, args.definition_name)
    return json.dumps(make_template_body(make_renderer(definition), definition['stacks'][args.stack_name]))


def create(args):
    definition = load_definition(args.yamlfile, args.definition_name)
    if args.noop:
        connection = dry_run_connection(definition)
    else:
        connection = connect(definition)
    forge = Forge(connection, make_renderer(definition))
    forge.forge_definition(args.definition_name, definition)


def cloudforge():
    parser = argparse.ArgumentParser(description='Forge CloudFormation stacks')
    subparsers = parser.add_subparsers()

    dump_p = subparsers.add_parser('dump', description='Dump template from Cloudforge definition')
    dump_p.set_defaults(func=dump)
    dump_p.add_argument('yamlfile', help='The file to read the Cloudplate definitions from')
    dump_p.add_argument('definition_name', help='The definition name')
    dump_p.add_argument('stack_name', help='The stack name')

    create_p = subparsers.add_parser('create', description='Create stack in CloudFormation from Cloudforge definition')
    create_p.set_defaults(func=create)
    create_p.add_argument('yamlfile', help='The file to read the Cloudplate definitions from')
    create_p.add_argument('definition_name', help='The definition name')
    create_p.add_argument('--noop', action='store_true', help='Use a fake connection to simulate a run')

    args = parser.parse_args()
    rv = args.func(args)
    if rv:
        print rv

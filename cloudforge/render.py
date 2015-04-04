import json
import yaml
import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_BASE = {'AWSTemplateFormatVersion': '2010-09-09'}


def make_renderer(definition):
    if 'template_path' in definition:
        return Renderer(FileSystemLoader(definition['template_path']))
    else:
        return Renderer(FileSystemLoader('./'))


def stringify(thing):
    if isinstance(thing, dict):
        return {k: stringify(v) for k, v in thing.items()}
    elif isinstance(thing, list):
        return [stringify(v) for v in thing]
    elif isinstance(thing, int) or isinstance(thing, bool):
        return str(thing)
    else:
        return thing


class Renderer(object):
    def __init__(self, loader):
        self.env = Environment(loader=loader)

    def render_resource(self, resource_def, parent_variables=None):
        variables = parent_variables or {}
        if resource_def[1]:
            name = resource_def[1].get('name', resource_def[0])
            template_path = resource_def[1].get('template', resource_def[0] + '.yaml')
            variables.update(resource_def[1].get('variables', {}))
        else:
            name = resource_def[0]
            template_path = resource_def[0] + '.yaml'
        template = self.env.get_template(template_path)
        return {name: yaml.safe_load(template.render(**variables))}

    def render_template(self, template_def, parent_variables=None):
        variables = parent_variables or {}
        if 'resource_chunk' in template_def:
            with open(template_def['resource_chunk']) as fp:
                rendered_resources = json.load(fp)
        else:
            rendered_resources = {}
        if 'resources' in template_def:
            resources_def = template_def['resources']
            if not isinstance(resources_def, dict):
                raise MalformedTemplateError(template_def, "bad resources definition")
            resource_defs = resources_def.items()
            variables.update(template_def.get('variables', {}))
            for resource_def in resource_defs:
                rendered_resources.update(self.render_resource(resource_def, variables))
        if not rendered_resources:
            raise NoResourcesError(template_def)
        template = TEMPLATE_BASE.copy()
        template['Resources'] = rendered_resources
        parameter_defs = template_def.get('parameters', {}).items()
        if parameter_defs:
            parameters = {}
            for name, parameter_def in parameter_defs:
                param = {name: {k.capitalize(): v for k, v in parameter_def.items() if k != 'source'}}
                parameters.update(param)
            template['Parameters'] = parameters
        return stringify(template)


class MalformedTemplateError(Exception):
    def __init__(self, template_def, reason):
        self.reason = reason
        self.template_def = template_def

    def __str__(self):
        return "Template {}:{} {0}".format(self.reason, *self.template_def)


class NoResourcesError(MalformedTemplateError):
    def __init__(self, template_def):
        super(NoResourcesError, self).__init__(template_def, "has no resources")

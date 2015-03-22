import yaml
import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_BASE = {'AWSTemplateFormatVersion': '2010-09-09'}


def make_renderer():
    return Renderer(FileSystemLoader(os.getcwd()))


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
        if 'resources' not in template_def:
            raise NoResourcesError(template_def)
        resources = template_def['resources']
        if not isinstance(resources, dict):
            raise MalformedTemplateError(template_def, "bad resources definition")
        if not resources:
            raise NoResourcesError(template_def)
        resource_defs = resources.items()
        variables.update(template_def.get('variables', {}))
        template = TEMPLATE_BASE.copy()
        resources = {}
        for resource_def in resource_defs:
            resources.update(self.render_resource(resource_def, variables))
        template['Resources'] = resources
        parameter_defs = template_def.get('parameters', {}).items()
        if parameter_defs:
            parameters = {}
            for name, parameter_def in parameter_defs:
                type_ = parameter_def['type'].capitalize()
                parameters.update({name: {'Type': type_}})
            template['Parameters'] = parameters
        return template


class MalformedTemplateError(Exception):
    def __init__(self, template_def, reason):
        self.reason = reason
        self.template_def = template_def

    def __str__(self):
        return "Template {}:{} {0}".format(self.reason, *self.template_def)


class NoResourcesError(MalformedTemplateError):
    def __init__(self, template_def):
        super(NoResourcesError, self).__init__(template_def, "has no resources")

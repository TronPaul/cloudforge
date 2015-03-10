import yaml
from jinja2 import Environment, FileSystemLoader

TEMPLATE_BASE = {'AWSTemplateFormatVersion': '2010-09-09'}

class Renderer(object):
    def __init__(self, loader):
        self.env = Environment(loader=loader)

    def render_cloudlet(self, cloudlet_def, global_variables=None):
        variables = global_variables or {}
        if cloudlet_def[1]:
            name = cloudlet_def[1].get('name', cloudlet_def[0])
            template_path = cloudlet_def[1].get('template', cloudlet_def[0] + '.yaml')
            variables.update(cloudlet_def[1].get('variables', {}))
        else:
            name = cloudlet_def[0]
            template_path = cloudlet_def[0] + '.yaml'
        template = self.env.get_template(template_path)
        return {name: yaml.safe_load(template.render(**variables))}


    def render_template(self, template_def):
        name, template_options = template_def
        if 'cloudlets' not in template_options:
            raise NoCloudletsError(template_def)
        cloudlets = template_options['cloudlets']
        if not isinstance(cloudlets, dict):
            raise MalformedTemplateError(template_def, "bad cloudlets definition")
        if not cloudlets:
            raise NoCloudletsError(template_def)
        cloudlet_defs = cloudlets.items()
        variables = template_options.get('variables', {})
        template = TEMPLATE_BASE.copy()
        resources = {}
        for cloudlet_def in cloudlet_defs:
            resources.update(self.render_cloudlet(cloudlet_def, variables))
        template['Resources'] = resources
        parameter_defs = template_options.get('parameters', {}).items()
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


class NoCloudletsError(MalformedTemplateError):
    def __init__(self, template_def):
        super(NoCloudletsError, self).__init__(template_def, "has no cloudlets")

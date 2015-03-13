import os
import json
from jinja2 import FileSystemLoader
from cloudplate.render import Renderer
from cloudplate.util import connect_to_cf


def order_templates(templates):
    dep_graph = {}
    satisfied_deps = []
    sorted_templates = []
    for name, template in templates.items():
        deps = set()
        if 'parameters' in template:
            for p_name, p_def in template['parameters'].items():
                if 'source' in p_def:
                    deps.add(p_def['source'])
        if 'requires' in template:
            deps.update(template['requires'])
        if deps:
            for dep in deps:
                if dep not in templates:
                    raise MissingDependencyError(name, dep)
            else:
                dep_graph[name] = list(deps)
        else:
            satisfied_deps.append(name)
    while len(satisfied_deps) > 0:
        completed_name = satisfied_deps.pop()
        sorted_templates.append((completed_name, templates[completed_name]))
        for name, deps in dep_graph.items():
            if completed_name in deps:
                deps.remove(completed_name)
                if not deps:
                    satisfied_deps.append(name)
                    del dep_graph[name]
    if len(dep_graph) > 0:
        raise CircularDependencyError(dep_graph.keys())
    return sorted_templates


def make_template_body(renderer, template, parent_variables=None):
    return json.dumps(renderer.render_template(template, parent_variables=None))


def build_parameters(connection, parameters):
    pass


class Forge(object):
    def __init__(self, region, **connect_opts):
        self.renderer = Renderer(FileSystemLoader(os.getcwd()))
        self.connection = connect_to_cf(region, **connect_opts)

    def forge_template(self, name, template, parent_variables=None):
        parameters = build_parameters(self.connection, template['parameters'])
        template_body = make_template_body(self.renderer, template, parent_variables)
        self.connection.create_stack(name, template_body=template_body, parameters=parameters)

    def forge_definition(self, name, definition):
        templates = order_templates(definition['templates'])
        variables = definition.get('variables')
        for name, template in templates:
            self.forge_template(name, template, variables)


class CircularDependencyError(Exception):
    def __init__(self, remaining_dependencies):
        self.remaining_dependencies = remaining_dependencies

    def __str__(self):
        return 'Templates {} have a circular dependency'.format(self.remaining_dependencies)


class MissingDependencyError(Exception):
    def __init__(self, template_name, dependency_name):
        self.template_name = template_name
        self.dependency_name = dependency_name

    def __str__(self):
        return 'Template {} requires {}, but is not defined'
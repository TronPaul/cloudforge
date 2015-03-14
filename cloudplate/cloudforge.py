import json


def order_templates(templates):
    dep_graph = {}
    satisfied_deps = []
    sorted_templates = []
    for name, template in templates.items():
        deps = set()
        if 'parameters' in template:
            for p_name, p_def in template['parameters'].items():
                if 'source' in p_def:
                    deps.add(p_def['source']['template'])
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
    return json.dumps(renderer.render_template(template, parent_variables=parent_variables))


def get_cf_value(connection, stack_name, value_name, value_type):
    if 'resource' == value_type:
        rv = connection.describe_stack_resource(stack_name, value_name)
        return rv['DescribeStackResourceResponse']['DescribeStackResourceResult']['StackResourceDetail'][
            'PhysicalResourceId']
    else:
        stack = connection.describe_stacks(stack_name)[0]
        if 'output' == value_type:
            vals = [o.value for o in stack.outputs if o.key == value_name]
        elif 'parameter' == value_type:
            vals = [p.value for p in stack.parameters if p.key == value_name]
        else:
            raise BadCloudformationValueType(value_type)
        if vals:
            return vals[0]
    raise CloudformationValueNotFound(stack_name, value_name, value_type)


def build_parameters(connection, parameters):
    cf_params = []
    for p_name, p_def in parameters.items():
        if 'source' in p_def:
            remote_param_name = p_def['source'].get('name', p_name)
            value = get_cf_value(connection, p_def['source']['template'], remote_param_name, p_def['source']['type'])
            cf_params.append((p_name, value))
        else:
            cf_params.append((p_name, p_def))
    return cf_params


class Forge(object):
    def __init__(self, connection, renderer):
        self.renderer = renderer
        self.connection = connection

    def forge_template(self, name, template, parent_variables=None):
        parameters = build_parameters(self.connection, template['parameters'])
        template_body = make_template_body(self.renderer, template, parent_variables)
        self.connection.create_stack(name, template_body=template_body, parameters=parameters)

    def forge_definition(self, name, definition):
        templates = order_templates(definition['templates'])
        variables = definition.get('variables')
        for name, template in templates:
            self.forge_template(name, template, variables)


class CloudformationValueNotFound(LookupError):
    def __init__(self, stack_name, param_name, type_):
        self.stack_name = stack_name
        self.param_name = param_name
        self.type_ = type_


class BadCloudformationValueType(ValueError):
    def __init__(self, value_type):
        self.value_type = value_type


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
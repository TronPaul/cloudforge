import json
from boto.exception import BotoServerError
from cloudforge.watcher import Watcher


def order_stacks(stack_definitions):
    dep_graph = {}
    satisfied_deps = []
    sorted_stack_definitions = []
    for name, stack_definition in stack_definitions.items():
        deps = set()
        if 'parameters' in stack_definition:
            for p_name, p_def in stack_definition['parameters'].items():
                if 'source' in p_def:
                    deps.add(p_def['source']['stack'])
        if 'requires' in stack_definition:
            deps.update(stack_definition['requires'])
        if deps:
            for dep in deps:
                if dep not in stack_definitions:
                    raise MissingDependencyError(name, dep)
            else:
                dep_graph[name] = list(deps)
        else:
            satisfied_deps.append(name)
    while len(satisfied_deps) > 0:
        completed_name = satisfied_deps.pop()
        sorted_stack_definitions.append((completed_name, stack_definitions[completed_name]))
        for name, deps in dep_graph.items():
            if completed_name in deps:
                deps.remove(completed_name)
                if not deps:
                    satisfied_deps.append(name)
                    del dep_graph[name]
    if len(dep_graph) > 0:
        raise CircularDependencyError(dep_graph.keys())
    return sorted_stack_definitions


def make_template_body(renderer, template, parent_variables=None):
    return json.dumps(renderer.render_template(template, parent_variables=parent_variables)).replace(r'\\', '\\')


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
        if isinstance(p_def, dict) and 'source' in p_def:
            remote_param_name = p_def['source'].get('name', p_name)
            value = get_cf_value(connection, p_def['source']['stack'], remote_param_name, p_def['source']['type'])
            cf_params.append((p_name, value))
    return cf_params


class StackCreationError(Exception):
    def __init__(self, name, status):
        self.name = name
        self.status = status

    def __str__(self):
        return 'Creation of {} failed, got status: {}'.format(self.name, self.status)


class StackDeletionError(Exception):
    def __init__(self, name, status):
        self.name = name
        self.status = status

    def __str__(self):
        return 'Deletion of {} failed, got status: {}'.format(self.name, self.status)


class StackAlreadyExistsError(Exception):
    def __init__(self, name, status):
        self.name = name
        self.status = status

    def __str__(self):
        return 'Could not create {}, it already exists in status {}'.format(self.name, self.status)


class TemplateValidationError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'AWS could not validate template {}'.format(self.name)


class Forge(object):
    def __init__(self, connection, renderer, log_level='INFO'):
        self.renderer = renderer
        self.connection = connection
        self.watcher = Watcher(connection, log_level)

    def forge_stack(self, name, stack_def, parent_variables=None):
        if 'parameters' in stack_def:
            parameters = build_parameters(self.connection, stack_def['parameters'])
        else:
            parameters = None
        template_body = make_template_body(self.renderer, stack_def, parent_variables)
        try:
            self.connection.validate_template(template_body=template_body)
        except BotoServerError:
            raise TemplateValidationError(name)
        try:
            stack = self.connection.describe_stacks(name)[0]
        except BotoServerError:
            stack = None
        if not stack:
            self.connection.create_stack(name, template_body=template_body, parameters=parameters,
                                         capabilities=['CAPABILITY_IAM'])
        elif stack.stack_status not in ['CREATE_COMPLETE', 'CREATE_IN_PROGRESS']:
            raise StackAlreadyExistsError(name, stack.stack_status)
        if not stack or stack.stack_status in ['CREATE_IN_PROGRESS']:
            status = self.watcher.watch(name, ['CREATE_IN_PROGRESS'])
            if status != 'CREATE_COMPLETE':
                raise StackCreationError(name, status)

    def forge_definition(self, name, definition):
        stacks = order_stacks(definition['stacks'])
        variables = definition.get('variables')
        for name, stack_def in stacks:
            self.forge_stack(name, stack_def, variables)

    def delete_stack(self, name):
        try:
            stack = self.connection.describe_stacks(name)[0]
        except BotoServerError:
            stack = None
        if stack and stack.stack_status not in ['DELETE_COMPLETE', 'DELETE_IN_PROGRESS']:
            self.connection.delete_stack(name)
        if stack and stack.stack_status not in ['DELETE_COMPLETE']:
            status = self.watcher.watch(name, ['DELETE_IN_PROGRESS'])
            if status != 'DELETE_COMPLETE':
                raise StackDeletionError(name, status)

    def delete_definition(self, name, definition):
        stacks = reversed(order_stacks(definition['stacks']))
        for name, _ in stacks:
            self.delete_stack(name)


class CloudformationValueNotFound(LookupError):
    def __init__(self, stack_name, param_name, type_):
        self.stack_name = stack_name
        self.param_name = param_name
        self.type_ = type_

    def __str__(self):
        return 'Stack {} did not have parameter {} with type {}'.format(self.stack_name,
                                                                        self.param_name,
                                                                        self.type_)


class BadCloudformationValueType(ValueError):
    def __init__(self, value_type):
        self.value_type = value_type

    def __str__(self):
        return 'Value type {} is invalid'.format(self.value_type)


class CircularDependencyError(Exception):
    def __init__(self, remaining_dependencies):
        self.remaining_dependencies = remaining_dependencies

    def __str__(self):
        return 'Stacks {} have a circular dependency'.format(self.remaining_dependencies)


class MissingDependencyError(Exception):
    def __init__(self, stack_name, dependency_name):
        self.stack_name = stack_name
        self.dependency_name = dependency_name

    def __str__(self):
        return 'Stack {} requires {}, but is not defined'.format(self.stack_name, self.dependency_name)

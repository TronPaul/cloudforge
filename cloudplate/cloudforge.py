

def has_deps(template_def):
    return template_def[1].get('require', []) > 0


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


def forge_definition(connection, name, definition):
    templates = order_templates(definition['templates'])


def forge_stack(connection, name, template_body, parameters=None):
    connection.create_stack(name, template_body=template_body, parameters=parameters)


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
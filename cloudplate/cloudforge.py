

def has_deps(template):
    return template.get('require', []) > 0


def order_templates(templates):
    for name, t in templates.items():
        ds = t.get('requires', [])
        for d in ds:
            if d not in templates:
                raise MissingDependencyError(name, d)
    return templates.items()


def forge_definition(connection, name, definition):
    templates = definition['templates']
    no_deps = filter(has_deps, templates)


def forge_stack(connection, name, template_body, parameters=None):
    connection.create_stack(name, template_body=template_body, parameters=parameters)


class MissingDependencyError(Exception):
    def __init__(self, template_name, dependency_name):
        self.template_name = template_name
        self.dependency_name = dependency_name

    def __str__(self):
        return 'Template {} requires {}, but is not defined'
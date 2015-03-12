

def has_deps(template):
    return template.get('require', []) > 0


def order_templates(templates):
    return templates.items()


def forge_definition(connection, name, definition):
    templates = definition['templates']
    no_deps = filter(has_deps, templates)



def forge_stack(connection, name, template_body, parameters=None):
    connection.create_stack(name, template_body=template_body, parameters=parameters)
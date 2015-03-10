import yaml


def render_cloudlet(jenv, cloudlet_def):
    if cloudlet_def[1]:
        name = cloudlet_def[1].get('name', cloudlet_def[0])
        template_path = cloudlet_def[1].get('template', cloudlet_def[0] + '.yaml')
        parameters = cloudlet_def[1].get('parameters', {})
    else:
        name = cloudlet_def[0]
        template_path = cloudlet_def[0] + '.yaml'
        parameters = {}
    template = jenv.get_template(template_path)
    return {name: yaml.safe_load(template.render(**parameters))}


def render_template(jenv, template_def):
    cloudlet_defs = template_def[1]['cloudlets'].items()
    template_base = {'AWSTemplateFormatVersion': '2010-09-09'}
    resources = {}
    for cloudlet_def in cloudlet_defs:
        resources.update(render_cloudlet(jenv, cloudlet_def))
    template_base['Resources'] = resources
    return template_base
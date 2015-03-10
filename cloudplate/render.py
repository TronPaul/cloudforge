import yaml


def render_cloudlet(jenv, cloudlet_def):
    if cloudlet_def[1]:
        name = cloudlet_def[1].get('name', cloudlet_def[0])
        template_path = cloudlet_def[1].get('template', cloudlet_def[0] + '.yaml')
    else:
        name = cloudlet_def[0]
        template_path = cloudlet_def[0] + '.yaml'
    template = jenv.get_template(template_path)
    return {name: yaml.safe_load(template.render())}
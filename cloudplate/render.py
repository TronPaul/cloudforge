import yaml


def render_cloudlet(jenv, cloudlet_def):
    template_path = cloudlet_def[0] + '.yaml'
    cloudlet_template = jenv.get_template(template_path)
    if cloudlet_def[1]:
        name = cloudlet_def[1].get('name', cloudlet_def[0])
    else:
        name = cloudlet_def[0]
    return {name: yaml.safe_load(cloudlet_template.render())}
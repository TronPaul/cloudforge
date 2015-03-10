import yaml


def render_cloudlet(jenv, cloudlet_def):
    template_path = cloudlet_def[0] + '.yaml'
    cloudlet_template = jenv.get_template(template_path)
    return {cloudlet_def[0]: yaml.safe_load(cloudlet_template.render())}
from distutils.core import setup

setup(
    name='cloudplate',
    version='0.0.1',
    packages=['cloudplate'],
    url='http://github.com/TronPaul/cloudplate',
    license='Apache-2.0',
    author='Mark McGuire',
    author_email='mark.b.mcg@gmail.com',
    description='',
    requires=['boto', 'jinja2', 'PyYAML', 'mock']
)

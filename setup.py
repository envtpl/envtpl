import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='envtpl',
    version='0.1.0',
    packages=['envtpl'],
    entry_points={
        'console_scripts': ['envtpl = envtpl.envtpl:main']
    },
    install_requires=['argparse>=1.0'],
    author='Andreas Jansson',
    author_email='andreas@jansson.me.uk',
    description=('Simple parameter substitution using environment variables'),
    license='GPL v3',
    keywords='template environment variables parameter substitution docker',
    long_description=read('README.md'),
    url='https://github.com/andreasjansson/envtpl',
)

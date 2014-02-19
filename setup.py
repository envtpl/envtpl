from setuptools import setup

long_description = '''
EnvTpl
======

_Simple parameter substitution using environment variables_

Installation
------------

    pip install envtpl

Usage
-----

This is a Python script that does basic parameter substitution from the command line. For example, if you have a file called file1.py.tpl that looks like

    # file1.py
    my_first_string = '{{ FOO }}'
    my_second_string = '{{ BAR|def }}'

If you pipe that file through envtpl.py, with FOO defined in the shell

    FOO=abc envtpl < file1.py.tpl

the following will be written to stdout:

    # file1.py
    my_first_string = 'abc'
    my_second_string = 'def'

Here, BAR=def was made default, by putting "def" after the pipe symbol (|). If you define BAR at the command line

    FOO=abc BAR=123 ./envtpl.py < file1.py.tpl

you get

    # file1.py
    my_first_string = 'abc'
    my_second_string = '123'

You can also give envtpl a filename

    $ ls
    file1.py.tpl

    $ envtpl -f file1.py.tpl
    $ ls
    file1.py

The input file will be parsed and stripped of the .tpl extension. You can keep the original template by passing in the --keep-template flag

    envtpl -f file1.py.tpl --keep-template

You can also explicitly specify the output file

    envtpl -f file1.py.tpl --output-file file2.py

If an environment variable is missing, the default behaviour is for envtpl to die with exit code 1. You can change that behaviour to insert empty strings instead by passing the --allow-missing flag

    envtpl --allow-missing < file_with_missing_vars.py.tpl

What's the point?
-----------------

I use this script a lot in Docker images, typically in a file called start.sh. A redis startup script could look something like this:

    #!/bin/bash
    # start.sh

    envtpl -f /etc/redis.conf.tpl

    redis-server

To me, that's a bit cleaner than http://blog.james-carr.org/2013/09/04/parameterized-docker-containers/
'''

setup(
    name='envtpl',
    version='0.1.3',
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
    long_description=long_description,
    url='https://github.com/andreasjansson/envtpl',
)

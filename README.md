envtpl
======

_Render jinja2 templates on the command line with shell environment variables_

[![Build Status](https://travis-ci.org/andreasjansson/envtpl.svg?branch=master)](https://travis-ci.org/andreasjansson/envtpl)
[![PyPI version](https://badge.fury.io/py/envtpl.svg)](https://badge.fury.io/py/envtpl)

Installation
------------

    pip install envtpl

How-to
------

Say you have a configuration file called whatever.conf that looks like this

    foo = 123
    bar = "abc"

You can use envtpl to set `foo` and `bar` from the command line by creating a file called whatever.conf.tpl

    foo = {{ FOO }}
    bar = "{{ BAR }}"
    
If you run

    FOO=123 BAR=abc envtpl < whatever.conf.tpl > whatever.conf

you'll get back the original whatever.conf.

You can also specify default values

    foo = {{ FOO | default(123) }}
    bar = "{{ BAR | default("abc") }}"

Running

    FOO=456 envtpl < whatever.conf.tpl > whatever.conf

will generate

    foo = 456
    bar = "abc"

This is all standard [Jinja2 syntax](http://jinja.pocoo.org/docs/templates/), so you can do things like

    {% if BAZ is defined %}
    foo = 123
    {% else %}
    foo = 456
    {% endif %}
    bar = "abc"

If an environment variable is missing, envtpl will throw an error

    $ echo '{{ FOO }} {{ BAR }}' | FOO=123 envtpl
    Error: 'BAR' is undefined

You can change this behaviour to insert empty strings instead by passing the `--allow-missing` flag.

Instead of reading from stdin and writing to stdout, you can pass the input filename as an optional positional argument,
and set the output filename with the `--output-file` (`-o`) argument.

    envtpl -o whatever.conf  whatever.conf.tpl

As a convenience, if you don't specify an output filename and the input filename ends with `.tpl`, the output filename will be the input filename without the `.tpl` extension, i.e.

    envtpl whatever.conf.tpl
    # is equivalent to
    envtpl -o whatever.conf whatever.conf.tpl

By default, envtpl will **delete** the input template file. You can keep it by passing the `--keep-template` flag.

There's a special `environment(prefix='')` function that you can use as a kind of wildcard variable. If you have `hello.tpl`

    hello = {{ FOO }}
    {% for key, value in environment('MY_') %}{{ key }} = {{ value }}
    {% endfor %}

and compile it using

    FOO=world MY_baz=qux MY_foo=bar envtpl hello.tpl

You end up with

    hello = world
    baz = qux
    foo = bar

If you need more complex data structures you can pass in JSON as a string and use the `from_json` filter to turn it into an object you can use in your template:

    FOO='[{"v": "hello"}, {"v": "world"}]' envtpl <<< '{% for x in FOO | from_json %}{{ x.v }}{% endfor %}'

gives

    helloworld

and

    FOO='{"bar": "baz"}' envtpl <<< '{{ (FOO | from_json).bar }}'

renders

    baz

What's the point?
-----------------

I use this script quite a lot in Docker images. [Here](https://github.com/andreasjansson/docker-redis) is an example.

In the CMD script I set up the runtime configuration using environment variables, e.g.

    #!/bin/bash
    # start_container

    envtpl /etc/redis.conf.tpl

    redis-server

This is the use case I've optimised for, so that's why envtpl by default will delete the original template file.

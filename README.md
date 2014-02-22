EnvTpl
======

_Render jinja2 templates on the command line using shell environment variables_

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

Instead of reading from stdin and writing to stdout, envtpl can take `--input-file` (`-f`) and `--output-file` (`-o`) arguments.

    envtpl -f whatever.conf.tpl -o whatever.conf

As a convenience, if you don't specify an output filename and the input filename ends with `.tpl`, the output filename will be the input filename without the `.tpl` extension, i.e.

    envtpl -f whatever.conf.tpl
    # is equivalent to
    envtpl -f whatever.conf.tpl -o whatever.conf

By default, envtpl will **delete** the input template file. You can keep it by passing the `--keep-template` flag.

What's the point?
-----------------

I use this script quite a lot in Docker images. Usually I'll have the CMD execute some file, like /bin/start.sh that sets up the runtime configuration for the container by building configurations from environment variables. A redis example could look like this

    #!/bin/bash
    # start.sh

    envtpl -f /etc/redis.conf.tpl

    redis-server

This is the use case I've optimised for, so that's why envtpl by default will delete the original template file.

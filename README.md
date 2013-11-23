envtpl.py
=========

This is a Python script that does basic parameter substitution from the command line. For example, if you have a file that looks like

    # file1.py
    my_first_string = '{{ FOO }}'
    my_second_string = '{{ BAR|bar }}'

If you pipe that file through envtpl.py, without any environment variables

    ./envtpl.py < file1.py > file1.py

you get

    # file1.py
    my_first_string = ''
    my_second_string = 'bar'

If you define the FOO and BAR environment variables

    FOO=foo BAR=bazzzz ./envtpl.py < file1.py > file1.py

you get

    # file1.py
    my_first_string = 'foo'
    my_second_string = 'bazzzz'

Double curly brackets encloses the name of the environment variable to insert, and the pipe symbol `|` declares a default to insert if the environment variable is undefined. If no default is given and the environment variable is undefined, the empty string is inserted.

Note that the spaces after the first and before the second pair of curlys are required. `{{ FOO }}` is valid, `{{FOO}}` is invalid.
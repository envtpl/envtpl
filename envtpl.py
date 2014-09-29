'''
envtpl - jinja2 template rendering with shell environment variables
Copyright (C) 2014  Andreas Jansson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys
import re
import argparse
import jinja2

EXTENSION = '.tpl'

def main():
    parser = argparse.ArgumentParser(
        description='jinja2 template rendering with shell environment variables'
    )
    parser.add_argument('input_file', 
                        nargs='?', help='Input filename. Defaults to stdin.'
    )
    parser.add_argument('-o', '--output-file', 
                        help='Output filename. If none is given, and the input file ends '
                        'with "%s", the output filename is the same as the input '
                        'filename, sans the %s extension. Otherwise, defaults to stdout.' %
                        (EXTENSION, EXTENSION)
    )
    parser.add_argument('--allow-missing', action='store_true',
                        help='Allow missing variables. By default, envtpl will die with exit '
                        'code 1 if an environment variable is missing'
    )
    parser.add_argument('--keep-template', action='store_true',
                        help='Keep original template file. By default, envtpl will delete '
                        'the template file'
    )
    args = parser.parse_args()

    variables = os.environ
    try:
        process_file(args.input_file, args.output_file, variables, not args.allow_missing, not args.keep_template)
    except (Fatal, IOError) as e:
        sys.stderr.write('Error: %s\n' % str(e))
        sys.exit(1)

    sys.exit(0)

def process_file(input_filename, output_filename, variables, die_on_missing_variable, remove_template):
    if not input_filename and not remove_template:
        raise Fatal('--keep-template only makes sense if you specify an input file')

    if die_on_missing_variable:
        undefined = jinja2.StrictUndefined
    else:
        undefined = jinja2.Undefined

    if input_filename and not output_filename:
        if not input_filename.endswith(EXTENSION):
            raise Fatal('If no output filename is given, input filename must end in %s' % EXTENSION)
        output_filename = input_filename[:-len(EXTENSION)]
        if not output_filename:
            raise Fatal('Output filename is empty')

    if input_filename:
        with open(input_filename, 'r') as f:
            source = f.read()

        loader = jinja2.FileSystemLoader(os.path.dirname(input_filename))
        env = jinja2.Environment(loader=loader, undefined=undefined)
        relpath = os.path.relpath(input_filename, os.path.dirname(input_filename))

        try:
            template = env.get_template(relpath)
        except jinja2.TemplateSyntaxError as e:
            raise Fatal('Syntax error on line %d: %s' % (e.lineno, e.message))
    else:
        source = sys.stdin.read()

    output = render(source, template, variables, undefined)

    if output_filename and output_filename != '-':
        with open(output_filename, 'w') as f:
            f.write(output)
    else:
        sys.stdout.write(output)

    if input_filename and remove_template:
        os.unlink(input_filename)

def render(source, template, variables, undefined):
    if template is None:
        try:
            template = jinja2.Template(source, undefined=undefined)
        except jinja2.TemplateSyntaxError as e:
            raise Fatal('Syntax error on line %d: %s' % (e.lineno, e.message))

    template.globals['environment'] = get_environment

    try:
        output = template.render(**variables)
    except jinja2.UndefinedError as e:
        raise Fatal(e)

    # jinja2 cuts the last newline
    if source.split('\n')[-1] == '' and output.split('\n')[-1] != '':
        output += '\n'

    return output

@jinja2.contextfunction
def get_environment(context, prefix=''):
    for key, value in sorted(context.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix):], value

class Fatal(Exception):
    pass

if __name__ == '__main__':
    main()

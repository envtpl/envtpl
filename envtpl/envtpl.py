import os
import sys
import re
import argparse

EXTENSION = '.tpl'
REGEX = re.compile(r'\{\{ *(?P<name>[^| ]+)(?: *\| *(?P<default>[^ \}]*))? *\}\}')

def main():
    parser = argparse.ArgumentParser(
        'Replace strings in the format "{{ VARIABLE }}" or "{{ VARIABLE|DEFAULT }}" '
        'with their corresponding environment variables.'
    )
    parser.add_argument('-f', '--input-file', 
                        help='Input filename. Defaults to stdin.'
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

    input_filename = args.input_file
    output_filename = args.output_file
    die_on_missing_variable = not args.allow_missing
    remove_template = not args.keep_template

    if not input_filename and remove_template:
        die('--keep-template only makes sense if you specify an input file')

    if input_filename and not output_filename:
        if not input_filename.endswith(EXTENSION):
            die('If no output filename is given, input filename must end in %s' % EXTENSION)
        output_filename = input_filename[:-len(EXTENSION)]
        if not output_filename:
            die('Output filename is empty')

    if input_filename:
        input_file = open(input_filename, 'r')
    else:
        input_file = sys.stdin
    if output_filename:
        output_file = open(output_filename, 'w')
    else:
        output_file = sys.stdin

    process_file(input_file, output_file, die_on_missing_variable)

    if input_file != sys.stdin:
        input_file.close()
    if output_file != sys.stdout:
        output_file.close()

    if remove_template:
        os.unlink(input_filename)

    sys.exit(0)

def process_file(input_file, output_file, die_on_missing_variable):
    for line in input_file:
        try:
            parsed_line = parse_line(line, os.environ, die_on_missing_variable)
        except MissingVariable, e:
            die(e.message)
        output_file.write(parsed_line)

def parse_line(line, variables, die_on_missing_variable):
    while True:
        match = REGEX.search(line)
        if not match:
            break

        groups = match.groupdict()
        name = groups['name']
        if name in variables:
            value = variables[name]
        else:
            if groups['default']:
                value = groups['default']
            else:
                if die_on_missing_variable:
                    raise MissingVariable(name)
                else:
                    value = ''
        line = line[:match.start()] + value + line[match.end():]

    return line

def die(message):
    sys.stderr.write('%s\n', message)
    sys.exit(1)

class MissingVariable(Exception):
    def __init__(self, name):
        super(MissingVariable, self).__init__('Missing environment variable: %s' % name)

if __name__ == '__main__':
    main()

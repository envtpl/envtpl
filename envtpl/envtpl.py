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

    variables = os.environ
    try:
        process_file(args.input_file, args.output_file, variables, not args.allow_missing, not args.keep_template)
    except (Fatal, IOError), e:
        sys.stderr.write('Error: %s\n' % str(e))
        sys.exit(1)

    sys.exit(0)

def process_file(input_filename, output_filename, variables, die_on_missing_variable, remove_template):
    if not input_filename and not remove_template:
        raise Fatal('--keep-template only makes sense if you specify an input file')

    if input_filename and not output_filename:
        if not input_filename.endswith(EXTENSION):
            raise Fatal('If no output filename is given, input filename must end in %s' % EXTENSION)
        output_filename = input_filename[:-len(EXTENSION)]
        if not output_filename:
            raise Fatal('Output filename is empty')

    if input_filename:
        input_file = open(input_filename, 'r')
    else:
        input_file = sys.stdin
    if output_filename:
        output_file = open(output_filename, 'w')
    else:
        output_file = sys.stdout

    output = ''
    for line in input_file:
        output += parse_line(line, variables, die_on_missing_variable)

    if input_file != sys.stdin:
        input_file.close()

    if output_filename:
        with open(output_filename, 'w') as f:
            f.write(output)
    else:
        sys.stdout.write(output)

    if input_filename and remove_template:
        os.unlink(input_filename)

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
                    raise Fatal('Missing environment variable: %s' % name)
                else:
                    value = ''
        line = line[:match.start()] + value + line[match.end():]

    return line

class Fatal(Exception):
    pass

if __name__ == '__main__':
    main()

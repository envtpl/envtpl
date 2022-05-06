# -*- coding: utf-8 -*-

"""
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
"""

import os
import sys
import argparse
import jinja2
import json
import io


EXTENSION = ".tpl"
IS_PYTHON_2 = sys.version_info < (3, 0)


def main():
    parser = argparse.ArgumentParser(
        description="jinja2 template rendering with shell environment variables"
    )
    parser.add_argument(
        "input_file", nargs="?", help="Input filename. Defaults to stdin."
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="Output filename. If none is given, and the input file ends "
        'with "%s", the output filename is the same as the input '
        "filename, sans the %s extension. Otherwise, defaults to stdout."
        % (EXTENSION, EXTENSION),
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Allow missing variables. By default, envtpl will die with exit "
        "code 1 if an environment variable is missing",
    )
    parser.add_argument(
        "--keep-template",
        action="store_true",
        help="Keep original template file. By default, envtpl will delete "
        "the template file",
    )
    args = parser.parse_args()

    variables = dict([(k, _unicodify(v)) for k, v in os.environ.items()])

    try:
        process_file(
            args.input_file,
            args.output_file,
            variables,
            not args.allow_missing,
            not args.keep_template,
        )
    except (Fatal, IOError) as e:
        sys.stderr.write("Error: %s\n" % str(e))
        sys.exit(1)

    sys.exit(0)


def process_file(
    input_filename, output_filename, variables, die_on_missing_variable, remove_template
):
    if not input_filename and not remove_template:
        raise Fatal("--keep-template only makes sense if you specify an input file")

    if die_on_missing_variable:
        undefined = jinja2.StrictUndefined
    else:
        undefined = jinja2.Undefined

    if input_filename and not output_filename:
        if not input_filename.endswith(EXTENSION):
            raise Fatal(
                "If no output filename is given, "
                "input filename must end in %s" % EXTENSION
            )
        output_filename = input_filename[: -len(EXTENSION)]
        if not output_filename:
            raise Fatal("Output filename is empty")

    if input_filename:
        output = _render_file(input_filename, variables, undefined)
    else:
        output = _render_string(stdin_read(), variables, undefined)

    if output_filename and output_filename != "-":
        with open(output_filename, "wb") as f:
            f.write(output.encode("utf-8"))
    else:
        stdout_write(output)

    if input_filename and remove_template:
        os.unlink(input_filename)


def _render_string(string, variables, undefined):
    template_name = "template_name"
    loader = jinja2.DictLoader({template_name: _unicodify(string)})
    return _render(template_name, loader, variables, undefined)


def _unicodify(s):
    if isinstance(s, str) and IS_PYTHON_2:
        s = unicode(s, "utf-8")  # NOQA
    return s


def stdin_read():
    if IS_PYTHON_2:
        return _unicodify(sys.stdin.read())
    else:
        return io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8").read()


def stdout_write(output):
    if IS_PYTHON_2:
        sys.stdout.write(_unicodify(output))
    else:
        io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8").write(output)


def _render_file(filename, variables, undefined):
    dirname = os.path.dirname(filename)
    loader = jinja2.FileSystemLoader(dirname)
    relpath = os.path.relpath(filename, dirname)
    return _render(relpath, loader, variables, undefined)


def _render(template_name, loader, variables, undefined):
    env = jinja2.Environment(loader=loader, undefined=undefined)
    env.filters["from_json"] = from_json

    template = env.get_template(template_name)
    template.globals["environment"] = get_environment

    try:
        output = template.render(**variables)
    except jinja2.UndefinedError as e:
        raise Fatal(e)

    # jinja2 cuts the last newline
    source, _, _ = loader.get_source(env, template_name)
    if source.split("\n")[-1] == "" and output.split("\n")[-1] != "":
        output += "\n"

    return output


@jinja2.pass_context
def get_environment(context, prefix=""):
    for key, value in sorted(context.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix) :], value


@jinja2.pass_eval_context
def from_json(eval_ctx, value):
    return json.loads(value)


class Fatal(Exception):
    pass


if __name__ == "__main__":
    main()

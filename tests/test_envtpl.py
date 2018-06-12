# -*- coding: utf-8 -*-

import sh
import tempfile
import six
import os
import jinja2
import envtpl
if six.PY3:
    import unittest
else:
    import unittest2 as unittest


class TestRender(unittest.TestCase):

    def test_empty(self):
        self.assertEquals(envtpl._render_string('', {}, jinja2.StrictUndefined, '{{,}}'), '')

    def test_die_on_missing(self):
        self.assertRaises(envtpl.Fatal, envtpl._render_string, '{{ FOO }}', {},
                          jinja2.StrictUndefined, '{{,}}')

    def test_dont_die_on_missing(self):
        self.assertEquals(envtpl._render_string('{{ FOO }}', {}, jinja2.Undefined, '{{,}}'), '')

    def test_defaults(self):
        self.assertEquals(envtpl._render_string('{{ FOO | default("abc") }}', {},
                          jinja2.StrictUndefined, '{{,}}'), 'abc')
        self.assertEquals(envtpl._render_string('{{ FOO | default("abc") }}', {'FOO': 'def'},
                          jinja2.StrictUndefined, '{{,}}'), 'def')

    def test_quoted(self):
        string = '''
foo = {{ FOO | default(123) }}
bar = "{{ BAR | default("abc") }}"
'''
        expected = '''
foo = 456
bar = "abc"
'''
        self.assertEquals(envtpl._render_string(string, {'FOO': 456},
                          jinja2.StrictUndefined, '{{,}}'), expected)

    def test_if_block(self):
        string = '''
{% if BAZ is defined %}
foo = 123
{% else %}
foo = 456
{% endif %}
bar = "abc"'''
        expected = '''

foo = 456

bar = "abc"'''
        self.assertEquals(envtpl._render_string(string, {}, jinja2.StrictUndefined,
                          '{{,}}'), expected)

    def test_environment(self):
        string = '''
{% for key, value in environment() %}{{ key }} = {{ value }}
{% endfor %}
'''
        expected = '''
baz = qux
foo = bar
'''
        self.assertEquals(envtpl._render_string(string, {'foo': 'bar', 'baz': 'qux'},
                          jinja2.StrictUndefined, '{{,}}'), expected)

    def test_environment_prefix(self):
        string = '''
{% for key, value in environment('X_') %}{{ key }} = {{ value }}
{% endfor %}
'''
        expected = '''
foo = bar
'''
        self.assertEquals(envtpl._render_string(string, {'X_foo': 'bar', 'baz': 'X_qux'},
                          jinja2.StrictUndefined, '{{,}}'), expected)

    def test_from_json_list(self):
        string = '''
{% for foo in FOOS_JSON | from_json %}{{ foo.bar }}
{% endfor %}
'''
        expected = '''
hello
world
'''
        foos_json = '[{"bar": "hello"}, {"bar": "world"}]'
        self.assertEquals(envtpl._render_string(string, {'FOOS_JSON': foos_json},
                                                jinja2.StrictUndefined, '{{,}}'), expected)

    def test_from_json_object(self):
        string = '''
{{ (FOO | from_json).bar }}
'''
        expected = '''
baz
'''
        self.assertEquals(envtpl._render_string(string, {'FOO': '{"bar": "baz"}'},
                                                jinja2.StrictUndefined, '{{,}}'), expected)

    def test_unicode_output(self):
        string = '''
åäö
'''
        expected = u'''
åäö
'''
        self.assertEquals(envtpl._render_string(string, {}, jinja2.StrictUndefined,
                          '{{,}}'), expected)

    def test_unicode_input(self):
        string = u'''
åäö
'''
        expected = u'''
åäö
'''
        self.assertEquals(envtpl._render_string(string, {}, jinja2.StrictUndefined,
                          '{{,}}'), expected)

    def test_custom_var_delimiter(self):
        string = '{{ FOO }} %% BAR %%'
        expected = '{{ FOO }} baz'

        self.assertEquals(envtpl._render_string(string, {'BAR': 'baz'}, jinja2.StrictUndefined,
                          '%%'), expected)

    def test_custom_var_delimiters(self):
        string = '{{ FOO }} [[ BAR ]]'
        expected = '{{ FOO }} baz'

        self.assertEquals(envtpl._render_string(string, {'BAR': 'baz'}, jinja2.StrictUndefined,
                          '[[,]]'), expected)


class TestFiles(unittest.TestCase):

    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.scratch_dir = os.path.join(self.cwd, 'scratch')
        if not os.path.exists(self.scratch_dir):
            os.mkdir(self.scratch_dir)

    def tearDown(self):
        for filename in os.listdir(self.scratch_dir):
            os.unlink(os.path.join(self.scratch_dir, filename))
        os.rmdir(self.scratch_dir)

    def test_bad_missing_output_filename(self):
        self.assertRaises(envtpl.Fatal, envtpl.process_file, 'foo.bar', None, {},
                          jinja2.Undefined, True, '{{,}}')
        self.assertRaises(envtpl.Fatal, envtpl.process_file, '.tpl', None, {},
                          jinja2.Undefined, True, '{{,}}')

    def test_delete(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write('''abc {{ FOO }} 123
frogs will be frogs
{{    BAR | default("456")}}''')

        expected = '''abc  123
frogs will be frogs
456'''
        envtpl.process_file(tpl_filename, None, {}, False, True, '{{,}}')
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), expected)

        self.assertFalse(os.path.exists(tpl_filename))

    def test_environment_vars(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write('''abc {{ FOO }} 123
frogs will be frogs
{{    BAR|default("456")}}''')

        expected = '''abc --- 123
frogs will be frogs
+++'''
        envtpl.process_file(tpl_filename, None, {'FOO': '---', 'BAR': '+++'}, False, True, '{{,}}')
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), expected)

    def test_include(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        incl_filename = filename + "-incl.tpl"
        tpl_filename = filename + '.tpl'

        with open(incl_filename, 'w') as f:
            f.write('''{{ INCLUDE|default('incl') }}''')

        with open(tpl_filename, 'w') as f:
            f.write('''abc {{ FOO }} 123 {% include 'file1-incl.tpl' %}
frogs will be frogs
{{    BAR|default("456")}}''')

        expected = '''abc --- 123 incl
frogs will be frogs
+++'''
        envtpl.process_file(tpl_filename, None, {'FOO': '---', 'BAR': '+++'}, False, True, '{{,}}')
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), expected)

    def test_no_delete(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write('foo')

        envtpl.process_file(tpl_filename, None, {'FOO': '---', 'BAR': '+++'}, False, False, '{{,}}')
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), 'foo')

        self.assertTrue(os.path.exists(tpl_filename))

    def test_die_on_missing(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write('{{ FOO }}')

        self.assertRaises(envtpl.Fatal, envtpl.process_file, tpl_filename, None, {}, True, False,
                          '{{,}}')

    def test_different_output_name(self):
        tpl_filename = os.path.join(self.scratch_dir, 'file1.tpl')
        output_filename = os.path.join(self.scratch_dir, 'file2')

        with open(tpl_filename, 'w') as f:
            f.write('foo')

        envtpl.process_file(tpl_filename, output_filename, {}, False, True, '{{,}}')
        with open(output_filename, 'r') as f:
            self.assertEquals(f.read(), 'foo')

        self.assertFalse(os.path.exists(tpl_filename))


class TestSubprocess(unittest.TestCase):

    def setUp(self):
        self.cleanup_filenames = []
        self.tempdir = tempfile.gettempdir()

    def tearDown(self):
        for filename in self.cleanup_filenames:
            if os.path.exists(filename):
                os.unlink(filename)

    def tempfile(self, name):
        filename = os.path.join(self.tempdir, name)
        self.cleanup_filenames.append(filename)
        return filename

    def envtpl(self):
        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, '..', 'envtpl.py')

    def test_files(self):
        tpl_filename = self.tempfile('test.txt.tpl')
        txt_filename = self.tempfile('test.txt')
        with open(tpl_filename, 'wt') as f:
            f.write('hello {{FOO}}')

        sh.python(
            self.envtpl(), tpl_filename,
            _env={'FOO': 'world'},
        )

        self.assertFalse(os.path.exists(tpl_filename))
        self.assertTrue(os.path.exists(txt_filename))
        with open(txt_filename, 'r') as f:
            self.assertEquals('hello world', f.read())

    def test_stdin(self):
        out = sh.python(
            self.envtpl(),
            _env={'FOO': 'world'},
            _in='hello {{FOO}}',
        )

        self.assertEquals('hello world', out)

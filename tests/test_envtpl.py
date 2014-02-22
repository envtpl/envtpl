import unittest2 as unittest

import os
import envtpl

class TestRender(unittest.TestCase):

    def test_empty(self):
        self.assertEquals(envtpl.render('', {}, True), '')

    def test_die_on_missing(self):
        self.assertRaises(envtpl.Fatal, envtpl.render, '{{ FOO }}', {}, True)

    def test_dont_die_on_missing(self):
        self.assertEquals(envtpl.render('{{ FOO }}', {}, False), '')

    def test_defaults(self):
        self.assertEquals(envtpl.render('{{ FOO | default("abc") }}', {}, True), 'abc')
        self.assertEquals(envtpl.render('{{ FOO | default("abc") }}', {'FOO': 'def'}, True), 'def')

    def test_quoted(self):
        source = '''
foo = {{ FOO | default(123) }}
bar = "{{ BAR | default("abc") }}"'''
        expected = '''
foo = 456
bar = "abc"'''
        self.assertEquals(envtpl.render(source, {'FOO': 456}, True), expected)

    def test_if_block(self):
        source = '''
{% if BAZ is defined %}
foo = 123
{% else %}
foo = 456
{% endif %}
bar = "abc"'''
        expected = '''

foo = 456

bar = "abc"'''
        self.assertEquals(envtpl.render(source, {}, True), expected)
        

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
        self.assertRaises(envtpl.Fatal, envtpl.process_file, 'foo.bar', None, {}, False, True)
        self.assertRaises(envtpl.Fatal, envtpl.process_file, '.tpl', None, {}, False, True)

    def test_delete(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write(
'''abc {{ FOO }} 123
frogs will be frogs
{{    BAR | default("456")}}'''
            )

        expected = '''abc  123
frogs will be frogs
456'''
        envtpl.process_file(tpl_filename, None, {}, False, True)
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), expected)

        self.assertFalse(os.path.exists(tpl_filename))

    def test_environment_vars(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write(
'''abc {{ FOO }} 123
frogs will be frogs
{{    BAR|default("456")}}'''
            )

        expected = '''abc --- 123
frogs will be frogs
+++'''
        envtpl.process_file(tpl_filename, None, {'FOO': '---', 'BAR': '+++'}, False, True)
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), expected)

    def test_no_delete(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write('foo')

        envtpl.process_file(tpl_filename, None, {'FOO': '---', 'BAR': '+++'}, False, False)
        with open(filename, 'r') as f:
            self.assertEquals(f.read(), 'foo')

        self.assertTrue(os.path.exists(tpl_filename))

    def test_die_on_missing(self):
        filename = os.path.join(self.scratch_dir, 'file1')
        tpl_filename = filename + '.tpl'

        with open(tpl_filename, 'w') as f:
            f.write('{{ FOO }}')

        self.assertRaises(envtpl.Fatal, envtpl.process_file, tpl_filename, None, {}, True, False)

    def test_different_output_name(self):
        tpl_filename = os.path.join(self.scratch_dir, 'file1.tpl')
        output_filename = os.path.join(self.scratch_dir, 'file2')

        with open(tpl_filename, 'w') as f:
            f.write('foo')

        envtpl.process_file(tpl_filename, output_filename, {}, False, True)
        with open(output_filename, 'r') as f:
            self.assertEquals(f.read(), 'foo')

        self.assertFalse(os.path.exists(tpl_filename))

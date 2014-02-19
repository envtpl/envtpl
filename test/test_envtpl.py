import unittest2 as unittest

import os
import envtpl

class TestParseLine(unittest.TestCase):

    def test_empty(self):
        line = ''
        parsed = envtpl.parse_line(line, {}, False)
        self.assertEquals(parsed, line)

    def test_no_vars(self):
        line = 'foo bar'
        parsed = envtpl.parse_line(line, {}, False)
        self.assertEquals(parsed, line)

    def test_missing_no_default(self):
        line = '{{ FOO }}'
        parsed = envtpl.parse_line(line, {}, False)
        self.assertEquals(parsed, '')
        
    def test_missing_default(self):
        line = '{{ FOO|foo }}'
        parsed = envtpl.parse_line(line, {}, False)
        self.assertEquals(parsed, 'foo')

    def test_missing_context(self):
        line = 'abc {{ FOO }} def'
        parsed = envtpl.parse_line(line, {}, False)
        self.assertEquals(parsed, 'abc  def')
        
    def test_missing_die(self):
        line = '{{ FOO }}'
        self.assertRaises(envtpl.Fatal, envtpl.parse_line, line, {}, True)

    def test_only_var(self):
        line = '{{ FOO }}'
        parsed = envtpl.parse_line(line, {'FOO': 'foo'}, False)
        self.assertEquals(parsed, 'foo')

    def test_context(self):
        line = 'abc {{ FOO }} def'
        parsed = envtpl.parse_line(line, {'FOO': 'foo'}, False)
        self.assertEquals(parsed, 'abc foo def')

    def test_multiple(self):
        line = '{{ FOO }} {{ BAR }}'
        parsed = envtpl.parse_line(line, {'FOO': 'foo', 'BAR': 'bar'}, False)
        self.assertEquals(parsed, 'foo bar')

    def test_multiple_context(self):
        line = 'abc {{ FOO }} def {{ BAR }} ghi'
        parsed = envtpl.parse_line(line, {'FOO': 'foo', 'BAR': 'bar'}, False)
        self.assertEquals(parsed, 'abc foo def bar ghi')

    def test_no_spaces(self):
        line = 'abc{{FOO|foo}}{{BAR}}def'
        parsed = envtpl.parse_line(line, {'BAR': 'bar'}, False)
        self.assertEquals(parsed, 'abcfoobardef')

    def test_many_spaces(self):
        line = 'abc  {{  FOO  |  foo  }}  {{  BAR  }}  def'
        parsed = envtpl.parse_line(line, {'BAR': 'bar'}, False)
        self.assertEquals(parsed, 'abc  foo  bar  def')

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
{{    BAR|456}}
'''
            )

        expected = '''abc  123
frogs will be frogs
456
'''
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
{{    BAR|456}}
'''
            )

        expected = '''abc --- 123
frogs will be frogs
+++
'''
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

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
        self.assertRaises(envtpl.MissingVariable, envtpl.parse_line, line, {}, True)

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

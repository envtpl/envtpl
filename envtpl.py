#!/usr/bin/env python

import os
import sys
import re

def main():
    regex = re.compile('\{\{ (?P<name>[^|]+)(?:\|(?P<default>.*))? \}\}')

    output = ''
    for line in sys.stdin:
        match = regex.search(line)
        if match:
            groups = match.groupdict()
            name = groups['name']
            default = groups['default']
            value = os.environ.get(name, default) or ''
            line = regex.sub(value, line)
        sys.stdout.write(line)

if __name__ == '__main__':
    main()

#!/usr/bin/python

import re

test_str = ''

m = re.match(r'.+?(\d{2}\:\d{2}\:\d{2})', test_str)

if m:
    print m
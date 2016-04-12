#-*- coding: utf-8 -*-
import re
import codecs

if re.search(u'([цкнгшщзхфвпсрлджчмтб])о&', u'коло&'):
    print u'search'

st = set([1, 3, 9, 9])
print st

print u'коло'[:-0]

a = [u'hh' for i in xrange(3)]
print a
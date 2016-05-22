#-*- coding: utf-8 -*-

import codecs
import json
import random

t = codecs.open(u'poliakov_added_5.json', u'r', u'utf-8')
tf = json.load(t)

chosen_ones = []
i = 0
while i < 100:
    r_i = random.choice(tf)
    if u'scores' not in r_i:
        continue
    if r_i[u'pos'] != u'N':
        continue
    for par in r_i[u'scores']:
        if r_i[u'scores'][par] >= 0.5:
            i += 1
            print i
            chosen_ones.append(r_i)

ss = codecs.open(u'100nouns0.5-1.json', u'w', u'utf-8')
json.dump(chosen_ones, ss, ensure_ascii=False, indent=2)
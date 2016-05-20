#-*- coding: utf-8 -*-
import re
import codecs
import json
from noun_class import letterchange
import noun_class


class uni_parser_word():
    def __init__(self):
        self.lemma = u''
        self.simple_lemma = u''
        self.paradigm = u''
        self.stems = []
        self.translation = u''
        self.gram = u''
        self.examples = []


def files_open(name_uni_parser, name_original):
    up = codecs.open(name_uni_parser, u'r', u'utf-8')
    upt = up.read()
    orig = codecs.open(name_original, u'r', u'utf-8')
    or_dict = {}
    for line in orig:
        line = line.rstrip()
        line = re.sub(u'<em>.+</em>', u'', line)
        if re.search(u'<p>(.+?)</a>.+?</a> (.+)</a> </p>', line):
            s = re.search(u'<p>(.+?)</a>.+?</a> (.+)</a> </p>', line)
            lemma = s.group(1)
            examples = s.group(2)
        elif re.search(u'<p>(.+?)</a>.+?</i>  .+?</a> </p>', line):
            s = re.search(u'<p>(.+?)</a>.+?</i>  (.+?)</a> </p>', line)
            lemma = s.group(1)
            examples = s.group(2)
        else:
            print line, u'no groups'
        or_dict[letterchange(lemma)] = examples.split(u'</a> , ')
    up_array = []
    up_arr = upt.split(u'-lexeme\r\n')
    for word in up_arr:
        word_content = word.split(u'\r\n')
        new_word = uni_parser_word()
        i = 1
        for item in word_content:
            if i == 1:
                new_word.lemma = item[6:]
                new_word.simple_lemma = letterchange(new_word.lemma)
                try:
                    new_word.examples = or_dict[new_word.simple_lemma]
                except KeyError:
                    try:
                        new_word.examples = or_dict[new_word.simple_lemma + u'ся']
                        new_word.lemma = new_word.lemma + u'ся'
                        new_word.simple_lemma = new_word.simple_lemma + u'ся'
                    except:
                        print u'no examples for the word', new_word.lemma
                        new_word.examples = u'delete_this_word'
                        continue
            elif i == 2:
                new_word.stems = item[7:]
            elif i == 3:
                new_word.gram = item[8:]
            elif i == 4:
                new_word.paradigm = item[11:]
            elif i == 5:
                new_word.translation = item[12:]
            elif i == 6:
                pass
            else:
                print u'i_error', word, i, item
            i += 1
        if u'persn' in new_word.gram or u'N-PRO' in new_word.gram or u'delete' in new_word.examples:
            continue
        up_array.append(new_word)
    return up_array

name_up = u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser\dictionary_1805_norm_pos.txt'
name_or = u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser\All_dict_polyakov.txt'
up_array = files_open(name_up, name_or)

for word in up_array:
    pass


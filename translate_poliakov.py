#-*- coding: utf-8 -*-
import re
import codecs
import json
from noun_class import letterchange
import noun_class
from levestein import levenshtein


class uni_parser_word():
    def __init__(self):
        self.lemma = u''
        self.simple_lemma = u''
        self.paradigm = u''
        self.stems = []
        self.translation = u''
        self.gram = u''
        self.examples = []
        self.pos = u''
        self.gender = u'-'


def files_open(name_uni_parser, name_original):
    up = codecs.open(name_uni_parser, u'r', u'utf-8')
    upt = up.read()
    orig = codecs.open(name_original, u'r', u'utf-8')
    or_dict = {}
    up_dict = {}
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
                    except KeyError:
                        # print u'no examples for the word', new_word.lemma
                        new_word.examples = u'delete_this_word'
                        continue
            elif i == 2:
                new_word.stems = item[7:]
            elif i == 3:
                new_word.gram = item[8:]
                if u'ADV' in new_word.gram:
                    new_word.pos = u'adverb'
                elif u'PART' in new_word.gram or u'CONJ' in new_word.gram:
                    new_word.pos = u'conjunction'
                elif u'N' in new_word.gram:
                    new_word.pos = u'N'
                    if u'f' in new_word.gram:
                        new_word.gender = u'f'
                    elif u',m' in new_word.gram:
                        new_word.gender = u'm'
                    elif u',n' in new_word.gram:
                        new_word.gender = u'n'
                    else:
                        new_word.gender = u'm'
                elif u'V' in new_word.gram:
                    new_word.pos = u'V'
                elif u'A' in new_word.gram or u'А' in new_word.gram:
                    new_word.pos = u'Adj'
                elif u'PREP' in new_word.gram:
                    new_word.pos = u'preposition'
            elif i == 4:
                new_word.paradigm = item[11:]
            elif i == 5:
                new_word.translation = item[12:]
            elif i == 6:
                pass
            else:
                print u'i_error', word, i, item
            i += 1
        if u'persn' in new_word.gram or u'N-PRO' in new_word.gram or u'delete' in new_word.examples or u'NUM' in new_word.gram:
            continue
        if new_word.pos == u'':
            print u'no part of speeach for ', new_word.lemma, new_word.gram
        if new_word.simple_lemma in up_dict:
            up_dict[new_word.simple_lemma].append(new_word)
        else:
            up_dict[new_word.simple_lemma] = [new_word]
        # up_array.append(new_word)
    return up_dict


def add_torot_to_up(name_torot, up_dict):
    t = codecs.open(name_torot, u'r', u'utf-8')
    tf = json.load(t)
    i = 0
    for word in tf:
        i += 1
        if word[u'lemma_new'] in up_dict:
            word[u'up_lemma'] = word[u'lemma_new']
            word[u'up_lemma_cs'] = up_dict[word[u'lemma_new']][0].lemma
            word[u'up_examples'] = up_dict[word[u'lemma_new']][0].examples
            word[u'up_gramm'] = up_dict[word[u'lemma_new']][0].gram
            word[u'up_translation'] = up_dict[word[u'lemma_new']][0].translation
            word[u'up_stems'] = {}
            for dict_entity in up_dict[word[u'lemma_new']]:
                word[u'up_stems'][dict_entity.paradigm] = dict_entity.stems
        else:
            if word[u'pos'] == u'N':
                distance, array = use_leven(word[u'lemma_new'], up_dict, word[u'pos'], word['gender'])
            else:
                distance, array = use_leven(word[u'lemma_new'], up_dict, word[u'pos'])
            if distance == u'no':
                lr.write(u'no correspondence to ' + word[u'lemma_new'] + u'\r\n')
            else:
                array_text = u''
                for lemma in array:
                    array_text += lemma + u', '
                array_text = array_text[:-2]
                tr.write(u'from ' + word[u'lemma_new'] + u'\t to \t' + array_text + u'\t distance == ' + str(distance) + u'\r\n')
        print i, u'done'
        if i == 100:
            break


def use_leven(word, up_dict, word_pos, gender=u'-'):
    l1 = []
    l2 = []
    for lemma in up_dict:
        if word_pos == up_dict[lemma][0].pos and gender == up_dict[lemma][0].gender:  # а если омонимия на ур. лемм?
            l = levenshtein(word.replace(u'ѣ', u'е'), lemma.replace(u'ѣ', u'е'))
            if l == 1:
                l1.append(lemma)
            elif l == 2 and l1 == []:
                l2.append(lemma)
    if l1 != []:
        if len(l1) > 1:
            l1 = chose_the_best(l1, word)
        return 1, l1
    elif l2 != []:
        if len(l2) > 1:
            l2 = chose_the_best(l2, word)
        return 2, l2
    else:
        return u'no', u'no'


def chose_the_best(array, word):
    full_fall0 = []
    full_fall1 = []
    word_ff = word.replace(u'о', u'').replace(u'е', u'').replace(u'ь', u'').replace(u'ъ', u'').replace(u'й', u'и')
    for w in array:
        w_ff = w.replace(u'о', u'').replace(u'е', u'').replace(u'ь', u'').replace(u'ъ', u'').replace(u'й', u'и')
        if w_ff == word_ff:
            full_fall0.append(w)
        elif levenshtein(w_ff, word_ff) == 1 and full_fall0 == []:
            full_fall1.append(w)
    if full_fall0 != []:
        return full_fall0
    elif full_fall1 != []:
        return simplify_array(word, full_fall1)
    else:
        return array


def simplify_array(word, full_fall0):
    if len(full_fall0) == 1:
        return full_fall0
    else:
        complete_fall0 = []
        complete_fall1 = []
        word_cf = re.sub(u'[уъыаоэяиюое]', u'', word)
        for w in full_fall0:
            w_cf = re.sub(u'[уъыаоэяиюое]', u'', w)
            if w_cf == word_cf:
                complete_fall0.append(w)
            elif levenshtein(w_cf, word_cf) == 1 and complete_fall0 == []:
                complete_fall1.append(w)
        if complete_fall0 != []:
            return complete_fall0
        elif complete_fall1 != []:
            return complete_fall1
        else:
            print u'is it possible???', word


lr = codecs.open(u'no_correspondence_2.txt', u'w', u'utf-8')
tr = codecs.open(u'have_correspondence_2.txt', u'w', u'utf-8')
name_up = u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser\dictionary_1805_norm_pos.txt'
name_or = u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser\All_dict_polyakov.txt'
up_array = files_open(name_up, name_or)
print len(up_array)
add_torot_to_up(u'torot_gram_4.json', up_array)
# for word in up_array:
#     print word.lemma, word.simple_lemma, word.paradigm, word.stems, word.translation, word.gram, word.examples[0]


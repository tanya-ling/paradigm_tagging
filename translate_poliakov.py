#-*- coding: utf-8 -*-
import re
import codecs
import json
from noun_class import letterchange
from levestein import levenshtein
import time


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
                new_word.stems = work_with_stems(item[7:])
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
    i = -1
    added = {}  # словарь слов из up (лемма : [distance, index]), которые были присоединены к торот
    for word in tf:
        i += 1
        # if i <= 6060:
        #     continue
        if word[u'lemma_new'] in up_dict:
            word, added = add_group_of_words(word, up_dict, added, word[u'lemma_new'], i, tf)
        else:
            if word[u'pos'] == u'N':
                distance, array = use_leven(word[u'lemma_new'], up_dict, word[u'pos'], word['gender'])
            else:
                distance, array = use_leven(word[u'lemma_new'], up_dict, word[u'pos'])
            if array == u'no':
                lr.write(u'no correspondence to ' + word[u'lemma_new'] + u'\r\n')
            else:
                if len(array) > 1:
                    array_text = u''
                    for lemma in array:
                        array_text += lemma + u', '
                    array_text = array_text[:-2]
                    tr.write(u'CANNOT chose from ' + word[u'lemma_new'] + u'\t to \t' + array_text + u'\t distance == ' + str(distance) + u'\r\n')
                else:
                    word, added = add_group_of_words(word, up_dict, added, array[0], i, tf, distance)
                    oc.write(u'from ' + word[u'lemma_new'] + u'\t to \t' + array[0] + u'\t distance == ' + str(distance) + u'\r\n')
        print i, u'done'
        # if i == 100:
        #     # json.dump(tf, pt, ensure_ascii=False, indent=2)
        #     break
    return tf, added


def work_with_stems(stems):
    if stems[-1] == u'.':
        stems = stems[:-1]
    stems_arr = stems.split(u'.|')
    g_stems = []
    for stem_group in stems_arr:
        stem_gr = list(set(stem_group.split(u'.//')))
        g_stems.append(stem_gr)
    return g_stems


def add_rest(tf, added, up):
    max_index = int(tf[-1]['id'])
    print max_index
    for sl in up:
        if sl not in added:
            word = {}
            word[u'up_lemma'] = up[sl][0].simple_lemma
            word[u'up_lemma_cs'] = up[sl][0].lemma
            word[u'up_examples'] = up[sl][0].examples
            word[u'up_gramm'] = up[sl][0].gram
            word[u'up_translation'] = up[sl][0].translation
            word[u'up_stems'] = {}
            for par in up[sl]:
                word[u'up_stems'][par.paradigm] = par.stems
            word[u'index'] = max_index + 1
            max_index += 1
            tf.append(word)
    return tf


def add_group_of_words(word, up_dict, added, up_sl, j, tf, distance=0):
    if up_sl in added:
        if added[up_sl][0][0] < distance:
            print u'we will not add', up_sl, 'to', word[u'lemma_new'], u', because the better correspondence exists:', tf[added[up_sl][0][1]][u'lemma_new']
            return word, added  # не добавляем, если это слово мы уже добавили к какому-то, у когорого меньше distance
        elif added[up_sl][0][0] > distance:
            print u'we will delete', up_sl, 'to', tf[added[up_sl][0][1]][u'lemma_new'], u', because the better correspondence exists:', \
            word[u'lemma_new']
            for index_group in added[up_sl]:
                index = index_group[1]
                del tf[index][u'up_lemma']
                del tf[index][u'up_lemma_cs']
                del tf[index][u'up_examples']
                del tf[index][u'up_gramm']
                del tf[index][u'up_translation']
                del tf[index][u'distance_to_up']
                del tf[index][u'up_stems']
                added[up_sl] = [[distance, j]]
            # нужно найти источник, там было добавлено неправильно
        else:  # если равно, то нужно хранить несколько
            added[up_sl].append([distance, j])
            print u'we will add', up_sl, 'to', word[u'lemma_new'], u', but the other correspondence also exists:', tf[added[up_sl][0][1]][
                u'lemma_new']

    else:
        added[up_sl] = [[distance, j]]
    word[u'up_lemma'] = up_sl
    word[u'up_lemma_cs'] = up_dict[up_sl][0].lemma
    word[u'up_examples'] = up_dict[up_sl][0].examples
    word[u'up_gramm'] = up_dict[up_sl][0].gram
    word[u'up_translation'] = up_dict[up_sl][0].translation
    word[u'distance_to_up'] = distance
    word[u'up_stems'] = {}
    for dict_entity in up_dict[up_sl]:
        word[u'up_stems'][dict_entity.paradigm] = dict_entity.stems
    return word, added


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
        word_cf = re.sub(u'[уъыаоэяиюье]', u'', word)
        for w in full_fall0:
            w_cf = re.sub(u'[уъыаоэяиюье]', u'', w)
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
            for i in full_fall0:
                print i
            return u'no'

lr = codecs.open(u'no_correspondence_6.txt', u'w', u'utf-8')
tr = codecs.open(u'have_several_corr_6.txt', u'w', u'utf-8')
oc = codecs.open(u'have_one_corr_6.txt', u'w', u'utf-8')
pt = codecs.open(u'poliakov_added_6.json', u'w', u'utf-8')
name_up = u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser\dictionary_1805_norm_pos.txt'
name_or = u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser\All_dict_polyakov.txt'
up_array = files_open(name_up, name_or)
print len(up_array)
t1 = time.clock()
tf, added = add_torot_to_up(u'torot_gram_6.json', up_array)
t2 = time.clock()
print str(t2-t1), 'seconds for searching correspondencies'
tf = add_rest(tf, added, up_array)
# for word in up_array:
#     print word.lemma, word.simple_lemma, word.paradigm, word.stems, word.translation, word.gram, word.examples[0]
json.dump(tf, pt, ensure_ascii=False, indent=2)
t3 = time.clock()
print str(t3-t2), 'seconds for writing correspondencies'
pt.close()


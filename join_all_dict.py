#-*- coding: utf-8 -*-

import re
import codecs
import json
from noun_class import letterchange
from levestein import levenshtein
import time


def files_open():
    t = codecs.open(u'torot_gram_7.json', u'r', u'utf-8')
    tf = json.load(t)
    n = codecs.open(u'rnc_gram_2.json', u'r', u'utf-8')
    nf = json.load(n)
    td = {}
    for word in tf:
        if word['lemma_new'] not in td:
            td[word['lemma_new']] = [word]
        else:
            td[word['lemma_new']].append(word)
        # if len(td) == 500:
        #     break
    nd = {}
    for word in nf:
        if word['lemma_new'] not in nd:
            nd[word['lemma_new']] = word
        else:
            print u'леммы повторяются в нкря, что подозрительно', word['lemma_new']
            nd[word['lemma_new']] = word
        if len(nd) == 500:
            break
    return td, nf
    return td, nd


# !!!!!!!!!!!!!!!


def add_torot_to_up(td, nd):
    i = -1
    added = {}  # словарь слов из up (лемма : [distance, index]), которые были присоединены к торот
    lennd = len(nd)
    for word in nd:
        i += 1
        # if i <= 6060:
        #     continue
        # print slovo
        # word = nd[slovo]
        # print word
        if word[u'lemma_new'] in td:
            word, added = add_group_of_words(word, td, added, word[u'lemma_new'], i, nd)
        else:
            if word[u'pos'] == u'N':
                distance, array = use_leven(word[u'lemma_new'], td, word[u'pos'], word['gender'])
            else:
                distance, array = use_leven(word[u'lemma_new'], td, word[u'pos'])
            if array == u'no':
                nc.write(u'no correspondence to ' + word[u'lemma_new'] + u'\r\n')
            else:
                if len(array) > 1:
                    array_text = u''
                    for lemma in array:
                        array_text += lemma + u', '
                    array_text = array_text[:-2]
                    sc.write(u'CANNOT chose from ' + word[u'lemma_new'] + u'\t to \t' + array_text + u'\t distance == ' + str(distance) + u'\r\n')
                else:
                    word, added = add_group_of_words(word, td, added, array[0], i, nd, distance)
                    oc.write(u'from ' + word[u'lemma_new'] + u'\t to \t' + array[0] + u'\t distance == ' + str(distance) + u'\r\n')
        if i % 100 == 0:
            print float(i)/lennd, u'done'
        # if i == 100:
        #     # json.dump(tf, pt, ensure_ascii=False, indent=2)
        #     break
    return nd, added



def add_rest(tf, added, nd):  # dict, add, arr of obj
    max_index = int(nd[-1]['id'])
    print max_index
    for key_lemma in tf:
        # print key_lemma
        if key_lemma not in added:
            word = {}
            word[u'lemma'] = key_lemma
            word[u'lemma_new'] = tf[key_lemma][0]['lemma_new']
            word[u'pos'] = tf[key_lemma][0]['pos']
            word[u'torot_id'] = tf[key_lemma][0]['torot_id']
            if tf[key_lemma][0][u'pos'] == u'N':
                word[u'tor_gender'] = tf[key_lemma][0]['gender']
            word[u'tor_examples'] = {}
            word[u'tor_unanalysed_examples'] = {}
            word[u'tor_predicted_stems'] = {}
            word[u'tor_scores'] = {}
            word[u'tor_par_stem'] = {}
            for dict_entity in tf[key_lemma]:
                    word[u'tor_unanalysed_examples'] = my_undate(word['tor_unanalysed_examples'],
                                                             dict_entity['unanalysed_examples'])
                    try:
                        word[u'tor_examples'] = my_undate(word['tor_examples'], dict_entity['examples'])
                        word[u'tor_predicted_stems'] = my_undate(word['tor_predicted_stems'],
                                                                 dict_entity['predicted_stems'])
                        word[u'tor_scores'] = my_undate(word['tor_scores'], dict_entity['scores'])
                        word[u'tor_par_stem'] = my_undate(word['tor_par_stem'], dict_entity['par_stem'])
                    except KeyError:
                        # print u'but there were no tor pr stems!', word['lemma'], dict_entity['lemma']
                        pass  # это штуки, у которых не тпределился тип
                    except AttributeError:
                        print u'we have attr problems, got list instead of dict', word['lemma']
            word[u'id'] = max_index + 1
            max_index += 1
            nd.append(word)
    return nd


def add_group_of_words(word, nd, added, up_sl, j, td, distance=0):
    if up_sl in added:
        if added[up_sl][0][0] < distance:
            # print u'we will not add', up_sl, 'to', word[u'lemma_new'], u', because the better correspondence exists:', td[added[up_sl][0][1]][u'lemma_new']
            return word, added  # не добавляем, если это слово мы уже добавили к какому-то, у когорого меньше distance
        elif added[up_sl][0][0] > distance:
            print u'we will delete', up_sl, 'to', td[added[up_sl][0][1]][u'lemma_new'], u', because the better correspondence exists:', \
            word[u'lemma_new']
            for index_group in added[up_sl]:
                index = index_group[1]
                del td[index][u'tor_lemma']
                del td[index][u'tor_lemma_new']
                del td[index][u'tor_examples']
                del td[index][u'tor_unanalysed_examples']
                del td[index][u'distance_to_tor']
                del td[index][u'tor_predicted_stems']
                del td[index][u'tor_scores']
                del td[index][u'tor_par_stem']
                if u'tor_gender' in td[index]:
                    del td[index][u'tor_gender']
                added[up_sl] = [[distance, j]]
            # нужно найти источник, там было добавлено неправильно
        else:  # если равно, то нужно хранить несколько
            added[up_sl].append([distance, j])
            print u'we will add', up_sl, 'to', word[u'lemma_new'], u', but the other correspondence also exists:', td[added[up_sl][0][1]][
                u'lemma_new']
    else:
        added[up_sl] = [[distance, j]]
        # print u'addedd index', j, u'with distance', distance, up_sl
    word[u'tor_lemma'] = up_sl
    word[u'tor_lemma_new'] = nd[up_sl][0]['lemma_new']
    word[u'distance_to_tor'] = distance
    word[u'tor_id'] = nd[up_sl][0]['id']
    if word[u'pos'] == u'N':
        try:
            word[u'tor_gender'] = nd[up_sl][0]['gender']
        except:
            print u'we miss the gender!', word['lemma']
    word[u'tor_examples'] = {}
    word[u'tor_unanalysed_examples'] = {}
    word[u'tor_predicted_stems'] = {}
    word[u'tor_scores'] = {}
    word[u'tor_par_stem'] = {}
    for dict_entity in nd[up_sl]:
        word[u'tor_unanalysed_examples'] = my_undate(word['tor_unanalysed_examples'],
                                                     dict_entity['unanalysed_examples'])
        if word['pos'] == u'N' or word['pos'] == u'V' or word['pos'] == 'Adj':
            try:
                word[u'tor_examples'] = my_undate(word['tor_examples'], dict_entity['examples'])
                word[u'tor_predicted_stems'] = my_undate(word['tor_predicted_stems'], dict_entity['predicted_stems'])
                word[u'tor_scores'] = my_undate(word['tor_scores'], dict_entity['scores'])
                word[u'tor_par_stem'] = my_undate(word['tor_par_stem'], dict_entity['par_stem'])
            except KeyError:
                # print u'but there were no tor pr stems!', word['lemma'], dict_entity['lemma']
                pass # это штуки, у которых не тпределился тип
            except AttributeError:
                print u'have list instead of dict', word['lemma']
    return word, added


def my_undate(x, y): # тут теряем часть примеров, что грустненько, но нет времени исправлять
    if len(x) == 0:
        return y
    if len(y) == 0:
        return x
    if len(x) > y:
        y.update(x)
        return y
    x.update(y)
    return x


def use_leven(word, up_dict, word_pos, gender=u'-'):
    l1 = []
    l2 = []
    for lemma in up_dict:
        if word_pos == up_dict[lemma][0]['pos']:  # а если омонимия на ур. лемм?
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

# !!!!!!!!!!!!!!!


nc = codecs.open(u'no_correspondence_7.txt', u'w', u'utf-8')
sc = codecs.open(u'have_several_corr_7.txt', u'w', u'utf-8')
oc = codecs.open(u'have_one_corr_7.txt', u'w', u'utf-8')

td, nd = files_open()

print type(td), type(nd)

t1 = time.clock()

nd, added = add_torot_to_up(td, nd)

print type(td)
print type(nd)

t2 = time.clock()
print t2-t1, u'for breaking bass'

nd = add_rest(td, added, nd)






t3 = time.clock()
print t3-t2, u'for making magic'
llllll = codecs.open(u'joined_3.json', u'w', u'utf-8')
json.dump(nd, llllll, ensure_ascii=False, indent=2)
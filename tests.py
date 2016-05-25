#-*- coding: utf-8 -*-

import codecs
import json
import random

t = codecs.open(u'poliakov_added_5.json', u'r', u'utf-8')
tf = json.load(t)

n = codecs.open(u'rnc_gram_0.json', u'r', u'utf-8')
nf = json.load(n)


def p_tagging(tf):
    chosen_ones = []
    i = 0
    ss = codecs.open(u'100nouns_best_rnc.txt', u'w', u'utf-8')
    while i < 100:
        r_i = random.choice(tf)
        if u'scores' not in r_i:
            continue
        if r_i[u'pos'] != u'N':
            continue
        max = 0
        max_arr = []
        for par in r_i[u'scores']:
            # if r_i[u'scores'][par] >= 0.5:
                print i
                if r_i[u'scores'][par] == max:
                    max_arr.append(par)
                elif r_i[u'scores'][par] > max:
                    max_arr = [par]
                    max = r_i[u'scores'][par]
        if len(max_arr) == 1:
            i += 1
            ss.write(r_i['lemma'] + u'\t' + max_arr[0] + u'\t' + str(max) + u'\r\n')
    # json.dump(chosen_ones, ss, ensure_ascii=False, indent=2)

p_tagging(nf)

def hawlick():
    chosen_ones = []
    i = 0
    ss = codecs.open(u'100hawlick.csv', u'w', u'utf-8')
    while i < 100:
        r_i = random.choice(tf)
        if u'lemma' not in r_i:
            continue
        i += 1
        print i
        chosen_ones.append(r_i)
        ss.write(r_i[u'lemma'] + u'\t' + r_i[u'lemma_new'] + u'\r\n')

# hawlick()


def comparison():
    ss = codecs.open(u'100lemmata.csv', u'w', u'utf-8')
    i = 0
    while i < 100:
        r_i = random.choice(tf)
        if u'lemma' not in r_i or u'up_lemma' not in r_i:
            continue
        i += 1
        print i
        ss.write(r_i[u'lemma'] + u'\t' + r_i[u'lemma_new'] + u'\t' + r_i[u'up_lemma'] + u'\r\n')


# comparison()

def sevcor():
    tf = codecs.open(u'have_several_corr_7.txt', u'r', u'utf-8')
    ss = codecs.open(u'100cannotchose.csv', u'w', u'utf-8')
    tf = tf.read()
    tf = tf.split(u'\r\n')
    i = 0
    while i < 100:
        r_i = random.choice(tf)
        i += 1
        print i
        ss.write(r_i + u'\r\n')

# sevcor()
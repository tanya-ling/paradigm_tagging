# -*- coding: utf-8 -*-
import codecs
import re
import noun_class
from hawlik_low import oslo_trans
from noun_class import letterchange

def open_rnc():
    f = codecs.open(u'oldrus_ana.txt', u'r', u'utf-8')
    dict = {}
    i = 0
    consonants = u'кнгзхвпрлджмтб'.split()
    firstline = True
    for line in f:
        if firstline or u'NONLEX' in line:
            firstline = False
            continue
        line = line.rstrip()
        n, ana, word, wordnorm, worder, posnorm, lemmanorm, lemma, pos = line.split(u'\t')
        if u'PRO' in ana:
            continue
        i += 1
        if i < 62095:
            continue
        simple_lemma = letterchange(lemmanorm.replace(u'э', u'ѣ'))
        if wordnorm[-1] in consonants:
            wordnorm += u'ъ'
        if simple_lemma not in dict:
            new_word = noun_class.word()
        else:
            new_word = dict[simple_lemma]
        new_word.lemma = lemma
        new_word.pos = translate_pos(pos)
        new_word.id = i
        new_word.rnc_id.append(n)
        new_word.lemma_after_fall = oslo_trans(simple_lemma)
        new_example = noun_class.example()
        new_example.form = [word]
        # new_example.form_norm = letterchange(wordnorm.replace(u'э', u'ѣ'))
        if pos == u'N' or pos == u'V' or pos == u'Adj':
            new_example.analys, gender = get_analysis(ana, pos)
        else:
            if u'uninfl' not in new_word.unan_examples:
                new_word.unan_examples[u'uninfl'] = []
            new_word.unan_examples[u'uninfl'].append(new_example.form)
        if pos != u'N':
            gender = u'-'
        new_word.gramm = gender
        if new_example.analys == u'supine' or new_example.analys == u'participle' or new_example.analys == u'diff':
            if gender not in new_word.unan_examples:  # в этой и следующих строчках это не род, просто та же переменная!
                new_word.unan_examples[gender] = []
            new_word.unan_examples[gender].append(new_example.form)
        else:
            found = False
            for example in new_word.examples:
                if example.analys == new_example.analys:
                    example.form.append(new_example.form[0])
                    found = True
                    break
            if not found:
                new_word.examples.append(new_example)
        dict[simple_lemma] = new_word
        print u'rnc is opening, ', str(100 * float(i)/343096), u'%', i
    return dict


def translate_pos(pos):
    if pos == u'S':
        pos = u'N'
    elif pos == u'A':
        pos = u'Adj'
    return pos


def get_analysis(ana, pos):
    s = re.search(u'gr="(.*?)"', ana)
    try:
        an = s.group(1).replace(u',persn', u'').replace(u'?', u'').replace(u'!', u'')
        if len(an) == 0:
            return u'diff', u'unmarked'
    except AttributeError:
        print u'no group 80', ana
    if u'V,past,sg' == an or an == u'V,past,pl' or u'damaged' in an or an == u'V,praes,sg' or an == u'V,praes,pl':
        return u'diff', an
    if an == u'V,praes' or an == u'V,sg,3p':
        an = u'V,praes,sg,3p'
    if an == u'V,3p,inf' or an == u'V,pl,3p':
        an = u'V,praes,pl,3p'
    if an == u'V,1p,sg':
        an = u'V,praes,1p,sg'
    a = an.split(u',')
    if a[0] == u'incorrect':
        a = a[1:]
    if pos == u'N':
        gender = a[1]
        number = a[2]
        case = a[3]
        if case == u'acc-gen':
            case = u'gen'
        gramm = number + u',' + case
    elif pos == u'V':
        if an[:5] == u'imper' or an[:5] == u'supin':
            an = u'V,' + an
            a = an.split(u',')
        if an == u'V':
            return u'inf', u'-'
        if len(a) == 1:
            print ana, u'too short'
        if a[1] == u'supin' or a[1] == u'inf':
            gramm = a[1]
            gender = an
        elif a[1] == u'partcp':
            try:
                if u'perf' in an:
                    number = a[3]
                    gender = a[4]
                    gramm = u'perf,' + number + u',' + gender
                else:
                    gramm = u'participle'
                    gender = an
            except IndexError:
                print u'105 indexerror', an
        else:
            tense = a[1]
            try:
                number = a[2]
                person = a[3]
            except IndexError:
                print u'indexerror 101', an
            if tense != u'imper':
                gramm = u'indic,' + tense + u',' + number + u',' + person
            else:
                gramm = tense + u',' + number + u',' + person
            gender = u'-'
    elif pos == u'Adj':
        number = a[1]
        gender = a[2]
        case = a[3]
        gramm = number + u',' + gender + u',' + case
    return gramm, gender


open_rnc()
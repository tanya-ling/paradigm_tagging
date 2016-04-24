#-*- coding: utf-8 -*-
import time
import codecs
import noun_class
import json


def make_content_dict(forms, pos):
    content_dict = {}
    forms = forms.split(u'|')
    for form in forms:
        try:
            tgramm, examples = form.split(u':')
        except:
            print u'mistake in lemmalist_file:', form
            continue
        tgramm = tgramm[:-1]
        if tgramm == u'non-infl':
            continue
        if pos == u'N':
            gramm, gender = make_content_dict_noun(tgramm)
        if pos == u'Adj':
            gramm, gender = make_content_dict_adj(tgramm)
        examples = examples.split(u',')
        content_dict[gramm] = examples
    return content_dict, gender

def make_content_dict_noun(tgramm):
        try:
            number, gender, case, infl = tgramm.split(u'., ')
        except:
            print u'2 mistake in lemmalist file', tgramm
        if case == u'gen./dat':
            case = u'dat'
        gramm = number + u',' + case
        return gramm, gender

def make_content_dict_adj(tgramm):
        tgramm = tgramm.replace(u'k,', u'k.,')
        tgramm = tgramm.replace(u'g,', u'g.,')
        try:
            number, gender, case, bla, strong, infl = tgramm.split(u'., ')
        except:
            print u'2 mistake in lemmalist file', tgramm
        if case == u'gen./dat':
            case = u'dat'
        gramm = number + u',' + gender + u',' + case
        if strong == u'strong':
            gramm += u',brev'
        return gramm, u'-'

paradigmy = noun_class.parad_from_file(u'прилфлексии.txt')
anal_data = noun_class.analysis_data(paradigmy)

f = codecs.open(u'lemmalist.csv', u'r', u'utf-8')
w = codecs.open(u'torot_gram.json', u'w', u'utf-8')
wb = codecs.open(u'torot_miss.json', u'w', u'utf-8')
id = 0
parsed = 0
unparsed = 0
time1 = time.clock()
great_d = []
misirable = []
pos = u'Adj'
for line in f:
    line = line.rstrip()
    lemma_content = line.split(u';')
    #if lemma_content[2] != u'common noun' or lemma_content[0] == u'FIXME':
    if lemma_content[2] != u'adjective' or lemma_content[0] == u'FIXME':
        continue
    id += 1
    # if id < 6:
    #     continue
    lemma_content_dict, gender = make_content_dict(lemma_content[3], pos)
    new_word = noun_class.word()
    new_word.lemma = lemma_content[0]
    if pos == u'N':
        new_word.pos = u'N'
    elif pos == u'Adj':
        new_word.pos = u'Adj'
    new_word.gramm = gender
    new_word.torot_id = lemma_content[1]
    new_word.id = id
    new_word.lemma_after_fall = noun_class.oslo_trans(new_word.lemma)
    new_word.create_examples(lemma_content_dict)
    new_word.guess(anal_data)
    new_word.group_stems()
    new_word.print_par_stem()
    print u'____________________________________________________________________'
    if id == 15:
        break
    if len(new_word.group_par_stem) > 0:
        parsed += 1
        wtw = new_word.write_guessed_to_file()
        great_d.append(wtw)
        # json.dump(wtw, w, ensure_ascii=False, indent=2)
    else:
        unparsed += 1
        wtw = new_word.write_unguessed_to_file()
        misirable.append(wtw)
time2 = time.clock()
t = time2 - time1
tword = parsed + unparsed
print 100*float(parsed)/tword, u'% parsed, time for one word apr. ', t/tword, u', total time ', t
time3 = time.clock()
json.dump(great_d, w, ensure_ascii=False, indent=2)
w.close()
print time3-time2, u'for writing parsed'
time4 = time.clock()
json.dump(misirable, wb, ensure_ascii=False, indent=2)
print time4-time3, u'for writing unparsed'
wb.close()
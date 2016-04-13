#-*- coding: utf-8 -*-
import time
import codecs
import noun_class

def make_content_dict(forms):
    content_dict = {}
    forms = forms.split(u'|')
    for form in forms:
        tgramm, examples = form.split(u':')
        tgramm = tgramm[:-1]
        if tgramm == u'non-infl':
            continue
        number, gender, case, infl = tgramm.split(u'., ')
        if case == u'gen./dat':
            case = u'dat'
        gramm = number + u',' + case
        examples = examples.split(u',')
        content_dict[gramm] = examples
    return content_dict, gender

paradigmy = noun_class.parad_from_file()
anal_data = noun_class.analysis_data(paradigmy)

f = codecs.open(u'lemmalist.csv', u'r', u'utf-8')
id = 0
parsed = 0
unparsed = 0
time1 = time.clock()
for line in f:
    line = line.rstrip()
    lemma_content = line.split(u';')
    if lemma_content[2] != u'common noun' or lemma_content[0] == u'FIXME':
        continue
    id += 1
    # if id < 6:
    #     continue
    lemma_content_dict, gender = make_content_dict(lemma_content[3])
    new_word = noun_class.word()
    new_word.lemma = lemma_content[0]
    new_word.pos = u'N'
    new_word.gramm = gender
    new_word.torot_id = lemma_content[1]
    new_word.id = id
    new_word.create_examples(lemma_content_dict)
    new_word.guess(anal_data)
    new_word.group_stems()
    # new_word.print_par_stem()
    # print u'____________________________________________________________________'
    if id == 15:
        break
    if len(new_word.group_par_stem) > 0:
        parsed += 1
    else:
        unparsed += 1
time2 = time.clock()
t = time1 - time2
tword = parsed + unparsed
print parsed/tword*100, u'% parsed, time for one word apr. ', t/tword, u', total time ', t
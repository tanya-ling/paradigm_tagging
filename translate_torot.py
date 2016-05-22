#-*- coding: utf-8 -*-
import time
import codecs
import noun_class
import json


def make_content_dict(forms, pos):
    content_dict = {}
    forms = forms.split(u'|')
    unanalysed_content = {}
    for form in forms:
        try:
            tgramm, examples = form.split(u':')
        except:
            print u'mistake in lemmalist_file:', form
            continue
        tgramm = tgramm[:-1]
        if tgramm == u'non-infl':
            if pos != u'N':
                gender = u'-'
                unanalysed_content[tgramm] = examples.split(u',')
            continue
        if pos == u'N':
            gramm, gender = make_content_dict_noun(tgramm)
        elif pos == u'Adj' or pos == u'A-NUM':
            gramm, gender = make_content_dict_adj(tgramm)
            if gramm == u'vocative':
                unanalysed_content[tgramm] = examples.split(u',')
                continue
        elif pos == u'V':
            gramm = make_content_dict_verb(tgramm)
            gender = u'-'
            if gramm == u'participle' or gramm == u'supine':
                unanalysed_content[tgramm] = examples.split(u',')
                continue
        else:
            unanalysed_content[tgramm] = examples.split(u',')
            gender = u'-'
            continue
        examples = examples.split(u',')
        # print u't_t, line 30',  gramm, examples
        content_dict[gramm] = examples
    try:
        return content_dict, gender, unanalysed_content
    except UnboundLocalError:
        print u'no gender in: ', forms, pos
        return content_dict, u'-', unanalysed_content


def make_content_dict_noun(tgramm):
        try:
            number, gender, case, infl = tgramm.split(u'., ')
        except:
            print u'2.0 mistake in lemmalist file', tgramm
        gender = genderize(gender)
        if case == u'gen./dat':
            case = u'dat'
        gramm = number + u',' + case
        return gramm, gender


def become_stronger(tgramm):
        tgramm = tgramm.replace(u'k,', u'k.,')
        tgramm = tgramm.replace(u'g,', u'g.,')
        return tgramm


def make_content_dict_adj(tgramm):
        tgramm = become_stronger(tgramm)
        if u'voc' in tgramm:
            return u'vocative', u'-'
        try:
            number, gender, case, bla, strong, infl = tgramm.split(u'., ')
            gender = genderize(gender)
        except:
            print u'2 mistake in lemmalist file', tgramm
        if case == u'gen./dat':
            case = u'dat'
        gramm = number + u',' + gender + u',' + case
        if strong == u'strong':
            gramm += u',brev'
        return gramm, u'-'

def genderize(gender):
    if u'/' in gender:
        if u'm' in gender:
            gender = u'm'
        elif u'f' in gender:
            gender = u'f'
        else:
            print u'what_the_gender?', gender
            gender = u'm'
    return gender


def make_content_dict_verb(tgramm):
    tgramm = become_stronger(tgramm)
    if u'sup.' in tgramm:
        return u'supine'
    if u'part' in tgramm:
        if u'result' not in tgramm:
            return u'participle'
        try:
            number, result, part, voice, gender, case, strong, infl = tgramm.split(u'., ')
            gender = genderize(gender)
            gramm = u'perf,' + number + u',' + gender
            return gramm
        except:
            print u'3 mistake in lemmalist file', tgramm
    if u'inf.,' in tgramm:
        gramm = u'inf'
        return gramm
    try:
        person, number, tense, mood, voice, infl = tgramm.split(u'., ')
        person = translate_person(person)
        if mood == u'imp':
            gramm = u'imper,' + number + u',' + person
            return gramm
        else:
            tense = translate_tense(tense)
            if tense == u'analyt,indic,praes,':
                return tense + number + u',' + person
            gramm = u'indic,' + tense + u',' + number + u',' + person
            return gramm
    except:
        print u'4 mistake in lemmalist file', tgramm


def translate_tense(tense):
    if tense == u'pres':
        tense = u'praes'
    elif tense == u'fut':
        tense = u'analyt,indic,praes,'
    return tense


def translate_mood(mood):
    if mood == u'ind':
        mood = u'indic'
    else:
        print u'strange mood', mood
    return mood


def translate_person(person):
    if u'1' in person:
        person = u'1p'
    elif u'2' in person:
        person = u'2p'
    elif u'3' in person:
        person = u'3p'
    else:
        print u'strange person', person
    return person


def mal(pos, lemma):
    if pos == u'Adj':
        if lemma[-1] == u'ъ':
            if lemma[-3:] != u'евъ' and lemma[-3:] != u'овъ':
                lemma = lemma[:-1] + u'ый'
    return lemma



paradigmy_a = noun_class.parad_from_file(u'прилфлексии.txt', u'описание основ сущ_lite.txt')
paradigmy_n = noun_class.parad_from_file(u'сущфлексии.txt', u'описание основ сущ_lite.txt')
paradigmy_v = noun_class.parad_from_file(u'глагфлексии.txt', u'глаголы_основы.txt')
anal_data_a = noun_class.analysis_data(paradigmy_a)
anal_data_n = noun_class.analysis_data(paradigmy_n)
anal_data_v = noun_class.analysis_data(paradigmy_v)

f = codecs.open(u'lemmalist.csv', u'r', u'utf-8')
w = codecs.open(u'torot_gram_7.json', u'w', u'utf-8')
wb = codecs.open(u'torot_miss_7.json', u'w', u'utf-8')
id = 0
parsed = 0
unparsed = 0
time1 = time.clock()
great_d = []
misirable = []
firstline = True
for line in f:
    if firstline:
        firstline = False
        continue
    line = line.rstrip()
    lemma_content = line.split(u';')
    if lemma_content[0] == u'FIXME':
        continue
    if u'pronoun' in lemma_content[2]:
        continue
    id += 1
    # if id < 1000:
    #     continue
    if lemma_content[2] == u'verb':
        pos = u'V'
        uninfl = False
    elif lemma_content[2] == u'adjective':
        pos = u'Adj'
        uninfl = False
    elif lemma_content[2] == u'common noun' or lemma_content[2] == u'proper noun':
        pos = u'N'
        uninfl = False
    elif lemma_content[2] == u'ordinal numeral':
        pos = u'A-NUM'
        uninfl = True
        continue
    else:
        pos = lemma_content[2]
        uninfl = True
        # print u'uninflected', lemma_content[0]

    lemma_content_dict, gender, unanal_content = make_content_dict(lemma_content[3], pos)
    new_word = noun_class.word()
    new_word.lemma = lemma_content[0]
    if new_word.lemma[-1] == u' ':
        new_word.lemma = new_word.lemma[:-1]
    new_word.pos = pos
    new_word.gramm = gender
    new_word.torot_id = lemma_content[1]
    new_word.id = id
    new_word.lemma_after_fall = mal(pos, noun_class.oslo_trans(new_word.lemma))
    new_word.unan_examples = unanal_content
    # print u'translate_torot, line 155', lemma_content_dict
    new_word.create_examples(lemma_content_dict)
    if pos == u'N':
        new_word.guess(anal_data_n)
    elif pos == u'V':
        new_word.guess(anal_data_v)
    elif pos == u'Adj':
        new_word.guess(anal_data_a)
    if not uninfl:
        new_word.group_stems()
        new_word.predict_stems()
        if new_word.predicted_par_stem == u'delete_this_word':
            continue
        new_word.change_score()
    # new_word.print_par_stem()
    print new_word.torot_id, float(id)/10319 * 100, u'% made'
    # if id == 1070:
    #     break
    if len(new_word.group_par_stem) > 0 or uninfl:
        parsed += 1
        wtw = new_word.write_guessed_to_file()
        great_d.append(wtw)
        # json.dump(wtw, w, ensure_ascii=False, indent=2)
    else:
        unparsed += 1
        wtw = new_word.write_unguessed_to_file()
        wtw2 = new_word.write_guessed_to_file_short()
        misirable.append(wtw)
        great_d.append(wtw2)
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

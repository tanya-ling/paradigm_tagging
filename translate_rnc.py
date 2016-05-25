# -*- coding: utf-8 -*-
import codecs
import re
import noun_class
from hawlik_low import oslo_trans
from noun_class import letterchange
import time
import json


def open_rnc():
    f = codecs.open(u'oldrus_ana.txt', u'r', u'utf-8')
    dict = {}
    i = 0
    consonants = u'кнгзхвпрлджмтб'.split()
    firstline = True
    pm_n = 0
    pm_v = 0
    pm_a = 0
    for line in f:
        if firstline or u'NONLEX' in line:
            firstline = False
            continue
        line = line.rstrip()
        n, ana, word, wordnorm, worder, posnorm, lemmanorm, lemma, pos = line.split(u'\t')
        if u'PRO' in ana:
            continue
        i += 1
        # if i < 70000:
        #     continue
        simple_lemma = letterchange(lemmanorm.replace(u'э', u'ѣ'))
        if wordnorm[-1] in consonants:
            wordnorm += u'ъ'
        if simple_lemma not in dict:
            new_word = noun_class.word()
        else:
            new_word = dict[simple_lemma]
        new_word.lemma = lemma
        pos = translate_pos(pos)
        new_word.pos = pos
        # print simple_lemma, u'simple lemma', new_word.pos
        new_word.id = i
        new_word.simple_lemma = simple_lemma
        new_word.rnc_id.append(n)
        new_word.lemma_after_fall = oslo_trans(simple_lemma)
        new_example = noun_class.example()
        new_example.form = [word]
        # new_example.form_norm = letterchange(wordnorm.replace(u'э', u'ѣ'))
        if pos == u'N' or pos == u'V' or pos == u'Adj':
            new_example.analys, gender = get_analysis_2(ana, pos)
            if gender == u'ignore':
                continue
            if new_example.analys == u'':
                print u'empty analysis', word.lemma, new_example.form
            # print new_example.form, new_example.analys, u'49', simple_lemma
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
                    new_form_norm = noun_class.form_norm()
                    new_form_norm.form = letterchange(wordnorm.replace(u'э', u'ѣ'))
                    new_example.form_norm.append(new_form_norm)
                    found = True
                    break
            if not found:
                new_form_norm = noun_class.form_norm()
                new_form_norm.form = letterchange(wordnorm.replace(u'э', u'ѣ'))
                new_example.form_norm.append(new_form_norm)
                new_word.examples.append(new_example)
            if pos == u'N' and pm_n < len(new_word.examples):
                pm_n = len(new_word.examples)
            elif pos == u'V' and pm_v < len(new_word.examples):
                pm_v = len(new_word.examples)
            elif pos == u'Adj' and pm_a < len(new_word.examples):
                pm_a = len(new_word.examples)
        dict[simple_lemma] = new_word
        if i % 10000 == 0:
            print u'rnc is opening, ', str(100 * float(i)/343096), u'%', i
        # if len(dict) == 500:
        #     break
    return dict, pm_n, pm_a, pm_v


def translate_pos(pos):
    if pos == u'S':
        pos = u'N'
    elif pos == u'A':
        pos = u'Adj'
    return pos


def correct_an(an):
    if an == u'V,praes' or an == u'V,sg,3p' or an == u'V,praes,3p':
        an = u'V,praes,sg,3p'
    elif an == u'V,3p,inf' or an == u'V,pl,3p' or an == u'V,3p,pl':
        an = u'V,praes,pl,3p'
    elif an == u'V,1p,sg':
        an = u'V,praes,1p,sg'
    elif an == u'cond,3p,sg' or an == u'3p,sg' or an == u'V,sg' or an == u'V,sg,1p':
        an = u'V,perf,sg,m'
    elif an == u'V,pl,2p':
        an = u'V,praes,pl,2p'
    elif an == u'cond,3p,pl':
        an = u'V,perf,pl,3p'
    elif an == "iperf,3p,pl":
        an = "V,iperf,3p,pl"
    elif an == u'V,aor,sg' or an == u'V,aor,3p':
        an = u'V,aor,sg,3p'
    elif an == u'V,perf,3p':
        an = u'V,perf,sg,f'


    elif an == u'A,sg,m':
        an = u'A,m,sg,gen'

    elif an == u'A,sg,ins':
        an = u'A,m,sg,ins'

    elif an == u'A,du,gen' or an == u'incorrect,A,du,gen':
        an = u'A,m,du,gen'
    elif an == u'A,du,ins' or an == u'incorrect,A,du,ins':
        an = u'A,m,du,ins'
    elif an == u'A,du,dat' or an == u'incorrect,A,du,dat':
        an = u'A,m,du,dat'
    elif an == u'A,du,gen' or an == u'incorrect,A,du,gen':
        an = u'A,m,du,gen'

    # elif an == u'A,pl,gen':
    #     an = u'A,pl,m,gen'
    elif an == u'A,pl,acc-gen' or an == u'incorrect,A,pl,gen' or an == u'A,pl,as_S,n' or an == u'A,pl,gen' or an == u'A,pl,as_S':
        an = u'A,pl,m,gen'
    elif an == u'A,pl,dat':
        an = u'A,pl,m,dat'
    elif an == u'A,pl,ins':
        an = u'A,pl,m,ins'
    elif an == u'A,pl,loc' or an == u'incorrect,A,pl,loc':
        an = u'A,pl,m,loc'



    elif an == u'S,m' or an == u'm,sg,nom' or an == u'S,m,sg':
        an = u'S,m,sg,nom'
    elif an == u'S' or an == u'S,n' or an == u'S,n,sg' or an == u'n,sg,nom':
        an = u'S,n,sg,nom'
    elif an == u'f' or an == u'S,f,sg' or an == u'f,nom' or an == u'S,f':
        an = u'S,f,sg,nom'

    elif an == u'S,m,acc':
        an = u'S,m,sg,acc'
    elif an == u'f,sg,acc' or an == u'f,dat' or an == u'f,acc':
        an = u'S,f,sg,acc'

    elif an == u'm,gen,in_persn' or an == u'S,m,sg' or an == u'S,m,gen' or an == u'f,acc-gen' or an == u'S,gen' or an == u'm,sg,acc-gen':
        an = u'S,m,sg,gen'
    elif an == u'S,f,gen' or an == u'f,gen' or an == u'f,sg,acc-gen':
        an = u'S,f,sg,gen'
    elif an == u'S,n,gen' or an == u'n,gen' or an == u'n,sg,acc-gen':
        an = u'S,n,sg,gen'

    elif an == u'm,loc' or an == u'S,m,loc' or an == u'S,loc':
        an = u'S,m,sg,loc'
    elif an == u'f,loc' or an == u'S,f,loc':
        an = u'S,f,sg,loc'
    elif an == u'loc' or an == u'n,loc' or an == u'S,n,loc':
        an = u'S,n,sg,loc'

    elif an == u'm,ins,in_persn' or an == u'S,m,ins' or an == u'm':
        an = u'S,m,sg,ins'

    elif an == u'S,dat':
        an = u'S,m,sg,dat'
    elif an == u'S,f,dat':
        an = u'S,f,sg,dat'


    elif an == u'S,pl,nom' or an == u'S,m,pl' or an == u'S,pl':
        an = u'S,m,pl,nom'
    elif an == u'S,f,nom':
        an = u'S,f,pl,nom'
    elif an == u'S,n,pl':
        an = u'S,n,pl,nom'

    elif an == u'S,pl,acc' or an == u'incorrect,S,pl,acc':
        an = u'S,m,pl,acc'
    elif an == u'S,f,acc' or an == u'incorrect,S,f,acc':
        an = u'S,f,pl,acc'

    elif an == u'S,pl,gen' or an == u'S,pl,in_topn' or an == u'S,pl,acc-gen' or an == u'm,pl,gen':
        an = u'S,m,pl,gen'
    elif an == u'f,pl,gen':
        an = u'S,f,pl,gen'
    elif an == u'n,pl,gen':
        an = u'S,n,pl,gen'

    elif an == u'S,pl,loc' or an == u'incorrect,S,pl,loc':
        an = u'S,m,pl,loc'

    elif an == u'S,pl,ins' or an == u'incorrect,S,pl,ins':
        an = u'S,m,pl,ins'
    elif an == u'f,ins':
        an = u'S,f,pl,ins'

    elif an == u'S,pl,dat' or an == u'incorrect,S,pl,dat':
        an = u'S,m,pl,dat'
    return an


def get_analysis_2(ana, pos):
    ana = ana.replace(u'nonpast', u'praes')
    s = re.search(u'gr="(.*?)"', ana)
    try:
        an = s.group(1).replace(u',persn', u'').replace(u'?', u'').replace(u'!', u'').replace(u',topn', u'').replace(
            u',as_S', u'')
        if len(an) == 0:
            return u'diff', u'unmarked'
    except AttributeError:
        print u'no group 80', ana
        return u'ignore', u'ignore'
    if u'V,past,sg' == an or an == u'V,past,pl' or u'damaged' in an or an == u'V,praes,sg' or an == u'V,praes,pl' or u'supin' in an or u'0' in an or an == u'A':
        return u'diff', an
    if pos == u'N':
        gramm = get_number(an) + u',' + get_case(an)
        return gramm, get_gender(an)
    elif pos == u'Adj':
        if u'comp' in an:
            return u'diff', an
        number = get_number(an)
        gender = get_gender(an)
        case = get_case(an)
        gramm = number + u',' + gender + u',' + case
        return gramm, u'-'
    elif pos == u'V':
        number = get_number(an)
        if u'partcp' in an or u'perf' in an or u'past' in an or u'cond' in an:
            if u'perf' in an or u'past' in an or u'cond' in an:
                gender = get_gender(an)
                gramm = u'perf,' + number + u',' + gender
                return gramm, u'-'
            return u'diff', an
        person = get_person(an)
        if u'imper' in an:
            return u'imper,' + number + u',' + person, u'-'
        if u'inf' in an or an == u'V':
            return u'inf', u'-'
        tense = get_tense(an)
        if tense == u'analyt':
            gramm = u'analyt,indic,praes,' + number + u',' + person
        else:
            gramm = u'indic,' + tense + u',' + number + u',' + person
        return gramm, u'-'


def get_tense(an):
    if u'aor' in an:
        number = u'aor'
    elif u'iperf' in an:
        number = u'imperf'
    elif u'praes' in an or u'nonpast' in an:
        number = u'praes'
    elif u'fut' in an:
        number = u'analyt'
    else:
        # print u'no tense', an
        number = u'praes'
    return number

def get_person(an):
    if u'1p' in an:
        number = u'1p'
    elif u'2p' in an:
        number = u'2p'
    elif u'3p' in an:
        number = u'3p'
    else:
        number = u'3p'
    return number

def get_gender(an):
    an = u',' + an + u','
    if u',m,' in an:
        gender = u'm'
    elif u',n,' in an:
        gender = u'n'
    elif u',f,' in an:
        gender = u'f'
    else:
        gender = u'm'
    return gender

def get_number(an):
    if u'sg' in an:
        number = u'sg'
    elif u'pl' in an:
        number = u'pl'
    elif u'du' in an:
        number = u'du'
    else:
        number = u'sg'
    return number

def get_case(an):
    if u'nom' in an:
        case = u'nom'
    elif u'gen' in an:
        case = u'gen'
    elif u'acc' in an:
        case = u'acc'
    elif u'dat' in an:
        case = u'dat'
    elif u'ins' in an:
        case = u'ins'
    elif u'loc' in an:
        case = u'loc'
    else:
        case = u'nom'
    return case

def get_analysis(ana, pos):
    ana = ana.replace(u'nonpast', u'praes')
    s = re.search(u'gr="(.*?)"', ana)
    try:
        an = s.group(1).replace(u',persn', u'').replace(u'?', u'').replace(u'!', u'').replace(u',topn', u'').replace(u',as_S', u'')
        if len(an) == 0:
            return u'diff', u'unmarked'
    except AttributeError:
        print u'no group 80', ana
        return u'ignore', u'ignore'
    if u'V,past,sg' == an or an == u'V,past,pl' or u'damaged' in an or an == u'V,praes,sg' or an == u'V,praes,pl' or u'supin' in an or u'0' in an or an == u'A':
        return u'diff', an
    an = correct_an(an)
    a = an.split(u',')
    if a[0] == u'incorrect':
        a = a[1:]
    if pos == u'N':
        try:
            gender = a[1]
            number = a[2]
            case = a[3]
        except IndexError:
            print u'157 indexerror', ana
            return u'diff', an
        if case == u'acc-gen':
            case = u'gen'
        if number == u'm' or number == u'f' or number == u'n':
            gramm = case + u',nom'
        elif number[0] == u'f' or number[0] == u'm' or number[0] == u'n':
            number = number[2:]
            gramm = number + u',' + case
        else:
            gramm = number + u',' + case
        # print u'noun analyses', gramm
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
                    if u'p' in gender:
                        gender = u'm'
                    if number == u'm':
                        gramm = u'perf,' + gender + u',' + number
                    else:
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
            if tense == u'iperf':
                tense = u'imperf'
            if tense != u'imper':
                if tense == u'past':
                    try:
                        gramm = u'perf,' + a[5] + u',' + a[4]
                    except:
                        return u'diff', an
                else:
                    if number == u'3p':
                        gramm = u'indic,' + tense + u',' + person + u',' + number
                    else:
                        gramm = u'indic,' + tense + u',' + number + u',' + person
            else:
                gramm = tense + u',' + number + u',' + person
            gender = u'-'
    elif pos == u'Adj':
        if u'comp' in an:
            return u'diff', an
        try:
            number = a[1]
            gender = a[2]
            case = a[3]
        except IndexError:
            print u'indexerror', ana
            return u'diff', an
        gramm = number + u',' + gender + u',' + case
    return gramm, gender

paradigmy_a = noun_class.parad_from_file(u'прилфлексии.txt', u'описание основ сущ_lite.txt')
paradigmy_n = noun_class.parad_from_file(u'сущфлексии.txt', u'описание основ сущ_lite.txt')
paradigmy_v = noun_class.parad_from_file(u'глагфлексии.txt', u'глаголы_основы.txt')
anal_data_a = noun_class.analysis_data(paradigmy_a)
anal_data_n = noun_class.analysis_data(paradigmy_n)
anal_data_v = noun_class.analysis_data(paradigmy_v)
print u'paradigms compiled'
dict, pm_n, pm_a, pm_v = open_rnc()
print pm_v, pm_n, pm_a, u'pos max for rnc'
ld = len(dict)
print ld, u'lexemes loaded'
w = codecs.open(u'rnc_gram_1.json', u'w', u'utf-8')
wb = codecs.open(u'rnc_miss_1.json', u'w', u'utf-8')
index = 0
parsed = 0
unparsed = 0
time1 = time.clock()
great_d = []
misirable = []
for key_lemma in dict:
    # print key_lemma
    # for example in dict[key_lemma].examples:
    #     print example.analys, example.form
    #     for form in example.form:
    #         print form
    #     for fn in example.form_norm:
    #         print fn.form
    word = dict[key_lemma]
    if word.pos == u'V' or word.pos == u'N' or word.pos == u'Adj':
        uninfl = False
    else:
        uninfl = True
    index += 1
    if word.pos == u'N':
        word.guess(anal_data_n)
    elif word.pos == u'V':
        word.guess(anal_data_v)
    elif word.pos == u'Adj':
        word.guess(anal_data_a)
    if not uninfl:
        word.group_stems()
        word.predict_stems(rnc=True)
        if word.predicted_par_stem == u'delete_this_word':
            continue
        word.change_score()
    # new_word.print_par_stem()
    print word.rnc_id[0], float(index) / ld * 100, u'% made'
    # if index == 1070:
    #     break
    if len(word.group_par_stem) > 0 or uninfl:
        parsed += 1
        wtw = word.write_guessed_to_file(rnc=True)
        great_d.append(wtw)
        # json.dump(wtw, w, ensure_ascii=False, indent=2)
    else:
        unparsed += 1
        wtw = word.write_unguessed_to_file()
        wtw2 = word.write_guessed_to_file_short(rnc=True)
        misirable.append(wtw)
        great_d.append(wtw2)
time2 = time.clock()
t = time2 - time1
tword = parsed + unparsed
print 100 * float(parsed) / tword, u'% parsed, time for one word apr. ', t / tword, u', total time ', t
time3 = time.clock()
json.dump(great_d, w, ensure_ascii=False, indent=2)
w.close()
print time3 - time2, u'for writing parsed'
time4 = time.clock()
json.dump(misirable, wb, ensure_ascii=False, indent=2)
print time4 - time3, u'for writing unparsed'
wb.close()
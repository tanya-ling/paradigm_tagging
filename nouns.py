#-*- coding: utf-8 -*-
import re
import codecs

def open_stems():
    f = codecs.open(u'описание основ сущ.txt', u'r', u'utf-8')
    dict = {}
    for line in f:
        line = line.rstrip()
        arr = line.split(u'		')
        dict[arr[0][:-1]] = arr[1:]
        i = 0
        for stemset in dict[arr[0][:-1]]:
            dict[arr[0][:-1]][i] = stemset.split(u'	')
            i += 1
    return dict


def open_paradigms():
    f = codecs.open(u'сущфлексии.txt', u'r', u'utf-8')
    a = f.read()
    a = a.split(u'-paradigm: ')
    dict = {}
    for i in a:
        dict = inside_paradigm(i, dict)
    return dict

def inside_paradigm(i, dict):
    c_dic = {}
    byline = i.split(u'\r\n')
    for j in range(len(byline)):
        # print byline[j]
        if j % 2 != 0 or j == 0:
            continue
        # print j, u'мы внутри парадигмы', byline[j]
        content = byline[j-1][8:].split(u'//')
        c_dic[byline[j][9:]] = content
    if byline[0] == u'':
        return dict
    dict[byline[0]] = c_dic
    return dict



def kleit(stems, paradigms):
    eow = {}
    for paradigm in paradigms:
        # print paradigm
        stemy = stems[paradigm]
        for grammema in paradigms[paradigm]:
            for inflextion in range(len(paradigms[paradigm][grammema])):
                for stemset in stemy:
                    paradigms[paradigm][grammema][inflextion] = re.sub(u'(<[01234]>\.)([йцукенгшщзхъфывапролджэячсмитьбю]+?)$', u'\\1&(\\2)', paradigms[paradigm][grammema][inflextion])
                    for i in range(len(stemset)):
                        paradigms[paradigm][grammema][inflextion] = paradigms[paradigm][grammema][inflextion].replace(u'<' + str(i) + u'>', stemset[i])
                        paradigms[paradigm][grammema][inflextion] = paradigms[paradigm][grammema][inflextion].replace(u'..', u'&')
                        paradigms[paradigm][grammema][inflextion] = paradigms[paradigm][grammema][inflextion].replace(u'&&', u'&')
                        paradigms[paradigm][grammema][inflextion] = paradigms[paradigm][grammema][inflextion].replace(u'.&', u'&')
                        # print paradigms[paradigm][grammema][inflextion], u'amp should be here'
        eow[paradigm] = paradigms[paradigm]
    return eow

def phonology(text, letter, letter2):
    if u'@' in text:
        if letter == u'г':
            # print u'prepalatalization', text, letter
            text = text.replace(u'\\1@', u'з')
            text = text.replace(u'\\1#', u'ж')
            # print u'palatalization', text, letter, letter2
        if letter == u'х':
            text = text.replace(u'\\1@', u'с')
            text = text.replace(u'\\1#', u'ш')
        if letter == u'к':
            text = text.replace(u'\\1@', u'ц')
            text = text.replace(u'\\1#', u'ч')
    text = text.replace(u'\\1', letter)
    text = text.replace(u'\\2', letter2)
    return text

def letter_search(where, what, letter = u'', letter2 = u''):
    lett = re.search(what, where)
    try:
        letter = lett.group(1)
        # print letter, paradigm
        try:
            letter2 = lett.group(2)
            # print letter2, paradigm
        except:
            pass
    except:
        pass
    return letter, letter2

def getstem(word, endofword, test):
    s = re.search(endofword + u'$', word)
    i = 1
    while True:
        try:
            inflex = s.group(i)
            i += 1
        except:
            break
    # print s.group(), u'inflexion'
    infl = len(inflex)
    stem = word[:-infl]
    # print word, endofword, stem
    if test == 1:
        print u'gotstem', stem, inflex, endofword
    return stem


def getst_n(inflextion):
    s = re.search(u'<([012345])>', inflextion)
    try:
        a = s.group(1)
    except:
        print inflextion
    return int(a)


def addstem(form, paradigm, end_i, stemresult, paradigms, eow, testdict, test):
                    stem = getstem(testdict[form], eow[paradigm][form][end_i], test, )
                    st_n = getst_n(paradigms[paradigm][form][end_i])
                    try:
                        stemresult[paradigm][int(st_n)] = stemresult[paradigm][int(st_n)].union({stem})
                    except:
                        stemresult[paradigm][int(st_n)] = {stem}
                    if test == 1:
                        print list(stemresult[paradigm][int(st_n)])[0], u'what do we have here?'
                    return stemresult


def alternation(eow, paradigm, form, end_i, testdict):
    form_no_amp = eow[paradigm][form][end_i].replace(u'&', u'')
    sgnom_no_amp = eow[paradigm][u'sg,nom'][0].replace(u'&', u'')
    return good_alternation(form_no_amp, testdict[u'sg,nom'], sgnom_no_amp)
    return eow[paradigm][form][end_i]


def good_alternation(ending, nomsgform, nomsgending, test=0, first=0):
    if u'\\' in ending:
        if first == 0:
            letter, letter2 = letter_search(nomsgform, nomsgending + u'$')
        else:
            s2 = re.search(nomsgending + u'$', nomsgform)
            letter = s2.group(0)
            letter2 = u''
        if test == 1:
            print letter, letter2, u'letters'
        ending = phonology(ending, letter, letter2)
    elif first == 1:
        print u'NomSg inflex: ', nomsgending, u' NomSg form: ', nomsgform
        s = re.search(nomsgending + u'$', nomsgform)
        return s.group(0)
    return ending


def guess(eow, testdict, paradigms, test=0):
    testresult = {}
    stemresult = {}
    for paradigm in eow:
        stemresult[paradigm] = {}
        # letter, letter2 = letter_search(testdict[u'sg,nom'], eow[paradigm][u'sg,nom'][0] + u'$')
        for form in testdict:
            for end_i in range(len(eow[paradigm][form])):
                eow[paradigm][form][end_i] = alternation(eow, paradigm, form, end_i, testdict)
                if re.search(eow[paradigm][form][end_i] + u'$', testdict[form]):

                    stemresult = addstem(form, paradigm, end_i, stemresult, paradigms, eow, testdict, test)

                    try:
                        testresult[form] = testresult[form].union({paradigm})
                        # print u'успешно добавил', paradigm, testresult[form]
                    except:
                        testresult[form] = {paradigm}
                        # print type(testresult[form]), testresult[form]
    return testresult, stemresult


def res_no_stems(testresult):
    setresult = testresult[u'sg,nom']
    for j in testresult:
        print j, testresult[j]
        setresult = setresult & testresult[j]
    return setresult


def check_stems(stems, stemdescr):
    stemdescr = stemdescr[0]
    for i in range(len(stemdescr)):
            if i in stems:
                stemdescr[i] = stemdescr[i][:-1]
                # print u'before altern', stemdescr[i]
                print u'NomSg form -- ', list(stems[0])[0]
                stemdescr[i] = good_alternation(stemdescr[i], list(stems[0])[0], stemdescr[0], first=1, test=1)
                # print u'after altern', stemdescr[i]
                stemdescr[i] = u'(' + stemdescr[i] + u')'
                s = re.search(stemdescr[i] + u'$', list(stems[i])[0])
                try:
                    old_eos = s.group()
                except:
                    print stemdescr[i], list(stems[i])[0], u'error 1'
                for j in stems[i]:
                    s = re.search(stemdescr[i] + u'$', j)
                    try:
                        eos = s.group()
                        # print eos, u'eos'
                    except:
                        return False
                        print j, stemdescr[i], u'error'
                    if eos != old_eos:
                        return False
                    old_eos = eos
    return True

def to_check_stems(paradigm, stems, stemdescr):
    stem = stems[paradigm]
    print list(stem[0])[0], u'is is Nom sg?'
    descr = stemdescr[paradigm]
    info = check_stems(stem, descr)
    return info




paradigms = open_paradigms()



realparadigms = open_paradigms()

stems = open_stems()
eow = kleit(stems, paradigms)

'''for key in eow:
    print key, eow[key]
    for key2 in eow[key]:
        print key2, eow[key][key2]
        for key3 in eow[key][key2]:
            print key3'''

testdict = {u'sg,nom': u'коло', u'sg,gen': u'колесемъ', u'du,ins': u'колесема'}
# testdict = {u'sg,nom': u'другъ', u'sg,gen': u'друга', u'pl,nom': u'друзи'}

testresult, stemresult = guess(eow, testdict, realparadigms, test=1)
setresult = res_no_stems(testresult)

for paradigm in setresult:
    print paradigm, stemresult[paradigm], u'result paradigm + stem'
    print list(stemresult[paradigm][0])[0], u'looking for nom sg'
    print to_check_stems(paradigm, stemresult, stems)


print setresult, u'FINAL!'
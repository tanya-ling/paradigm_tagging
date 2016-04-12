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
        c_dic[byline[j][9:]] = byline[j-1][8:]
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
            for stemset in stemy:
                # print paradigms[paradigm][grammema], u'1'
                paradigms[paradigm][grammema] = re.sub(u'(<[01234]>\.)(.+?)/', u'\\1(\\2)', paradigms[paradigm][grammema])
                # print paradigms[paradigm][grammema], u'2'
                paradigms[paradigm][grammema] = re.sub(u'(<[01234]>\.)([йцукенгшщзхъфывапролджэячсмитьбю]+?)$', u'\\1(\\2)', paradigms[paradigm][grammema])
                for i in range(len(stemset)):
                    paradigms[paradigm][grammema] = paradigms[paradigm][grammema].replace(u'<' + str(i) + u'>', stemset[i])
                    paradigms[paradigm][grammema] = paradigms[paradigm][grammema].replace(u'..', u'')
                if u'/' in paradigms[paradigm][grammema]:
                        array = paradigms[paradigm][grammema].split(u'/')
                        for i in range(len(array)):
                            array[i] = u'(?:' + array[i] + u')'
                        paradigms[paradigm][grammema] = u'$|'.join(array)
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

def getstem(word, endofword, inflexion):
    pass

def guess(eow, testdict, paradigms):
    testresult = {}
    for paradigm in eow:
        letter, letter2 = letter_search(testdict[u'sg,nom'], eow[paradigm][u'sg,nom'] + u'$')
        for form in testdict:
            if u'\\' in eow[paradigm][form]:
                eow[paradigm][form] = phonology(eow[paradigm][form], letter, letter2)
            if re.search(eow[paradigm][form] + u'$', testdict[form]):
                print paradigm, form, testdict[form], eow[paradigm][form]
                inflexions = paradigms[paradigm][form]
                print inflexions, u'inflexions', paradigm, form
                inflexions = re.sub(u'<[01234]+?>', u'', inflexions)
                inflexions = inflexions.split(u'//')
                for flex in inflexions:
                    print u'flex!', flex
                    if re.search(flex + u'$', testdict[form]):
                        s = re.search(u'(.+)(' + flex + u'$)', testdict[form])
                        stem = s.group(1)
                        print stem, u'stem!'

                # stem = getstem(testdict[form], eow[paradigm][form], s.group(2))
                try:
                    testresult[form] = testresult[form].union({paradigm})
                    # print u'успешно добавил', paradigm, testresult[form]
                except:
                    testresult[form] = {paradigm}
                    # print type(testresult[form]), testresult[form]
    return testresult

def res_no_stems(testresult):
    setresult = testresult[u'sg,nom']
    for j in testresult:
        print j, testresult[j]
        setresult = setresult & testresult[j]
    return setresult

def check_stems(endings, testdict, stems):
    for form in testdict:
        pass



paradigms = open_paradigms()
realparadigms = open_paradigms()

stems = open_stems()
eow = kleit(stems, paradigms)

'''for key in eow:
    print key, eow[key]
    for key2 in eow[key]:
        print key2, eow[key][key2]'''

testdict = {u'sg,nom': u'коло', u'sg,gen': u'колесемъ', u'du,ins': u'колесема'}
testdict = {u'sg,nom': u'другъ', u'sg,gen': u'друга', u'pl,nom': u'друзи'}

testresult = guess(eow, testdict, realparadigms)
setresult = res_no_stems(testresult)



print setresult, u'FINAL!'
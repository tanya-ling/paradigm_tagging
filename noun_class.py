#-*- coding: utf-8 -*-
import re
import codecs

class word:
    def __init__(self):
        self.examples = []
        self.lemma = u''
        self.pos = u''
        self.gramm = u''
        self.par_stem = []
        self.modern = u''
        self.torot_id = u''
        self.id = u''
        self.par_name_list = []
        self.group_par_stem = {}

    def guess(self, analy_data):
        par_set = u'firsttime'
        for ex in self.examples:
            ex.guess_example(analy_data)
            # print u'in guess, guessed forms for one example ', ex.par_stem
            if par_set == u'firsttime':
                par_set = set(ex.par_stem)
            par_set = par_set & set(ex.par_stem)
        self.par_name_list = list(par_set)
        for par_name in self.par_name_list:
            # print u'getting stems for', par_name
            for ex in self.examples:
                good_p_s = ex.par_name_dict[par_name]
                self.par_stem.append(good_p_s)

    def group_stems(self):
        for par_stem in self.par_stem:
            for whateveritis in par_stem:
                if whateveritis.par.name not in self.group_par_stem:
                    self.group_par_stem[whateveritis.par.name] = [set() for i in xrange(whateveritis.par.num_of_stems)]
                # print self.group_par_stem[whateveritis.par.name], whateveritis.stem.number, whateveritis.par.num_of_stems
                self.group_par_stem[whateveritis.par.name][whateveritis.stem.number] = self.group_par_stem[whateveritis.par.name][whateveritis.stem.number] | set([whateveritis.stem.stem_form])


class example:
    def __init__(self):
        self.form = []
        self.form_norm = []
        self.analys = u''
        self.par_stem = []
        self.par_name_list = []
        self.par_name_dict = {}

    def guess_example(self, analy_data):
        # print u'analys', self.analys
        grammema = analy_data[self.analys]
        wordform_par_set = u'firsttime'
        # print u'form_norm class', type(self.form_norm[0])
        for form_n in self.form_norm:
            # print u'form_n', form_n.form
            form_par = form_n.guess_wordform(grammema)
            # print u'in guess example, guessed forms for one normal form', form_par
            form_n.par_stem = form_par
            if wordform_par_set == u'firsttime':
                wordform_par_set = set(form_par)
                # print u'in guess example first set', wordform_par_set
            wordform_par_set = wordform_par_set & set(form_n.par_stem)
        self.par_name_list = list(wordform_par_set)
        for par_name in self.par_name_list:
            for form_n in self.form_norm:
                good_p_s = form_n.par_name_dict[par_name]
                self.par_stem.append(good_p_s)
                if par_name in self.par_name_dict:
                    self.par_name_dict[par_name].append(good_p_s)
                else:
                    self.par_name_dict[par_name] = [good_p_s]
        self.par_stem = list(wordform_par_set)
        return self.par_name_list



class form_norm:
    def __init__(self):
        self.form = u''
        self.par_stem = []
        self.par_name_list = []
        self.par_name_dict = {}
    def guess_wordform(self, grammema):
        for p_i_m in grammema.par_infl_mod:
            for infl_form in p_i_m.infl:
                ishod = infl_form.st_mod + infl_form.gram_form
                # print u'ishod:', ishod, p_i_m.par.name, self.form
                if re.search(ishod + u'&', self.form + u'&'):
                    # print u'найдено совпадение на уровне примера', p_i_m.par.name, ishod, grammema.an_name, self.form
                    new_par_stem = par_stem()
                    new_par_stem.par = p_i_m.par
                    new_par_stem.infl = infl_form.gram_form
                    new_par_stem.ishod = ishod
                    new_par_stem.stem = stem()
                    if len(infl_form.gram_form) != 0:
                        new_par_stem.stem.stem_form = self.form[:-len(infl_form.gram_form)]
                    else:
                        new_par_stem.stem.stem_form = self.form
                    new_par_stem.stem.number = infl_form.st_num
                    self.par_stem.append(new_par_stem)
                    self.par_name_list.append(new_par_stem.par.name)
                    if new_par_stem.par.name in self.par_name_dict:
                        print self.par_name_dict[new_par_stem.par.name], u'два матча на одну парадигму в конкретном примере, в основу запишется позднейщий'
                    else:
                        self.par_name_dict[new_par_stem.par.name] = new_par_stem
                        # print new_par_stem.stem.stem_form, u'это основа для', new_par_stem.par.name
                        # print self.par_name_dict[new_par_stem.par.name], u'checking rint', new_par_stem.par.name
        return self.par_name_list


class par_stem:
    def __init__(self):
        self.par = u''
        self.stem = u''
        self.infl = u''
        self.ishod = u''

# class par_stems:
#     def __init__(self):
#         self.paradigm = paradigm()
#         self.stems = []


class paradigm:
    def __init__(self):
        self.name = u''
        self.num_of_stems = u''
        self.inflexions = []
        self.stem_model = []

class stem:
    def __init__(self):
        self.number = u''
        self.model = u''  # ???
        self.stem_form = u''
        self.exp_form = u''  # ???

class inflexion:
    def __init__(self):
        self.name = u''
        self.grammema = grammema()

class grammema():
    def __init__(self):
        self.gram_form = u''
        self.st_mod = u''
        self.st_num = u''

class analysis:
    def __init__(self):
        self.an_name = u''
        self.par_infl_mod = []

class par_infl_mod:
    def __init__(self):
        self.par = u''
        self.infl = []
        self.model = []

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

def parad_from_file():
    paradigmy = []
    paradigms = open_paradigms()
    parad_dict = {}
    stems = open_stems()
    for j in paradigms:
        nos = 1
        apar = paradigm()
        apar.name = j
        apar.stem_model = stems[j][0]
        for i in paradigms[j]:
            infl = inflexion()
            infl.name = i
            infl.grammema = paradigms[j][i]
            for infl_form in infl.grammema:
                if u'3' in infl_form:
                    nos = 4
                elif u'2' in infl_form and nos < 4:
                    nos = 3
                elif u'1' in infl_form and nos < 3:
                    nos = 2
            apar.inflexions.append(infl)
        apar.num_of_stems = nos
        # print apar.name, u'nos -- ', apar.num_of_stems
        paradigmy.append(apar)
        parad_dict[apar.name] = apar
    return parad_dict
    return paradigmy

def open_stems():
    filename = u'описание основ сущ_lite.txt'
    f = codecs.open(filename, u'r', u'utf-8')
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

def analysis_data(paradigmy):
    anal_data = {}
    for par_name in paradigmy:
        for infl in paradigmy[par_name].inflexions:
            if infl.name not in anal_data:
                anal_data[infl.name] = analysis()
                anal_data[infl.name].an_name = infl.name
            new_par_gram = par_infl_mod()
            new_par_gram.par = paradigmy[par_name]
            new_par_gram.infl = []
            for flex in infl.grammema:
                new_grammema = grammema()
                new_grammema.gram_form = re.sub(u'<[012]>\.', u'', flex)
                if u'<0>' in flex:
                    new_grammema.st_mod = paradigmy[par_name].stem_model[0][:-1]
                    new_grammema.st_num = 0
                elif u'<1>' in flex:
                    try:
                        new_grammema.st_mod = paradigmy[par_name].stem_model[1][:-1]
                        new_grammema.st_num = 1
                    except:
                        print u'no stem 1: ', paradigmy[par_name].name, flex
                elif u'<2>' in flex:
                    try:
                        new_grammema.st_mod = paradigmy[par_name].stem_model[2][:-1]
                        new_grammema.st_num = 2
                    except:
                        print u'no stem 2: ', paradigmy[par_name].name, flex
                elif u'<3>' in flex:
                    try:
                        new_grammema.st_mod = paradigmy[par_name].stem_model[3][:-1]
                        new_grammema.st_num = 3
                    except:
                        print u'no stem 3: ', paradigmy[par_name].name, flex
                else:
                    print u'mistake in stems description', flex, par_name, infl.name
                new_par_gram.infl.append(new_grammema)
            # new_par_gram.model = paradigmy[par_name].stem_model
            anal_data[infl.name].par_infl_mod.append(new_par_gram)
    return anal_data


# нормализация орфографии
def sochet(word):
    word = word.lower()
    word2 = word.replace(u'оу', u'у')
    word2 = word2.replace(u'жы', u'жи')
    word2 = word2.replace(u'шы', u'ши')
    word2 = word2.replace(u'щы', u'щи')
    word2 = word2.replace(u'чы', u'чи')
    word2 = word2.replace(u'жю', u'жу')
    word2 = word2.replace(u'шю', u'шу')
    word2 = word2.replace(u'щю', u'щу')
    word2 = word2.replace(u'чю', u'чу')
    # ! 09.12 by manuscript
    word2 = word2.replace(u'сч', u'щ')
    word2 = word2.replace(u'жч', u'щ')
    word2 = word2.replace(u'дч', u'дш')
    word2 = word2.replace(u'дщ', u'дш')
    # ! 09.12 agso
    word2 = re.sub(u'([уеыаоэяию])(у)', u'\\1ю', word2)
    word2 = re.sub(u'([уеыаоэяию])(а)', u'\\1я', word2)
    #  word2 = re.sub(u'([уеыаоэяию])(о)', u'\\1ё', word2) #  это делает симеёна
    word2 = re.sub(u'([уеыаоэяию])(э)', u'\\1е', word2)
    # ! 09.12 ts delete from paradigms
    # word2 = word2.replace(u'тс', u'ц') # пока убираем, потом нужно добавить, и в словаре
    # word2 = word2.replace(u'тц', u'ц')
    word2 = word2.replace(u'щъ', u'щь')
    return word2

def letterchange(word):
    newword = word
    newword = newword.replace(u'i', u'и')
    newword = newword.replace(u'і', u'и')
    newword = newword.replace(u'ї', u'и')
    newword = newword.replace(u'ï', u'и')
    newword = newword.replace(u'ꙇ', u'и')
    newword = newword.replace(u'ѡ', u'о')
    newword = newword.replace(u'є', u'e')
    newword = newword.replace(u'́', u'')
    newword = newword.replace(u'҃', u'')
    newword = newword.replace(u'ѿ', u'от')
    newword = newword.replace(u'꙽', u'')
    newword = newword.replace(u'ѵ', u'и')
    newword = newword.replace(u'̂', u'')
    newword = newword.replace(u'ѻ', u'о')
    newword = newword.replace(u'ѳ', u'ф')
    newword = newword.replace(u'ѯ', u'кс')
    newword = newword.replace(u'ѱ', u'пс')
    newword = newword.replace(u'ѕ', u'з')
    newword = newword.replace(u'ꙋ', u'у')
    newword = newword.replace(u'ꙗ', u'я')
    newword = newword.replace(u'ѧ', u'я')
    newword = newword.replace(u'ѹ', u'у')
    return newword

def inter_new(word):
    newword = re.sub(u'([цкнгшщзхфвпрлджчсмтб])(ь|ъ)([цкнгшщзхфвпрлджчсмтб])', u'\\1\\3', word)
    return newword

def commonform(word):
    word = letterchange(word)
    # print word
    word = inter_new(word)
    word = sochet(word)
    # print word
    # print word
    word = begend_new(word)
    return word

def begend_new(word):
    word += u'8'
    if re.search(u'[кнгзхфвпрлдсмтб]8', word):
        word = word[:-1]
        word += u'ъ'
    else:
        word = word[:-1]
        # print u'begend_new'
    return word


paradigmy = parad_from_file()
anal_data = analysis_data(paradigmy)

# for grammema in anal_data:
#     print grammema
#     print anal_data[grammema].an_name
#     for p_i_m in anal_data[grammema].par_infl_mod:
#         print p_i_m.par.name
#         for i in p_i_m.infl:
#             print i.gram_form
#             print i.st_mod
#             print i.st_num

# for apar in paradigmy:
#     print apar, u'parad'
#     print paradigmy[apar].name
#     print paradigmy[apar].stem_model, u'stemmodel'
#     for infl in paradigmy[apar].inflexions:
#         print infl.name
#         print infl.grammema

testdict = {u'sg,nom': [u'коло'], u'sg,ins': [u'колесемъ', u'колесем'], u'du,ins': [u'колесема']}
testdict = {u'sg,nom': [u'другъ'], u'sg,gen': [u'друга'], u'pl,nom': [u'друзи', u'дгузи']}
kolo = word()
kolo.lemma = u'коло'
kolo.id = 1
for key in testdict:
    new_ex = example()
    new_ex.analys = key
    new_ex.form = testdict[key]
    common_wf = []
    for wordform in new_ex.form:
        wordform_norm = commonform(wordform)
        if wordform_norm not in common_wf:
            new_ex_form_norm = form_norm()
            new_ex_form_norm.form = wordform_norm
            common_wf.append(wordform_norm)
            new_ex.form_norm.append(new_ex_form_norm)
    kolo.examples.append(new_ex)

# for ex in kolo.examples:
#     print ex.analys
#     for rorm in ex.form:
#         print rorm
#     for rorm in ex.form_norm:
#         print rorm

kolo.guess(anal_data)
for p_s in kolo.par_stem:
    for item in p_s:
        print item.par.name, item.stem.stem_form, item.stem.number

kolo.group_stems()
for par_name in kolo.group_par_stem:
    print par_name, kolo.group_par_stem[par_name]
    for stem_forms in kolo.group_par_stem[par_name]:
        for form in stem_forms:
            print form
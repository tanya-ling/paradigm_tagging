#-*- coding: utf-8 -*-
import re
import codecs
import math
from hawlik_low import oslo_trans
from sys import path

path.append(u'C:\Tanya\НИУ ВШЭ\двевн курсач\приведение словаря\poliakov-to-uniparser')
import total_new_dict_1903


class word:
    def __init__(self):
        self.examples = []
        self.lemma = u''
        self.simple_lemma = u''
        self.pos = u''
        self.gramm = u''
        self.par_stem = []
        self.modern = u''
        self.torot_id = u''
        self.id = u''
        self.par_name_list = []
        self.group_par_stem = {}
        self.predicted_par_stem = {}
        self.lemma_after_fall = u''
        self.weight_dict = {}
        self.score_dict = {}
        self.unan_examples = {}
        self.second_score_dict = {}
        self.rnc_id = []

    def create_examples(self, testdict):
        for key in testdict:
            new_ex = example()
            new_ex.analys = key
            new_ex.form = testdict[key]
            # print u'noun class line 28', new_ex.form, new_ex.analys
            common_wf = []
            for wordform in new_ex.form:
                wordform_norm = commonform(wordform)
                if wordform_norm not in common_wf:
                    new_ex_form_norm = form_norm()
                    new_ex_form_norm.form = wordform_norm
                    common_wf.append(wordform_norm)
                    new_ex.form_norm.append(new_ex_form_norm)
            self.examples.append(new_ex)

    def guess(self, analy_data):
        par_set = u'firsttime'
        for ex in self.examples:
            ex.guess_example(analy_data)
            # print u'            guessed forms for ', ex.analys, ex.par_stem
            if par_set == u'firsttime':
                par_set = set(ex.par_stem)
            par_set = par_set & set(ex.par_stem)
        self.par_name_list = list(par_set)
        self.get_stems()

    def get_p_s_if_no(self):
        looked_pars = []
        for example in self.examples:
            # print example.form[0], u'possible paradigms: ',example.par_stem
            for par_stem in example.par_stem:
                    if par_stem not in looked_pars:
                        looked_pars.append(par_stem)
                        for ex in self.examples:
                            for par_st in ex.par_stem:
                                if par_st == par_stem:
                                    # print example.par_name_dict[par_stem]
                                    example.par_name_dict[par_stem][0].weight += 1
                                    ex.par_name_dict[par_st][0].weight += 1
                                    # par_stem.weight += 1
                                    # par_st.weight = par_stem.weight
        if len(looked_pars) == 0:
            # print self.lemma, u'really nothing to guess?'
            return

        if self.pos == u'N':
            pos_max = 15  # real - 31
        elif self.pos == u'Adj':
            pos_max = 21  # real - 45
        elif self.pos == u'V':
            pos_max = 23  # real - 101
        else:
            print u'what a pos?', self.pos, self.lemma
            pos_max = 1

        max_score = 0
        second_best = []
        not_first = False
        for para in looked_pars:
            con = False
            for example in self.examples:
                if con:
                    continue
                for par_stem in example.par_stem:
                    if con:
                        continue
                    if par_stem == para:
                        # print par_stem
                        # print float(example.par_name_dict[par_stem][0].weight), float(len(self.examples))
                        # print float(example.par_name_dict[par_stem][0].weight) / float(len(self.examples))
                        # print math.log(1 + float(example.par_name_dict[par_stem][0].weight) / len(self.examples), 2)
                        measure = float(len(self.examples)) / pos_max * math.log(
                            1 + float(example.par_name_dict[par_stem][0].weight) / len(self.examples), 2)
                        if measure > 1:
                            measure = 1
                        example.par_name_dict[par_stem][0].weight_score = measure
                        self.score_dict[par_stem] = example.par_name_dict[par_stem][0].weight_score
                        # print u'par stem weight score', par_stem, example.par_name_dict[par_stem][0].weight, example.par_name_dict[par_stem][0].weight_score
                        if example.par_name_dict[par_stem][0].weight_score > max_score:
                            # print u'par stem best weight, weight-score', par_stem, example.par_name_dict[par_stem][0].weight, example.par_name_dict[par_stem][0].weight_score
                            if not_first and max_score > 0.1:
                                second_best.append(old_par_stem)
                                self.second_score_dict[old_par_stem] = max_score
                            max_score = example.par_name_dict[par_stem][0].weight_score
                            best_match = [par_stem]
                            old_par_stem = par_stem
                            con = True
                            self.weight_dict = {par_stem: max_score}
                            not_first = True
                        elif example.par_name_dict[par_stem][0].weight_score == max_score:
                            best_match.append(par_stem)
                            con = True
                            self.weight_dict[par_stem] = max_score
        self.par_name_list = best_match
        self.get_stems()

    def get_stems(self):
        for par_name in self.par_name_list:
            # print u'getting stems for', par_name
            for ex in self.examples:
                try:
                    good_p_s = ex.par_name_dict[par_name]
                    self.par_stem.append(good_p_s)
                except KeyError:
                    pass

    def predict_stems(self, rnc=False):
        lemma_to_work = self.lemma
        if rnc:
            lemma_to_work = self.simple_lemma
        for par_stem in self.group_par_stem:
            if self.pos == u'N' or self.pos == u'Adj' or self.pos == u'A-NUM':
                stem0 = total_new_dict_1903.osnnoun(self.lemma_after_fall, par_stem)
                if stem0 == u'delete_this_word':
                    self.predicted_par_stem[par_stem] = u'delete_this_word'
                    return
                stems = total_new_dict_1903.nounstem(par_stem, stem0)
                stem0_old = total_new_dict_1903.osnnoun(lemma_to_work, par_stem)
                if stem0_old == stem0:
                    if u'w' not in stems:
                        res_stems = stems.split(u'.|')
                        res_stems = [res_stems[i].split(u'.//') for i in xrange(len(res_stems))]
                    else:
                        res_stems = []
                    self.predicted_par_stem[par_stem] = res_stems
                    continue
                stems_old = total_new_dict_1903.nounstem(par_stem, stem0_old)
                # print u'stems old', stems_old
            if self.pos == u'V':
                    stem0 = total_new_dict_1903.osninf(self.lemma_after_fall, par_stem)
                    try:
                        stems, paradigm = total_new_dict_1903.verbstem(self.lemma_after_fall, par_stem, 1, 0)
                        if stems == u'delete_this':
                            stems = []
                            continue
                        if stems[-2:] == u'|.':  # очень тупой способ дебажки
                            stems = stems[:-2]
                    # except IndexError:
                    #     print self.lemma, stem0, par_stem, u'index error'
                    #     stems = []
                    except ValueError:
                        print self.lemma, stem0, par_stem, u'too many values to unpack'
                        stems = []
                    stem0_old = total_new_dict_1903.osninf(lemma_to_work, par_stem)
                    if stem0_old == stem0:  # не знаю, ускоряет или замедляет эта проверка, так как нулевая основа считается дважды
                        if u'w' not in stems:
                            stems = stems[:-1]
                            res_stems = stems.split(u'.|')
                            res_stems = [res_stems[i].split(u'.//') for i in xrange(len(res_stems))]
                        else:
                            res_stems = []
                        self.predicted_par_stem[par_stem] = res_stems
                        continue
                    stems_old, paradigm = total_new_dict_1903.verbstem(lemma_to_work, par_stem, 1, 0)
                    if stems_old[-2:] == u'|.':
                        stems_old = stems_old[:-2]
            # print par_stem, stems, u'and stems old', stems_old
            if u'w' in stems or u'w' in stems_old:
                res_stems = []
            else:
                if stems[-1] == u'.':
                    stems = stems[:-1]
                if stems_old[-1] == u'.':
                    stems_old = stems_old[:-1]
                # print self.id, stems, stems_old, u'asdf'
                stems = stems.split(u'.|')
                stems = [stems[i].split(u'.//') for i in xrange(len(stems))]
                stems_old = stems_old.split(u'.|')
                stems_old = [stems_old[i].split(u'.//') for i in xrange(len(stems_old))]
                res_stems = [None for i in xrange(len(stems))]
                for i in xrange(len(stems)):
                    try:
                                if stems[i] == stems_old[i]:
                                    res_stems[i] = [stems[i]]
                                else:
                                    listmerge6 = lambda s: reduce(lambda d, el: d.extend(el) or d, s, [])  # MAGIC
                                    res_stems[i] = listmerge6([stems[i], stems_old[i]])
                    except IndexError:
                        print u'len of old and new stems is different', self.lemma, self.lemma_after_fall, par_stem
                        res_stems = stems
            self.predicted_par_stem[par_stem] = res_stems

    def group_stems(self):
        if len(self.par_stem) == 0:
            # print u'не нашли точного совпадения', self.lemma  # ну уж совсем нестрогий вариант
            self.get_p_s_if_no()
        todel = []
        for par_stem in self.par_stem:
            for whateveritis in par_stem:
                if whateveritis.par.name not in self.group_par_stem:
                    self.group_par_stem[whateveritis.par.name] = [[] for i in xrange(whateveritis.par.num_of_stems)]
                # print self.group_par_stem[whateveritis.par.name], whateveritis.stem.number, whateveritis.par.num_of_stems
                self.group_par_stem[whateveritis.par.name][whateveritis.stem.number] = list(set(self.group_par_stem[whateveritis.par.name][whateveritis.stem.number]) | set([whateveritis.stem.stem_form.lower()]))

        for par_st in self.group_par_stem:
            i = 0
            if u'STAR' in par_st:
                for stemset in self.group_par_stem[par_st]:
                    if len(stemset) > 0:
                        i += 1
                if i > 1:
                    # print u'it must be a star, then better delete ', par_st[:-5]
                    todel.append(par_st[:-5])
            if self.pos == u'N':
                if u'4' in par_st:
                    if u'41' in par_st:
                        if self.gramm != u'f':
                            todel.append(par_st)
                    elif self.gramm != u'm':
                        todel.append(par_st)
                elif u'1' in par_st and self.gramm != u'm':
                    todel.append(par_st)
                elif u'2' in par_st and self.gramm != u'n':
                    todel.append(par_st)
                elif u'3' in par_st and self.gramm == u'n':
                    todel.append(par_st)
                elif u'6' in par_st and self.gramm != u'm':
                    todel.append(par_st)

        for par_name in todel:
            try:
                del self.group_par_stem[par_name]
            except:
                try:
                    del self.group_par_stem[u'N5ov']
                except:
                    print u'key error in group stems', par_name

    def change_score(self):
        for par_name in self.group_par_stem:
            # print u'change score', self.lemma, par_name
            if par_name in self.score_dict or par_name in self.second_score_dict:
                # print u'change_score 0', self.lemma, par_name
                self.change_concrete_score(par_name)
            else:
                if self.pos == u'N':
                    pos_max = 15  # real - 31
                elif self.pos == u'Adj' or self.pos == u'A-NUM':
                    pos_max = 21  # real - 45
                elif self.pos == u'V':
                    pos_max = 23  # real - 101
                measure = float(len(self.examples)) / pos_max
                if measure > 1:
                    measure = 1
                self.score_dict[par_name] = measure
                # print u'change score 0.5', self.lemma, par_name
                self.change_concrete_score(par_name)

    def change_concrete_score(self, par_name):
        real_stems = self.group_par_stem[par_name]
        if par_name not in self.predicted_par_stem:
            # print u'is it okey that nothing was predicted for ', self.lemma, par_name
            l.write(u'nothing was predicted for:\t' + self.lemma + u'\t' + par_name + u'\r\n')
            measure = 0.1
        elif self.predicted_par_stem[par_name] == []:
            if par_name != u'Viti':
                # print u'is it okey that nothing was predicted for ', self.lemma, par_name
                l.write(u'nothing was predicted for:\t' + self.lemma + u'\t' + par_name + u'\r\n')
            measure = 0.1
        else:
            predicted_stems = self.predicted_par_stem[par_name]
            if len(predicted_stems) != len(real_stems):
                if par_name == u'Vdat':
                    self.group_par_stem[par_name] = [self.group_par_stem[par_name][0]]  # очень тупой способ дебажки
                    real_stems = self.group_par_stem[par_name]
                    if real_stems[0][0] == predicted_stems[0][0]:
                        measure = 1
                    else:
                        measure = 0.05
                else:
                    # print u'predicted and real stems length is no equal', self.lemma, par_name, len(predicted_stems), predicted_stems[0][0], len(real_stems)
                    l.write(u'predicted (' + str(len(predicted_stems)) + ') and real (' + str(len(real_stems)) + ') stems length is no equal:\t' + self.lemma + u'\t' + par_name + u'\r\n')
                    measure = 0.1
            else:
                i = 0
                for stem_nummer in xrange(len(real_stems)):
                    found_predicted_stem = False
                    for stem in real_stems[stem_nummer]:
                        if stem in predicted_stems[stem_nummer]:
                            found_predicted_stem = True
                    if found_predicted_stem:
                        i += 1
                if i != 0:
                    measure = float(i) / float(len(real_stems))
                else:
                    measure = 0.05
        # print self.lemma, par_name, measure, i, len(real_stems), u'in change_concrete_score'
        self.score_dict[par_name] = self.score_dict[par_name] * measure


    def print_par_stem(self):
        print self.id, self.lemma, self.gramm, u'in print_par_stem'
        for par_name in self.group_par_stem:
            print par_name, self.group_par_stem[par_name]
            for stem_forms in self.group_par_stem[par_name]:
                for form in stem_forms:
                    print form

    def write_guessed_to_file_short(self, rnc=False):
        uninfl = False
        wtw = {u'id': self.id, u'torot_id': self.torot_id, u'pos': self.pos, u'lemma': self.lemma}
        wtw[u'lemma_new'] = self.lemma_after_fall
        wtw[u'unanalysed_examples'] = self.unan_examples
        if rnc:
            wtw[u'unanalysed_examples'] = {}
            for annot in self.unan_examples:
                listmerge6 = lambda s: reduce(lambda d, el: d.extend(el) or d, s, [])  # MAGIC
                res = listmerge6(self.unan_examples[annot])
                wtw[u'unanalysed_examples'][annot] = list(set(res))
        if uninfl:
            return wtw
        if self.pos == u'N':
            wtw[u'gender'] = self.gramm
        wtw[u'examples'] = [{ex.analys: ex.form} for ex in self.examples]
        if rnc:
            wtw[u'examples'] = [{ex.analys: list(set(ex.form))} for ex in self.examples]
        return wtw

    def write_guessed_to_file(self, rnc=False):
        if self.id == '94307' or self.id == '185022':
            print 'test sample', self.lemma, self.examples, self.group_par_stem, self.gramm, self.par_stem
        uninfl = False
        if self.pos == u'N':
            pos_max = 15  # real - 31
        elif self.pos == u'Adj' or self.pos == u'A-NUM':
            pos_max = 21  # real - 45
        elif self.pos == u'V':
            pos_max = 23  # real - 101
        else:
            uninfl = True
        wtw = {u'id': self.id, u'torot_id': self.torot_id, u'pos': self.pos, u'lemma': self.lemma}
        wtw[u'lemma_new'] = self.lemma_after_fall
        wtw[u'unanalysed_examples'] = self.unan_examples
        if rnc:
            wtw[u'unanalysed_examples'] = {}
            for annot in self.unan_examples:
                listmerge6 = lambda s: reduce(lambda d, el: d.extend(el) or d, s, [])  # MAGIC
                res = listmerge6(self.unan_examples[annot])
                wtw[u'unanalysed_examples'][annot] = list(set(res))
        if uninfl:
            return wtw
        if self.pos == u'N':
            wtw[u'gender'] = self.gramm
        wtw[u'examples'] = [{ex.analys: ex.form} for ex in self.examples]
        if rnc:
            wtw[u'examples'] = [{ex.analys: list(set(ex.form))} for ex in self.examples]
        wtw[u'par_stem'] = self.group_par_stem
        wtw[u'predicted_stems'] = self.predicted_par_stem
        wtw[u'scores'] = {}
        for par_name in self.group_par_stem:
            if par_name in self.score_dict:
                wtw[u'scores'][par_name] = self.score_dict[par_name]
                for par_name2 in self.second_score_dict:  # тупо сделано и всё тормозит, по несколько раз добавляет
                    wtw[u'scores'][par_name2] = self.second_score_dict[par_name2]
            else:
                print u"I'll marry her anyway", par_name, self.lemma
                measure = float(len(self.examples))/pos_max
                if measure > 1:
                    measure = 1
                wtw[u'scores'][par_name] = measure
        return wtw

    def write_unguessed_to_file(self):
        if self.id == '94307' or self.id == '185022':
            print 'test sample', self.lemma, self.examples, self.group_par_stem, self.gramm, self.par_stem
        wtw = {u'id': self.id, u'torot_id': self.torot_id, u'pos': self.pos, u'gender': self.gramm, u'lemma': self.lemma}
        wtw[u'lemma_new'] = self.lemma_after_fall
        wtw[u'examples'] = [{ex.analys: ex.form, u'paradigms': ex.par_name_list} for ex in self.examples]
        return wtw


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
        try:
            grammema = analy_data[self.analys]
        except KeyError:
            print u'key error in guess example', self.analys, self.form[0]
            return []
        wordform_par_set = u'firsttime'
        for form_n in self.form_norm:
            # print u'form_n', form_n.form
            form_par = form_n.guess_wordform(grammema)
            # print u'guessed forms for ', form_n.form, form_par
            form_n.par_stem = form_par
            if wordform_par_set == u'firsttime':
                wordform_par_set = set(form_par)
                # print u'in guess example first set', wordform_par_set
            wordform_par_set = wordform_par_set | set(form_n.par_stem)  # нестрогий вариант
            # wordform_par_set = wordform_par_set & set(form_n.par_stem)  # строгий вариант
        self.par_name_list = list(wordform_par_set)
        for par_name in self.par_name_list:
            for form_n in self.form_norm:
                try:
                    good_p_s = form_n.par_name_dict[par_name]
                    self.par_stem.append(good_p_s)
                    if par_name in self.par_name_dict:
                        self.par_name_dict[par_name].append(good_p_s)
                    else:
                        self.par_name_dict[par_name] = [good_p_s]
                except:
                    # попадаем сюда при выполнении "нестрогого" варианта для тех разборов,
                    # которые есть не у всех norm form.
                    # Наверное, в таком случае нам не нужны основы.
                    pass
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
                        pass
                        # print new_par_stem.par.name, new_par_stem.stem.stem_form, self.form, u'два матча на одну парадигму в конкретном примере, в основу запишется первый'
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
        self.weight = 0
        self.weight_score = 0

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
        self.classic_index = u''

    def classic_indexing(self):
        if u'N1' in self.name:
            self.classic_index = u'o'
        if u'N2' in self.name:
            self.classic_index = u'o'
        if u'N3' in self.name:
            self.classic_index = u'a'
        if u'N4' in self.name:
            self.classic_index = u'i'
        if u'N5' in self.name:
            self.classic_index = u'u-long'
        if u'N6' in self.name:
            self.classic_index = u'u-short'

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

    def num_of_stems(self, nos, paradigma, flex):
        try:
            self.st_mod = paradigma.stem_model[nos][:-1]
            self.st_num = nos
        except:
            print u'no stem ' + str(nos) + u': ', paradigma.name, flex


class analysis:
    def __init__(self):
        self.an_name = u''
        self.par_infl_mod = []


class par_infl_mod:
    def __init__(self):
        self.par = u''
        self.infl = []
        self.model = []

def open_paradigms(filen):
    f = codecs.open(filen, u'r', u'utf-8')
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
        for index in range(len(content)):
            content[index].replace(u'й', u'и')  # с replace это довольно спорный шаг
        c_dic[byline[j][9:]] = content
    if byline[0] == u'':
        return dict
    dict[byline[0]] = c_dic
    return dict

def parad_from_file(filen, filename):
    paradigmy = []
    paradigms = open_paradigms(filen)
    parad_dict = {}
    stems = open_stems(filename)
    for j in paradigms:
        nos = 1
        apar = paradigm()
        apar.name = j
        apar.classic_indexing()
        # print stems, u'line 363'
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

def open_stems(filename):
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
                new_grammema.num_of_stems(int(flex[1]), paradigmy[par_name], flex)
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
    word2 = word2.replace(u'кы', u'ки')
    # word2 = word2.replace(u'гы', u'ги')  # чтобы не пороть другый, но вообще решение нужно
    word2 = word2.replace(u'хы', u'хи')
    word2 = word2.replace(u'чы', u'чи')
    word2 = word2.replace(u'жю', u'жу')
    word2 = word2.replace(u'шю', u'шу')
    word2 = word2.replace(u'щю', u'щу')
    word2 = word2.replace(u'чю', u'чу')
    # ! 09.12 by manuscript
    # word2 = word2.replace(u'сч', u'щ')  #  не нравится мне это для этой программы
    # word2 = word2.replace(u'жч', u'щ')  #  не нравится мне это для этой программы
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
    newword = newword.replace(u'ʼ', u'')
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
    newword = newword.replace(u'ѳ', u'ф')
    newword = newword.replace(u'ꙑ', u'ы')
    newword = newword.replace(u'ꙑ', u'ы')
    return newword

def inter_new(word):
    newword = re.sub(u'([цкнгшщзхфвпрлджчсмтб])(ь|ъ)([цкнгшщзхфвпрлджчсмтб])', u'\\1\\3', word)
    return newword

def commonform(word):
    word = letterchange(word)
    # print word
    # word = inter_new(word)  # от этого нужно отказаться, иначе невозможно выделить основы до падения редуцированных
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

l = codecs.open(u'error_log.txt', 'w', 'utf-8')
# paradigmy = parad_from_file(u'сущфлексии.txt')
# paradigmy = parad_from_file(u'прилфлексии.txt')
# anal_data = analysis_data(paradigmy)

# for grammema in anal_data:
#     print grammema, u'grammema'
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

# testdict = {u'sg,nom': [u'коло'], u'sg,ins': [u'колесемъ', u'колесем'], u'du,ins': [u'колесема']}
# # testdict = {u'sg,nom': [u'другъ'], u'sg,gen': [u'друга'], u'pl,nom': [u'други', u'дгузи']}
# testdict = {u'pl,f,nom': [u'храбрыя'], u'pl,m,nom,brev': [u'храбри', u'храбры'], u'sg,m,nom,brev': [u'храбръ']}
# kolo = word()
# kolo.lemma = u'коло'
# kolo.id = 666
# kolo.create_examples(testdict)
#
#
# # for ex in kolo.examples:
# #     print ex.analys
# #     for rorm in ex.form:
# #         print rorm
# #     for rorm in ex.form_norm:
# #         print rorm
#
# kolo.guess(anal_data)
# for p_s in kolo.par_stem:
#     for item in p_s:
#         print item.par.name, item.stem.stem_form, item.stem.number
#
# kolo.group_stems()
#
# kolo.print_par_stem()
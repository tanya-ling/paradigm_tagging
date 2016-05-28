#-*- coding: utf-8 -*-

import codecs
import json
import random

t = codecs.open(u'torot_gram_7.json', u'r', u'utf-8')
tf = json.load(t)
#
n = codecs.open(u'rnc_gram_2.json', u'r', u'utf-8')
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

# p_tagging(nf)

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

j = codecs.open(u'СЛОВАРЬ.json', u'r', u'utf-8')
jf = json.load(j)

def drei_tagging():
    while i < 100:
        r_i = random.choice(tf)
        if u'tor_lemma':
            pass

def f_measure_poliakov():
    has_all_three = 0
    has_all_three_infl = 0
    tor_tp, tor_tn, tor_fp, tor_fn = 0, 0, 0, 0
    nrc_tp, nrc_tn, nrc_fp, nrc_fn = 0, 0, 0, 0
    count = 0
    diclen = len(jf)
    for word in jf:
        count += 1
        if count % 300 == 0:
            print float(count)/diclen, u'done'
        pos = word['pos']
        if u'lemma' in word and u'tor_lemma' in word and u'up_lemma' in word:
            # тут есть выравнивание на вc`
            has_all_three += 1
            if pos == u'N' or pos == u'V' or pos == u'Adj':
                has_all_three_infl +=1
                real_paradigms = []
                for paradigm in word['up_stems']:
                    real_paradigms.append(paradigm)
                if u'tor_scores' in word and u'scores' in word:  # для обоих предсказали что-то
                    t_tp, t_tn, t_fp, t_fn = get_ts(real_paradigms, word['tor_scores'], pos)
                    n_tp, n_tn, n_fp, n_fn = get_ts(real_paradigms, word['scores'], pos)
                    tor_fn += t_fn
                    tor_fp += t_fp
                    tor_tn += t_tn
                    tor_tp += t_tp
                    nrc_fn += n_fn
                    nrc_fp += n_fp
                    nrc_tn += n_tn
                    nrc_tp += n_tp
                    continue
        if u'lemma' in word and u'up_lemma' in word:
            # торот + поляков или нкря + поляков выглядят одинаково
            if pos == u'N' or pos == u'V' or pos == u'Adj':
                pos = word['pos']
                real_paradigms = []
                for paradigm in word['up_stems']:
                    real_paradigms.append(paradigm)
                if u'tor_scores' in word:
                    t_tp, t_tn, t_fp, t_fn = get_ts(real_paradigms, word['tor_scores'], pos)
                    tor_fn += t_fn
                    tor_fp += t_fp
                    tor_tn += t_tn
                    tor_tp += t_tp
                elif u'scores' in word:
                    n_tp, n_tn, n_fp, n_fn = get_ts(real_paradigms, word['scores'], pos)
                    nrc_fn += n_fn
                    nrc_fp += n_fp
                    nrc_tn += n_tn
                    nrc_tp += n_tp
                else:
                    if pos == u'N':
                        total = 48
                    elif pos == u'V':
                        total = 54
                    elif pos == u'Adj':
                        total = 11
                    # ничего не предсказано для этого слова!
                    if u'tor_id' in word:
                        # оно было-таки торотовским
                        t_tn = total - len(word['up_stems'])
                        t_fn = len(word['up_stems'])
                        tor_fn += t_fn
                        tor_tn += t_tn
                    else:
                        n_tn = total - len(word['up_stems'])
                        n_fn = len(word['up_stems'])
                        nrc_fn += n_fn
                        nrc_tn += n_tn
    t_pres, t_recall, t_f_measure = f_measure(tor_tp, tor_tn, tor_fp, tor_fn)
    n_pres, n_recall, n_f_measure = f_measure(nrc_tp, nrc_tn, nrc_fp, nrc_fn)
    return t_pres, t_recall, t_f_measure, n_pres, n_recall, n_f_measure, has_all_three_infl, has_all_three


def f_measure_manual():
    n = codecs.open(u'for_manual.json', u'r', u'utf-8')
    nf = json.load(n)
    m = codecs.open(u'manual_answers.txt', u'r', u'utf-8')
    di = {}
    for line in m:
        line = line.rstrip().split(u'\t')
        di[line[0]] = [line[1]]
    tor_tp, tor_tn, tor_fp, tor_fn = 0, 0, 0, 0
    nrc_tp, nrc_tn, nrc_fp, nrc_fn = 0, 0, 0, 0
    for word in nf:
        if word['lemma'] in di:
                    real_paradigms = di[word['lemma']]
                    if u'tor_scores' in word and u'scores' in word:  # для обоих предсказали что-то
                        t_tp, t_tn, t_fp, t_fn = get_ts(real_paradigms, word['tor_scores'], u'N')
                        n_tp, n_tn, n_fp, n_fn = get_ts(real_paradigms, word['scores'], u'N')
                        tor_fn += t_fn
                        tor_fp += t_fp
                        tor_tn += t_tn
                        tor_tp += t_tp
                        nrc_fn += n_fn
                        nrc_fp += n_fp
                        nrc_tn += n_tn
                        nrc_tp += n_tp
                        continue
                    if u'tor_scores' in word:
                        t_tp, t_tn, t_fp, t_fn = get_ts(real_paradigms, word['tor_scores'], u'N')
                        tor_fn += t_fn
                        tor_fp += t_fp
                        tor_tn += t_tn
                        tor_tp += t_tp
                    elif u'scores' in word:
                        n_tp, n_tn, n_fp, n_fn = get_ts(real_paradigms, word['scores'], u'N')
                        nrc_fn += n_fn
                        nrc_fp += n_fp
                        nrc_tn += n_tn
                        nrc_tp += n_tp
                    else:
                        total = 48
                        # ничего не предсказано для этого слова!
                        if u'tor_id' in word:
                            # оно было-таки торотовским
                            t_tn = total - 1
                            t_fn = 1
                            tor_fn += t_fn
                            tor_tn += t_tn
                        else:
                            n_tn = total - 1
                            n_fn = 1
                            nrc_fn += n_fn
                            nrc_tn += n_tn
    t_pres, t_recall, t_f_measure = f_measure(tor_tp, tor_tn, tor_fp, tor_fn)
    n_pres, n_recall, n_f_measure = f_measure(nrc_tp, nrc_tn, nrc_fp, nrc_fn)
    return t_pres, t_recall, t_f_measure, n_pres, n_recall, n_f_measure


def get_ts(real_par, predict_par, pos):
    tp = 0
    fp = 0
    fn = 0
    for par in predict_par:
        if par in real_par:
            tp += 1
        else:
            fp += 1
    for par in real_par:
        if par not in predict_par:
            fn += 1
    pred_length = len(predict_par)
    if pos == u'N':
        total = 48
    elif pos == u'V':
        total = 54
    elif pos == u'Adj':
        total = 11
    tn = total - fp - fn - tp
    return tp, tn, fp, fn


def chose_for_manual():
    chosen_ones = []
    i = 0
    while i < 30:
        r_i = random.choice(jf)
        if r_i in chosen_ones or r_i['pos'] != u'N':
            continue
        if u'tor_scores' not in r_i or u'scores' not in r_i:
            continue
        i += 1
        chosen_ones.append(r_i)
    co = codecs.open(u'for_manual.json', u'w', u'utf-8')
    json.dump(chosen_ones, co, ensure_ascii=False, indent=2)
    co.close()


def f_measure(tp, tn, fp, fn):
    pres = float(tp) / (tp + fp)
    recall = float(tp) / (tp + fn)
    f_meas = 2 * pres * recall / (pres + recall)
    return pres, recall, f_meas


# t_pres, t_recall, t_f_measure, n_pres, n_recall, n_f_measure, has_all_three_infl, has_all_three = f_measure_poliakov()
# print u'btw, we have ', has_all_three, u'common words and', has_all_three_infl, u'inflected among them'
# print u'TOROT pres: ', t_pres, u', recall: ', t_recall, u', f-measure: ', t_f_measure
# print u'RNC pres: ', n_pres, u', recall: ', n_recall, u', f-measure: ', n_f_measure

# chose_for_manual()

# t_pres, t_recall, t_f_measure, n_pres, n_recall, n_f_measure = f_measure_manual()
# print u'TOROT pres: ', t_pres, u', recall: ', t_recall, u', f-measure: ', t_f_measure
# print u'RNC pres: ', n_pres, u', recall: ', n_recall, u', f-measure: ', n_f_measure

def raspr():
    t_score_dict = {}
    n_score_dict = {}
    for_r_2t = codecs.open(u'for_r2t.csv', u'w', u'utf-8')
    for_r_2n = codecs.open(u'for_r2n.csv', u'w', u'utf-8')
    for word in jf:
        if u'scores' in word:
            for par in word['scores']:
                score = word['scores'][par]
                for_r_2t.write(str(score) + u'\r\n')
                if word['scores'][par] in n_score_dict:
                    n_score_dict[word['scores'][par]] += 1
                else:
                    n_score_dict[word['scores'][par]] = 1
        if u'tor_scores' in word:
            for par in word['tor_scores']:
                score = word['tor_scores'][par]
                for_r_2n.write(str(score) + u'\r\n')
                if word['tor_scores'][par] in t_score_dict:
                    t_score_dict[word['tor_scores'][par]] += 1
                else:
                    t_score_dict[word['tor_scores'][par]] = 1
    j_score_dict = {}
    for score in t_score_dict:
        j_score_dict[score] = [t_score_dict[score], 0]
    for score in n_score_dict:
        if score in j_score_dict:
            j_score_dict[score][1] = n_score_dict[score]
        else:
            j_score_dict[score] = [0, n_score_dict[score]]
    for_r = codecs.open(u'for_r.csv', u'w', u'utf-8')
    for score in sorted(j_score_dict):
        for_r.write(str(score) + u'\t' + str(j_score_dict[score][0]) + u'\t' + str(j_score_dict[score][1]) + u'\r\n')

raspr()
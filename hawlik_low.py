#-*- coding: utf-8 -*-
import re

def samelettter(word):
    word = word.replace(u'нн', u'н')
    word = word.replace(u'сс', u'с')
    word = word.replace(u'жж', u'ж')
    word = word.replace(u'зз', u'з')
    word = word.replace(u'вв', u'в')
    word = word.replace(u'тт', u'т')
    word = word.replace(u'лл', u'л')
    word = word.replace(u'дд', u'д')
    return word

def hawlik_low(word):
    isodd = False
    word = list(word)
    vowels = list(u'уеыаѣоэяию')
    for i in xrange(len(word)):
        li = len(word) - i -1
        if word[li] in vowels:
            isodd = False
        if word[li] == u'ь' or word[li] == u'ъ':
            if isodd == True:
                word[li] = word[li].replace(u'ь', u'е')
                word[li] = word[li].replace(u'ъ', u'о')
                isodd = False
            else:
                isodd = True
                word[li] = u''
    word = u''.join(word)
    return word


def letterchange(word):
    newword = word
    newword = newword.replace(u'i', u'и')
    newword = newword.replace(u'і', u'и')
    newword = newword.replace(u'ѡ', u'о')
    newword = newword.replace(u'є', u'e')
    newword = newword.replace(u'́', u'')
    newword = newword.replace(u'́', u'')
    newword = newword.replace(u'ѵ', u'и')
    newword = newword.replace(u'̂', u'')
    newword = newword.replace(u'ѻ', u'о')
    newword = newword.replace(u'ѳ', u'ф')
    newword = newword.replace(u'ѯ', u'кс')
    newword = newword.replace(u'ѱ', u'пс')
    newword = newword.replace(u'ѕ', u'з')
    newword = newword.replace(u'ѣ', u'е')
    newword = newword.replace(u'ꙋ', u'у')
    newword = newword.replace(u'ꙗ', u'я')
    newword = newword.replace(u'ѧ', u'я')
    return newword

def inter_new(word):
    newword = re.sub(u'([цкнгшщзхфвпрлджчсмтб])(ь|ъ)([цкнгшщзхфвпрлджчсмтб])', u'\\1\\3', word)
    if newword[-1] == u'ь' or newword[-1] == u'ъ':
        newword = newword[:-1]
    return newword


def modernize_oslo(word2):
    word2 = word2.replace(u"ѣ", u"е")
    word2 = word2.replace(u"кы", u"ки")
    word2 = word2.replace(u"гы", u"ги")
    word2 = word2.replace(u"хы", u"хи")
    return word2

def cluster_yers(word2):
    word3 = word2.replace(u"чст", u"чест")
    word3 = word3.replace(u"чск", u"ческ")
    return word3


def moscow_prefix_yers(word2):
    if (word2[0] == u"в" or word2[0] == u"с") and word2[1] == u"о" and len(word2) > 4:
        word2 = word2[0] + u'ъ' + word2[2:]
    return word2

def oslo_trans(goldlemma):
    goldlemma = letterchange(goldlemma)
    goldlemma = hawlik_low(goldlemma)
    goldlemma = cluster_yers(goldlemma)
    goldlemma = samelettter(goldlemma)
    goldlemma = modernize_oslo(goldlemma)
    return goldlemma

def indent(goldlemma, unilemma):
    unilemma = letterchange(unilemma)
    unilemma = moscow_prefix_yers(unilemma)
    unilemma = inter_new(unilemma)
    unilemma = unilemma.replace(u'зс', u'сс')
    unilemma = samelettter(unilemma)
    unilemma = unilemma.replace(u'жде', u'же')
    if unilemma == u"сеи":
        unilemma = u"сии"
    if unilemma == u"тои":
        unilemma = u"тыи"
    if unilemma == u"перед":
        unilemma = u"пред"
    if unilemma == u"писати":
        unilemma = u"псати"
    if unilemma == goldlemma:
        return True
    return False

# word = u'сьрдьце'
# print hawlik_low(word)
# word = u'отьць'
# print hawlik_low(word)
# word = u'отьца'
# print hawlik_low(word)
# print indent(u'отьць', u'отець')
# print moscow_prefix_yers(u'состояние')
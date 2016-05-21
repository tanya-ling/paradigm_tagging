#-*- coding: utf-8 -*-

def levenshtein(s, t):
    m, n = len(s), len(t)
    D = [range(n + 1)] + [[x + 1] + [None] * n for x in xrange(m)]
    for i in xrange(1, m + 1):
        for j in xrange(1, n + 1):
            if s[i - 1] == t[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                before_insert = D[i][j - 1]
                before_delete = D[i - 1][j]
                before_change = D[i - 1][j - 1]
                D[i][j] = min(before_insert, before_delete, before_change) + 1
        # поиск предписания проходом от конца к началу
    prescription = [] # собственно, предписание
    prescription_s = [] # соответствие предписания и символов строки s
    prescription_t = [] # соответствие предписания и символов строки t
    i, j = m, n
    while i and j:
        insert = D[i][j - 1]
        delete = D[i - 1][j]
        match_or_replace = D[i - 1][j - 1]
        best_choice = min(insert, delete, match_or_replace)
        if best_choice == match_or_replace:
            if s[i - 1] == t[j - 1]:  # match
                prescription.append('M')
            else: # replace
                prescription.append('R')
            prescription_s.append(s[i - 1])
            prescription_t.append(t[j - 1])
            i -= 1
            j -= 1
        elif best_choice == insert:
            prescription.append('I')
            prescription_s.append('-')
            prescription_t.append(t[j - 1])
            j -= 1
        elif best_choice == delete:
            prescription.append('D')
            prescription_s.append(s[i - 1])
            prescription_t.append('-')
            i -= 1
    # поиск шел в обратном направлении, reverse вернет прямой порядок
    prescription.reverse()
    prescription_s.reverse()
    prescription_t.reverse()
##    print prescription
##    print list(s)
##    print prescription_s
##    print list(t)
##    print prescription_t

    for d in D:
#        print d
        pass
    return D[m][n]
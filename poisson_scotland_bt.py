import scipy.stats as ss
from math import exp, factorial
import scipy.optimize as sc
import csv
from random import uniform
from collections import defaultdict

def poisson_test(scores):
    _m = 0
    for i in range(len(scores)):
        _m += scores[i]*i
    _m /= sum(scores)
    _chi = 0
    for i in range(len(scores)):
        O = scores[i]
        E = pow(_m, i)*exp(-_m)/factorial(i)*sum(scores)
        _chi += pow(O-E,2)/E
    return _m, 1-ss.chi2.cdf(_chi, len(scores)-2)

d = {}
means = {}
with open('Szkocja_20201225.csv', newline = '') as csvfile:
    _reader = csv.reader(csvfile, delimiter = ';')
    next(_reader)
    for row in _reader:
        if (row[0], 'A') not in d:
            d[(row[0], 'A')] = [0]*10
            d[(row[0], 'D')] = [0]*10
        d[(row[0], 'A')][int(row[2])] += 1
        d[(row[0], 'D')][int(row[3])] += 1
        if (row[1], 'A') not in d:
            d[(row[1], 'A')] = [0]*10
            d[(row[1], 'D')] = [0]*10
        d[(row[1], 'A')][int(row[3])] += 1
        d[(row[1], 'D')][int(row[2])] += 1

plevels = {}
for team in d:
    print(team, d[team], poisson_test(d[team]))
    means[team] = poisson_test(d[team])[0]
    plevels[team] = poisson_test(d[team])[1]

w = [uniform(1, 2) for _ in range(len(d))]
inds = {}
inv_inds = {}
ind = 0
for team in d:
    inds[team] = ind
    inv_inds[ind] = team
    ind += 1

# def f(w):
#     sm = 0
#     with open('Szkocja.csv', newline='') as csvfile:
#         _reader = csv.reader(csvfile, delimiter=';')
#         next(_reader)
#         for row in _reader:
#             w_left = w[inds[(row[0], 'A')]]/(w[inds[(row[0], 'A')]] + w[inds[(row[1], 'D')]])
#             w_right = 1-w_left
#             sm += w_left*exp(-means[(row[0], 'A')])*pow(means[(row[0], 'A')], int(row[4]))/factorial(int(row[4]))
#             sm += w_right*exp(-means[(row[1], 'D')])*pow(means[(row[1], 'D')], int(row[4]))/factorial(int(row[4]))
#
#             w_left = w[inds[(row[1], 'A')]]/(w[inds[(row[1], 'A')]] + w[inds[(row[0], 'D')]])
#             w_right = 1-w_left
#             sm += w_left*exp(-means[(row[1], 'A')])*pow(means[(row[1], 'A')], int(row[5]))/factorial(int(row[5]))
#             sm += w_right*exp(-means[(row[0], 'D')])*pow(means[(row[0], 'D')], int(row[5]))/factorial(int(row[5]))
#
#     return -sm
#
# res = sc.minimize(f, x0= w[:], method='SLSQP', tol=pow(10,-8), options={'maxiter':2000000}, bounds=[(1,2) for _ in range(len(d))])
# print(res)
#
# for i in range(len(res.x)):
#     print(inv_inds[i], res.x[i])

predictors = [('Dundee United FC', 'Kilmarnock FC', (2,0)), ('Motherwell FC', 'Aberdeen FC', (0,0)),
              ('Saint Johnstone FC', 'Glasgow Rangers FC', (0,3)),
              ('Hibernian FC', 'Saint Mirren FC', (1,0)), ('Hamilton Academicals FC', 'Livingston FC', (0,2)),
              ('Celtic Glasgow FC', 'Ross County',  (2,0)), ('Aberdeen FC', 'Saint Johnstone FC', (2,1)),
              ('Dundee United FC', 'Motherwell FC', (1,1)), ('Hamilton Academicals FC', 'Celtic Glasgow FC', (0,3)),
              ('Kilmarnock FC', 'Livingston FC', (1,2)), ('Ross County', 'Saint Mirren FC', (0,2)),
              ('Glasgow Rangers FC', 'Hibernian FC', (1,0))]

#predictors = []
with open('Szkocja_20201225.csv', newline = '') as csvfile:
    _reader = csv.reader(csvfile, delimiter = ';')
    next(_reader)
    for row in _reader:
        predictors.append((row[0], row[1], (int(row[2]), int(row[3]))))

counts = [0]*6
counts_25 = [0,0]
counts_sum = [0,0]
for pred in predictors:
    scores = defaultdict(float)
    scores_uo25 = defaultdict(float)
    scores_102 = defaultdict(float)
    scores_both = defaultdict(float)
    scores_sum = defaultdict(float)
    for i in range(10):
        for j in range(10):
            p = ((pow(means[(pred[0], 'A')], i)*exp(-means[(pred[0], 'A')])/factorial(i)
                            +pow(means[(pred[1], 'D')], i)*exp(-means[(pred[1], 'D')])/factorial(i))/2)\
                            *((pow(means[(pred[1], 'A')], j)*exp(-means[(pred[1], 'A')])/factorial(j)
                            +pow(means[(pred[0], 'D')], j)*exp(-means[(pred[0], 'D')])/factorial(j))/2)
            scores[(i,j)] += p
            if i+j < 2.5: scores_uo25['-2.5'] += p
            else: scores_uo25['+2.5'] += p
            if i > j: scores_102[1] += p
            elif i == j: scores_102[0] += p
            else: scores_102[2] += p
            if i == 0 or j == 0: scores_both['N'] += p
            else: scores_both['Y'] += p
            scores_sum[i+j] += p
    #print(pred)
    _scores = []
    #print(scores_uo25['-2.5'], scores_uo25['+2.5'])
    #print([scores_102[1], scores_102[0], scores_102[2]])
    #print(scores_both['Y'], scores_both['N'])
    # for i in range(10):
    #     for j in range(10):
    #         _scores.append([(i,j), scores[(i,j)]])
    # _scores.sort(key= lambda x: -x[1])
    # for i in range(len(_scores[:5])):
    #     print(_scores[i])
    # threshold_25 = 0.55
    # if scores_uo25['-2.5'] > threshold_25:
    #     if sum(pred[2]) < 2.5:
    #         counts_25[0] += 1
    #     else:
    #         counts_25[1] += 1
    # if scores_uo25['+2.5'] > threshold_25:
    #     if sum(pred[2]) > 2.5:
    #         counts_25[0] += 1
    #     else:
    #         counts_25[1] += 1
    # check = False
    # if _scores[0][1] > 0.11:
    #     for i in range(len(_scores[:1])):
    #         if _scores[i][0] == pred[2]:
    #             if not check:
    #                 counts[i] += 1
    #                 check = True
    #         #print(_scores[i])
    #     if not check: counts[5] += 1
    #     # for i in range(len(_scores[:1])):
    #     #     print(_scores[i])
    #     print(pred)
    #     print(_scores[0])
    _scores_sum = []
    for i in range(5):
        _scores_sum.append((i, scores_sum[i]))
    _scores_sum.sort(key= lambda x: -x[1])
    if _scores_sum[0][1]+_scores_sum[1][1] > 0.45:
        print(pred)
        print(_scores_sum[:2])
        print('************')
        if sum(pred[2]) in (_scores_sum[0][0], _scores_sum[1][0]):
            counts_sum[0] += 1
        else:
            counts_sum[1] += 1

# print(counts_25, counts_25[0]/sum(counts_25))
#print(counts)
#print(sum(counts[:1]), sum(counts), sum(counts[:1])/sum(counts))
print(counts_sum, counts_sum[0]/sum(counts_sum))
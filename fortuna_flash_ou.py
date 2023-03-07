import csv
import statsmodels.stats.proportion as sm
import numpy as np
import fortuna_helper as fh

data = []
data_path = 'C://Users//Marzena//PycharmProjects//DS//flashscore_ous.csv'
with open(data_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    for row in reader:
        if row[2] == 'o':
            data.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[1])), 1])
            data.append([float(row[1]), fh.calc_equilibrium(float(row[0]), float(row[1])), 0])
        else:
            data.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[1])), 0])
            data.append([float(row[1]), fh.calc_equilibrium(float(row[0]), float(row[1])), 1])

data = np.array(data)
m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
m1, d1 = np.mean(data[:,1]), np.std(data[:,1])

for k in range(data.shape[0]):
    data[k,0] -= m0
    data[k,0] /= d0
    data[k,1] -= m1
    data[k,1] /= d1

def sort_radius(x):
    return (x[2][0] * (x[0][0] - 1) - (1 - x[2][0]))

def knn_area(rate, normalized=True):
    if not normalized:
        _rate = ((rate[0] - m0)/d0, (rate[1] - m1)/d1)
    else:
        _rate = rate
    positive = 0
    ct = 0
    for row in data:
        if ((row[0] - _rate[0])**2 + (row[1] - _rate[1])**2)**0.5 < 0.25:
            if row[2] == 1: positive += 1
            ct += 1
    return positive, ct

_alpha = 0.01

positive_ct = 0
main_ct = 0
all_ct = 0
for r in data:
    k = knn_area(r[:2], True)
    s = sm.proportion_confint(k[0], k[1], alpha=_alpha)
    ev = s[0]*(r[0]*d0+m0-1) - (1-s[0])
    if ev > 0.2:
        main_ct += 1
        if r[2] == 1:
            positive_ct += 1
    all_ct += 1
    if all_ct % 100 == 0: print(positive_ct, main_ct, all_ct)

print(positive_ct, main_ct, all_ct)

# r = (1.81, fh.calc_equilibrium(1.81, 2.11))
# k = knn_area(r[:2], False)
# s = sm.proportion_confint(k[0], k[1], alpha=_alpha)
# ev = s[0]*(r[0]-1) - (1-s[0])
# print(r, k, s, ev)
#
# r = (1.72, fh.calc_equilibrium(1.72, 2.25))
# k = knn_area(r[:2], False)
# s = sm.proportion_confint(k[0], k[1], alpha=_alpha)
# ev = s[0]*(r[0]-1) - (1-s[0])
# print(r, k, s, ev)
#
# r = (1.65, fh.calc_equilibrium(1.65, 2.38))
# k = knn_area(r[:2], False)
# s = sm.proportion_confint(k[0], k[1], alpha=_alpha)
# ev = s[0]*(r[0]-1) - (1-s[0])
# print(r, k, s, ev)
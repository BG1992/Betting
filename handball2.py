from scipy.stats import norm
import scipy.optimize as sc
from scipy.stats import shapiro
import numpy as np
import csv
from random import uniform, shuffle
from collections import defaultdict

matches = []
params = {}
scores = defaultdict(list)
with open('pgnig_men.csv', newline='') as f:
    _reader = csv.reader(f, delimiter=';')
    for row in _reader:
        l, r = float(row[4].replace(',', '.')), float(row[5].replace(',', '.'))
        matches.append((row[0], row[1], int(row[2]), int(row[3]), l, r))

ratio = 0.8
shuffle(matches)
train = matches[:int(len(matches)*ratio)]
test = matches[int(len(matches)*ratio):]
test.append(('Głogów', 'Puławy', 0, 0, 56.5, 60.5))
#if ('Elbląg', 'Kobierzyce', 20, 22) not in test:quit()

for m in train:
    scores[m[0], 'A'].append(m[2])
    scores[m[1], 'D'].append(m[2])
    scores[m[1], 'A'].append(m[3])
    scores[m[0], 'D'].append(m[3])

for s in scores:
    params[s] = (np.average(scores[s]), np.std(scores[s]))

for s in scores:
    print(s, params[s])

x = [uniform(0, 1) for _ in range(len(scores))]
ords = {}
k = 0
for s in scores:
    ords[s] = k
    k += 1

data = defaultdict(list)
sims_ct = 2*pow(10,2)
for s in scores:
    for i in range(sims_ct):
        data[s].append(np.random.normal(params[s][0], params[s][1]))

def f(x):
    sm = 0
    for m in train:
        wl = x[ords[(m[0], 'A')]]/(x[ords[(m[0], 'A')]] + x[ords[(m[1], 'D')]])
        wr = 1-wl
        for i in range(sims_ct):
            sm += (data[(m[0], 'A')][i]*wl + data[(m[1], 'D')][i]*wr - m[2])**2
        wl = x[ords[(m[1], 'A')]]/(x[ords[(m[1], 'A')]] + x[ords[(m[0], 'D')]])
        wr = 1-wl
        for i in range(sims_ct):
            sm += (data[(m[1], 'A')][i]*wl + data[(m[0], 'D')][i]*wr - m[3])**2
    return sm

bnds = [(0.01,0.99) for _ in range(len(scores))]
res = sc.minimize(f, x0= x[:], method='L-BFGS-B', tol=pow(10,-14), options={'maxiter':2000000},
                  bounds=bnds)

print(res)
p = 0.99
qt = norm.ppf(p)
ct = 0
ct2 = 0
ctu = 0
cto = 0
for m in test:
    print(m)
    wl = x[ords[(m[0], 'A')]] / (x[ords[(m[0], 'A')]] + x[ords[(m[1], 'D')]])
    wr = 1 - wl
    left_goals = (wl*params[(m[0], 'A')][0] + wr*params[(m[1], 'D')][0],
                  wl*params[(m[0], 'A')][1] + wr*params[(m[1], 'D')][1])
    mi_left, sigma_left2 = wl*params[(m[0], 'A')][0] + wr*params[(m[1], 'D')][0], \
                (wl*params[(m[0], 'A')][1]**2 + wr*params[(m[1], 'D')][1]**2)
    #interval = (mi - qt*sigma/len(scores[(m[0], 'A')]), mi + qt*sigma/len(scores[(m[0], 'A')]))
    #print('left', interval)
    interval = (mi_left - (sigma_left2**0.5) * 0.8, mi_left + (sigma_left2**0.5) * 0.8)
    print(mi_left, interval, m[2])
    if m[2] >= interval[0] and m[2] <= interval[1]: ct += 1
    wl = x[ords[(m[1], 'A')]] / (x[ords[(m[1], 'A')]] + x[ords[(m[0], 'D')]])
    wr = 1 - wl
    right_goals = (wl * params[(m[1], 'A')][0] + wr * params[(m[0], 'D')][0],
                  wl * params[(m[1], 'A')][1] + wr * params[(m[0], 'D')][1])
    mi_right, sigma_right2 = wl*params[(m[1], 'A')][0] + wr*params[(m[0], 'D')][0], \
                (wl*params[(m[1], 'A')][1]**2 + wr*params[(m[0], 'D')][1]**2)
    interval = (mi_right - (sigma_right2 ** 0.5) * 0.8, mi_right + (sigma_right2 ** 0.5) * 0.8)
    print(mi_right, interval, m[3])
    if m[3] >= interval[0] and m[3] <= interval[1]: ct += 1
    mi = mi_left + mi_right
    sigma2 = sigma_left2 + sigma_right2
    interval =  (mi - (sigma2**0.5)*0.8, mi + (sigma2**0.5)*0.8)
    if m[2]+m[3] >= interval[0] and m[2] + m[3] <= interval[1]: ct2 += 1
    print(mi, interval, m[2]+m[3])
    if m[2]+m[3] < mi + (sigma2**0.5)*0.1: ctu += 1
    if m[2]+m[3] > mi - (sigma2**0.5)*0.1: cto += 1
    print(mi, (sigma2)**0.5, (m[4], m[5]))

    #print(left_goals, right_goals)
    #interval = (mi - qt*sigma/len(scores[(m[1], 'A')]), mi + qt*sigma/len(scores[(m[1], 'A')]))
    #print('right', interval)
    print('***************')

print(ct, len(test)*2-2, ct/(len(test)*2-2))
print(ct2, len(test)-1, ct2/(len(test)-1))
# print(ctu, len(test)-1, ctu/(len(test)-1))
# print(cto, len(test)-1, cto/(len(test)-1))

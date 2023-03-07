import csv
import statsmodels.stats.proportion as sm
from statistics import mean, stdev
import numpy as np
import scipy as sp
from sklearn.neighbors import KNeighborsClassifier
from random import sample

data = []

def get_score(score):
    left = int(score[:score.index('--')])
    right = int(score[score.index('--')+2:])
    return [left, right]

def format_row(row):
    _row = []
    for el in row:
        if el == '':
            _row.append(0)
        else:
            _row.append(float(el))
    return _row

def calc_equilibrium(left, right):
    p = ((right-1)*0.88+1)/((left-1)*0.88+1+(right-1)*0.88+1)
    return (left-1)*0.88*p - (1-p)

def new_bet(left, right, score, bet, under=None):
    if bet == '1':
        if score[0] > score[1]:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    elif bet == '0':
        if score[0] == score[1]:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    elif bet == '2':
        if score[0] < score[1]:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    elif bet == 'under':
        if sum(score) < under:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    return [min(left, right), calc_equilibrium(left, right), _result][:]

data_test = []
with open('C://Users//Marzena//Documents//fortuna 06112020.csv', newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        score = get_score(row[-1])
        data.append(new_bet(float(row[0]), float(row[4]), score, '1'))
        data.append(new_bet(float(row[1]), float(row[5]), score, '0'))
        data.append(new_bet(float(row[2]), float(row[3]), score, '2'))
        if row[6] != '': data.append(new_bet(float(row[6]), float(row[7]), score, 'under', 0.5))
        if row[8] != '': data.append(new_bet(float(row[8]), float(row[9]), score, 'under', 1.5))
        if row[10] != '': data.append(new_bet(float(row[10]), float(row[11]), score, 'under', 2.5))
        if row[12] != '': data.append(new_bet(float(row[12]), float(row[13]), score, 'under', 3.5))
        if row[14] != '': data.append(new_bet(float(row[14]), float(row[15]), score, 'under', 4.5))
        if row[16] != '': data.append(new_bet(float(row[16]), float(row[17]), score, 'under', 5.5))
        if row[18] != '': data.append(new_bet(float(row[18]), float(row[19]), score, 'under', 6.5))

data = np.array(data)

print(data.shape)
print(sp.stats.shapiro(data[:,0]))
print(sp.stats.shapiro(data[:,1]))

m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
m1, d1 = np.mean(data[:,1]), np.std(data[:,1])

for k in range(data.shape[0]):
    data[k,0] -= m0
    data[k,0] /= d0
    data[k,1] -= m1
    data[k,1] /= d1

def knn(score, k):
    ct = 0
    q = []
    _score = ((min(score) - m0)/d0, (calc_equilibrium(score[0], score[1]) - m1)/d1)
    for row in data:
        dist = ((row[0] - _score[0])**2 + (row[1] - _score[1])**2)**0.5
        q.append((dist, row[2]))
    q.sort(key=lambda x: x[0])
    for i in range(k):
        if q[i][1] == 1: ct += 1
        #print(q[i])
    return ct

def knn_radius(score, radius):
    ct = 0
    q = []
    _score = ((min(score) - m0)/d0, (calc_equilibrium(score[0], score[1]) - m1)/d1)
    for row in data:
        dist = ((row[0] - _score[0])**2 + (row[1] - _score[1])**2)**0.5
        q.append((dist, row[2]))
    q.sort(key=lambda x: x[0])
    i = 0
    while q[i][0] <= radius:
        if q[i][1] == 1: ct += 1
        i += 1
        #print(q[i])
    return ct, i, ct/i


def knn_weighted(score, k):
    _score = [[(min(score) - m0) / d0, (calc_equilibrium(score[0], score[1]) - m1) / d1]]
    X, y = data[:,:2], data[:,2]
    neigh = KNeighborsClassifier(n_neighbors=k, weights='distance')
    neigh.fit(X, y)
    return neigh.predict_proba(_score)

n = 100
q = 1
rates = [(1.73, 2.32), (1.7, 2.15), (1.78, 2.04), (1.78, 2.16), (1.93, 1.97), (1.86, 2.05),
         (1.75, 2.2), (1.91, 1.95), (1.90, 1.99), (1.88, 2.02), (1.91, 1.97), (1.82, 2.08),
         (1.87, 2.0), (1.89, 1.95)]

radius_sorted = []
for r in rates:
    # _knn = knn_weighted(r, n)[0][1]
    # _knn2 = knn(r, n)
    _knn3 = knn_radius(r, 0.5)
    radius_sorted.append([r, _knn3, sm.proportion_confint(_knn3[0], _knn3[1])])

radius_sorted.sort(key= lambda x: -x[2][0])
for r in radius_sorted:
    print(r)
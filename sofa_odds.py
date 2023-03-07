import csv
import statsmodels.stats.proportion as sm
from random import uniform

def check_score(score):
    if score[0] >= score[1]: return 1
    return 0

def check_row(row):
    if row[0] > 1000:
        return True
    return False

data = []

with open('sofascore_test_data.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    for row in _reader:
        s = sum(map(lambda x: float(x), row[7:]))
        _row = [s, float(row[7])/s, float(row[8])/s, float(row[9])/s]
        if check_row(_row):
            data.append(_row + [1 if check_score(list(map(lambda x: int(x), row[4:6]))) else 0])

a = [0.55, 0.6]
b = [0.15, 0.2]

m = 0
_x = 0
_y = 0
_positive = 0
_ct = 0

for i in range(pow(10,6)):
    x = uniform(0.4, 0.8)
    y = uniform(0.5, 0.9)
    positive, ct = 0, 0
    for row in data:
        if row[1] > x and row[1]+row[2] > y:
            if row[-1] == 1:
                positive += 1
            ct += 1
    s = sm.proportion_confint(positive, ct, alpha=0.01)
    if ct > 200 and s[0] > m:
        m = s[0]
        _x = x
        _y = y
        _positive = positive
        _ct = ct
    if i % 1000 == 0: print(i, m, _x, _y, _positive, _ct)
    #print(positive, ct, positive/ct, s)
import csv
from collections import defaultdict
from random import uniform
import numpy as np
import statsmodels.api as sm
import pandas as pd

variables = defaultdict(float)
ind_variables = {}
teams = set()
with open('premierleague_scores.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        teams.add(row[0])

ind = 0
for team in teams:
    variables[(team, 'H', 'A')] = ind
    ind_variables[ind] = (team, 'H', 'A')
    ind += 1
    variables[(team, 'H', 'D')] = ind
    ind_variables[ind] = (team, 'H', 'D')
    ind += 1
    variables[(team, 'A', 'A')] = ind
    ind_variables[ind] = (team, 'A', 'A')
    ind += 1
    variables[(team, 'A', 'D')] = ind
    ind_variables[ind] = (team, 'A', 'D')
    ind += 1

data = []

with open('premierleague_scores.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        _row = [0]*len(variables)
        _row[variables[(row[0], 'H', 'A')]] = uniform(0.9, 1)
        _row[variables[(row[1], 'A', 'D')]] = uniform(0.9, 1)
        _row[variables[(row[1], 'A', 'A')]] = uniform(0.9, 1)
        _row[variables[(row[0], 'H', 'D')]] = uniform(0.9, 1)
        if float(row[2]) + float(row[3]) < 1.5:
            _row.append(1.0)
        else:
            _row.append(0.0)
        data.append(_row[:])

samples_ct = len(data)
data = pd.DataFrame(data)
#data = sm.add_constant(data)

X = data.iloc[:samples_ct, :-1]
y = data.iloc[:samples_ct, -1]

print(X.corr())
results = sm.Logit(y, X).fit()
print(results.summary())

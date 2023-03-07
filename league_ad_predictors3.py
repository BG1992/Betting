import csv
from collections import defaultdict
from random import uniform
import scipy.optimize as sc
from math import exp

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
    variables[(team, 'H', 'A', '1')] = ind
    ind_variables[ind] = (team, 'H', 'A', '1')
    ind += 1
    variables[(team, 'H', 'A', '2')] = ind
    ind_variables[ind] = (team, 'H', 'A', '2')
    ind += 1
    variables[(team, 'H', 'D', '1')] = ind
    ind_variables[ind] = (team, 'H', 'D', '1')
    ind += 1
    variables[(team, 'H', 'D', '2')] = ind
    ind_variables[ind] = (team, 'H', 'D', '2')
    ind += 1
    variables[(team, 'A', 'A', '1')] = ind
    ind_variables[ind] = (team, 'A', 'A', '1')
    ind += 1
    variables[(team, 'A', 'A', '2')] = ind
    ind_variables[ind] = (team, 'A', 'A', '2')
    ind += 1
    variables[(team, 'A', 'D', '1')] = ind
    ind_variables[ind] = (team, 'A', 'D', '1')
    ind += 1
    variables[(team, 'A', 'D', '2')] = ind
    ind_variables[ind] = (team, 'A', 'D', '2')
    ind += 1

tb = [uniform(-0.3, 0.3) for _ in range(len(variables))]

def g(score_left, score_right):
    if float(score_left) + float(score_right) < 2.5: return 1
    return -1

def f(x):
    sm = 0
    with open('premierleague_scores.csv', newline='') as csvfile:
        _reader = csv.reader(csvfile, delimiter=';')
        next(_reader)
        for row in _reader:
            # eq = x[variables[(row[0], 'H', 'A')]] - x[variables[(row[1], 'A', 'D')]]+ \
            #     x[variables[(row[1], 'A', 'A')]] - x[variables[(row[0], 'H', 'D')]]
            # if eq*g(row[2], row[3]) < 0: sm += 1
            # s = x[variables[(row[0], 'H', 'A', '1')]] + x[variables[(row[0], 'H', 'A', '2')]]
            # + x[variables[(row[1], 'A', 'A', '1')]] + x[variables[(row[1], 'A', 'A', '2')]]
            # + x[variables[(row[1], 'A', 'D', '1')]] + x[variables[(row[1], 'A', 'D', '2')]]
            # + x[variables[(row[0], 'H', 'D', '1')]] + x[variables[(row[0], 'H', 'D', '2')]]
            s = x[variables[(row[0], 'H', 'A', '1')]] + x[variables[(row[1], 'A', 'D', '1')]]
            y = float(row[2])
            sm += abs(exp(s)/(1+exp(s)) - y)
            s = x[variables[(row[1], 'A', 'A', '1')]] + x[variables[(row[0], 'H', 'D', '1')]]
            y = float(row[3])
            sm += abs(exp(s) / (1 + exp(s)) - y)
    return sm

res = sc.minimize(f, x0= tb[:], method='SLSQP', tol=pow(10,-8), options={'maxiter':2000000})
print(res)

for i in range(len(res.x)):
    print(ind_variables[i], res.x[i])

predictors = [(('Arsenal', 'H', 'A', '1'), ('Wolves', 'A', 'D', '1')),
                (('Arsenal', 'H', 'A', '2'), ('Wolves', 'A', 'D', '2')),
                (('Arsenal', 'H', 'D', '1'), ('Wolves', 'A', 'A', '1')),
                (('Arsenal', 'H', 'D', '2'), ('Wolves', 'A', 'A', '2')),
                (('Chelsea', 'H', 'A', '1'), ('Tottenham', 'A', 'D', '1')),
                (('Chelsea', 'H', 'A', '2'), ('Tottenham', 'A', 'D', '2')),
                (('Chelsea', 'H', 'D', '1'), ('Tottenham', 'A', 'A', '1')),
                (('Chelsea', 'H', 'D', '2'), ('Tottenham', 'A', 'A', '2')),
                (('Southampton', 'H', 'A', '1'), ('Manchester Utd', 'A', 'D', '1')),
                (('Southampton', 'H', 'A', '2'), ('Manchester Utd', 'A', 'D', '2')),
                (('Southampton', 'H', 'D', '1'), ('Manchester Utd', 'A', 'A', '1')),
                (('Southampton', 'H', 'D', '2'), ('Manchester Utd', 'A', 'A', '2')),
                (('West Brom', 'H', 'A', '1'), ('Sheffield Utd', 'A', 'D', '1')),
                (('West Brom', 'H', 'A', '2'), ('Sheffield Utd', 'A', 'D', '2')),
                (('West Brom', 'H', 'D', '1'), ('Sheffield Utd', 'A', 'A', '1')),
                (('West Brom', 'H', 'D', '2'), ('Sheffield Utd', 'A', 'A', '2')),
                (('Everton', 'H', 'A', '1'), ('Leeds', 'A', 'D', '1')),
                (('Everton', 'H', 'A', '2'), ('Leeds', 'A', 'D', '2')),
                (('Everton', 'H', 'D', '1'), ('Leeds', 'A', 'A', '1')),
                (('Everton', 'H', 'D', '2'), ('Leeds', 'A', 'A', '2')),
                (('Manchester City', 'H', 'A', '1'), ('Burnley', 'A', 'D', '1')),
                (('Manchester City', 'H', 'A', '2'), ('Burnley', 'A', 'D', '2')),
                (('Manchester City', 'H', 'D', '1'), ('Burnley', 'A', 'A', '1')),
                (('Manchester City', 'H', 'D', '2'), ('Burnley', 'A', 'A', '2')),
                (('Brighton', 'H', 'A', '1'), ('Liverpool', 'A', 'D', '1')),
                (('Brighton', 'H', 'A', '2'), ('Liverpool', 'A', 'D', '2')),
                (('Brighton', 'H', 'D', '1'), ('Liverpool', 'A', 'A', '1')),
                (('Brighton', 'H', 'D', '2'), ('Liverpool', 'A', 'A', '2')),
                (('Crystal Palace', 'H', 'A', '1'), ('Newcastle', 'A', 'D', '1')),
                (('Crystal Palace', 'H', 'A', '2'), ('Newcastle', 'A', 'D', '2')),
                (('Crystal Palace', 'H', 'D', '1'), ('Newcastle', 'A', 'A', '1')),
              (('Crystal Palace', 'H', 'D', '2'), ('Newcastle', 'A', 'A', '2'))]

for pred in predictors:
    print(pred[0], '|', pred[1], '|', res.x[variables[pred[0]]], '|', res.x[variables[pred[1]]])
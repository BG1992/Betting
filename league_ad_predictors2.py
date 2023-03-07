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

tb = [uniform(-1, 1) for _ in range(len(variables))]

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
            s1 = x[variables[(row[0], 'H', 'A')]] + x[variables[(row[1], 'A', 'D')]]
            y1 = float(row[2]) > 1.5
            sm += (1/(1+exp(-s1))-y1)**2
            s2 = x[variables[(row[1], 'A', 'A')]] + x[variables[(row[0], 'H', 'D')]]
            y2 = float(row[3]) > 1.5
            sm +=(1/(1+exp(-s2))-y2)**2
    return sm

res = sc.minimize(f, x0= tb[:], method='SLSQP', bounds=[(-10000, 10000) for _ in range(len(variables))],
                  tol=pow(10,-8), options={'maxiter':2000000})
print(res)

for i in range(len(res.x)):
    print(ind_variables[i], res.x[i])

# predictors = [(('Arsenal', 'H', 'A'), ('Wolves', 'A', 'D')),
#                 (('Arsenal', 'H', 'D'), ('Wolves', 'A', 'A')),
#                 (('Chelsea', 'H', 'A'), ('Tottenham', 'A', 'D')),
#                 (('Chelsea', 'H', 'D'), ('Tottenham', 'A', 'A')),
#                 (('Southampton', 'H', 'A'), ('Manchester Utd', 'A', 'D')),
#                 (('Southampton', 'H', 'D'), ('Manchester Utd', 'A', 'A')),
#                 (('West Brom', 'H', 'A'), ('Sheffield Utd', 'A', 'D')),
#                 (('West Brom', 'H', 'D'), ('Sheffield Utd', 'A', 'A')),
#                 (('Everton', 'H', 'A'), ('Leeds', 'A', 'D')),
#                 (('Everton', 'H', 'D'), ('Leeds', 'A', 'A')),
#                 (('Manchester City', 'H', 'A'), ('Burnley', 'A', 'D')),
#                 (('Manchester City', 'H', 'D'), ('Burnley', 'A', 'A')),
#                 (('Brighton', 'H', 'A'), ('Liverpool', 'A', 'D')),
#                 (('Brighton', 'H', 'D'), ('Liverpool', 'A', 'A')),
#                 (('Crystal Palace', 'H', 'A'), ('Newcastle', 'A', 'D')),
#                 (('Crystal Palace', 'H', 'D'), ('Newcastle', 'A', 'A'))]

predictors = [(('Leicester', 'H', 'A'), ('Fulham', 'A', 'D')),
                (('Leicester', 'H', 'D'), ('Fulham', 'A', 'A')),
                (('West Ham', 'H', 'A'), ('Aston Villa', 'A', 'D')),
                (('West Ham', 'H', 'D'), ('Aston Villa', 'A', 'A'))]

for pred in predictors:
    print(pred[0], '|', pred[1], '|', res.x[variables[pred[0]]], '|', res.x[variables[pred[1]]])
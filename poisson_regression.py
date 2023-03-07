import csv
from collections import defaultdict
import pandas as pd
import statsmodels.api as sm

variables = defaultdict(float)
ind_variables = {}
teams = set()
with open('premierleague_scores.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        teams.add(row[0])

scores = defaultdict(list)

X_columns = []
X_columns.append('H')
Y_columns = list(teams)

for team in teams:
    X_columns.append(team + '_' + 'A' + '_' + 'const')
    X_columns.append(team + '_' + 'D' + '_' + 'const')
    X_columns.append(team + '_' + 'A' + '_' + 'temp')
    X_columns.append(team + '_' + 'D' + '_' + 'temp')

X = pd.DataFrame(columns=X_columns[:])
Y = pd.DataFrame(columns=Y_columns)

with open('premierleague_scores.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        X_temp_row = pd.DataFrame([[0]*len(X_columns)], columns=X_columns)
        d = {row[0]+'_A_const': 1, row[1]+'_D_const': 1, 'H': 1}
        i = 1
        while i <= 3:
            if i > len(scores[(row[0], 'A')]): break
            X_temp_row[row[0] + '_A_temp'] += scores[(row[0], 'A')][-i]
            i += 1
        if i >= 2: X_temp_row[row[0] + '_A_temp'] /= (i-1)
        i = 1
        while i <= 3:
            if i > len(scores[(row[1], 'D')]): break
            X_temp_row[row[1] + '_D_temp'] += scores[(row[1], 'D')][-i]
            i += 1
        if i >= 2: X_temp_row[row[1] + '_D_temp'] /= (i-1)
        for el in d:
            X_temp_row[el] = d[el]
        X = X.append(X_temp_row, ignore_index=True)
        Y_temp_row = pd.DataFrame([[0]*len(list(teams))], columns=Y_columns)
        Y_temp_row[row[0]] = int(row[2])
        Y = Y.append(Y_temp_row, ignore_index=True)
        X_temp_row = pd.DataFrame([[0] * len(X_columns)], columns=X_columns)
        d = {row[1] + '_A_const': 1, row[0] + '_D_const': 1}
        i = 1
        while i <= 3:
            if i > len(scores[(row[1], 'A')]): break
            X_temp_row[row[1] + '_A_temp'] += scores[(row[1], 'A')][-i]
            i += 1
        if i >= 2: X_temp_row[row[1] + '_A_temp'] /= (i - 1)
        i = 1
        while i <= 3:
            if i > len(scores[(row[0], 'D')]): break
            X_temp_row[row[0] + '_D_temp'] += scores[(row[0], 'D')][-i]
            i += 1
        if i >= 2: X_temp_row[row[0] + '_D_temp'] /= (i - 1)
        for el in d:
            X_temp_row[el] = d[el]
        X = X.append(X_temp_row, ignore_index=True)
        Y_temp_row = pd.DataFrame([[0] * len(list(teams))], columns=Y_columns)
        Y_temp_row[row[1]] = int(row[3])
        Y = Y.append(Y_temp_row, ignore_index=True)
        scores[(row[0], 'A')].append(int(row[2]))
        scores[(row[0], 'D')].append(int(row[3]))
        scores[(row[1], 'A')].append(int(row[3]))
        scores[(row[1], 'D')].append(int(row[2]))

X['const'] = 1

for team in teams:
    X_team = X[X[str(team) + '_A_const'] != 0]
    indices = list(X_team.index.values)
    y_team = Y[Y.index.isin(indices)][team]
    g = sm.GLM(y_team.astype(float), X_team.astype(float), family=sm.families.Poisson())
    g.raise_on_perfect_prediction = False
    res = g.fit()
    print(team)
    print(res.summmary())
    print('**************************************')
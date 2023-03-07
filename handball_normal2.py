import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
from collections import defaultdict
from math import log
from random import uniform

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\pgnig_test.csv', encoding='latin1', delimiter=';')
df = df[['HomeTeam','AwayTeam','FTHG','FTAG']]
df = df.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

df.reset_index(inplace=True)

pos_ct, ct = 0, 0

ind = 0
inds = {}
rev_inds = []

for i in range(df.shape[0]):
    if (df.iloc[i]['HomeTeam'], 'A', 'mi') not in inds:
        inds[(df.iloc[i]['HomeTeam'], 'A', 'mi')] = ind
        rev_inds.append((df.iloc[i]['HomeTeam'], 'A', 'mi'))
        ind += 1
    if (df.iloc[i]['HomeTeam'], 'A', 'sigma') not in inds:
        inds[(df.iloc[i]['HomeTeam'], 'A', 'sigma')] = ind
        rev_inds.append((df.iloc[i]['HomeTeam'], 'A', 'sigma'))
        ind += 1
    if (df.iloc[i]['HomeTeam'], 'D', 'mi') not in inds:
        inds[(df.iloc[i]['HomeTeam'], 'D', 'mi')] = ind
        rev_inds.append((df.iloc[i]['HomeTeam'], 'D', 'mi'))
        ind += 1
    if (df.iloc[i]['HomeTeam'], 'D', 'sigma') not in inds:
        inds[(df.iloc[i]['HomeTeam'], 'D', 'sigma')] = ind
        rev_inds.append((df.iloc[i]['HomeTeam'], 'D', 'sigma'))
        ind += 1
    if (df.iloc[i]['AwayTeam'], 'A', 'mi') not in inds:
        inds[(df.iloc[i]['AwayTeam'], 'A', 'mi')] = ind
        rev_inds.append((df.iloc[i]['AwayTeam'], 'A', 'mi'))
        ind += 1
    if (df.iloc[i]['AwayTeam'], 'A', 'sigma') not in inds:
        inds[(df.iloc[i]['AwayTeam'], 'A', 'sigma')] = ind
        rev_inds.append((df.iloc[i]['AwayTeam'], 'A', 'sigma'))
        ind += 1
    if (df.iloc[i]['AwayTeam'], 'D', 'mi') not in inds:
        inds[(df.iloc[i]['AwayTeam'], 'D', 'mi')] = ind
        rev_inds.append((df.iloc[i]['AwayTeam'], 'D', 'mi'))
        ind += 1
    if (df.iloc[i]['AwayTeam'], 'D', 'sigma') not in inds:
        inds[(df.iloc[i]['AwayTeam'], 'D', 'sigma')] = ind
        rev_inds.append((df.iloc[i]['AwayTeam'], 'D', 'sigma'))
        ind += 1

df_in = df.iloc[:df.shape[0]-9]
df_out = df.iloc[df.shape[0]-9:]

df_in.reset_index(inplace=True)
df_out.reset_index(inplace=True)

def f(x):
    sm = 0
    for i in range(df_in.shape[0]):

        home_score = df_in.iloc[i]['HomeGoals']
        away_score = df_in.iloc[i]['AwayGoals']

        mi_a, mi_d = x[inds[(df.iloc[i]['HomeTeam'], 'A', 'mi')]], x[inds[(df.iloc[i]['AwayTeam'], 'D', 'mi')]]
        sigma_a, sigma_d = x[inds[(df.iloc[i]['HomeTeam'], 'A', 'sigma')]], x[inds[(df.iloc[i]['AwayTeam'], 'D', 'sigma')]]

        sm += (-log(sigma_a**2 + sigma_d**2) - pow(home_score - (mi_a + mi_d), 2)/(sigma_a**2 + sigma_d**2))

        mi_a, mi_d = x[inds[(df.iloc[i]['AwayTeam'], 'A', 'mi')]], x[inds[(df.iloc[i]['HomeTeam'], 'D', 'mi')]]
        sigma_a, sigma_d = x[inds[(df.iloc[i]['AwayTeam'], 'A', 'sigma')]], x[inds[(df.iloc[i]['HomeTeam'], 'D', 'sigma')]]

        sm += (-log(sigma_a**2 + sigma_d**2) - pow(away_score - (mi_a + mi_d), 2)/(sigma_a**2 + sigma_d**2))
    print(-sm)
    return -sm

x0 = []
bnds = []
for i in range(len(inds)):
    if i % 2 == 0:
        x0.append(uniform(-10, 10))
        bnds.append((None, None))
    else:
        x0.append(uniform(0, 8))
        bnds.append((0.001, None))

res = minimize(f, x0, method='SLSQP', bounds=bnds)

for i in range(len(res.x)):
    print(rev_inds[i], res.x[i])

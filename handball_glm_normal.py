import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
from collections import defaultdict

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\pgnig_test.csv', encoding='latin1', delimiter=';')
df = df[['HomeTeam','AwayTeam','FTHG','FTAG']]
df = df.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

import statsmodels.api as sm
import statsmodels.formula.api as smf

def simulate_match(foot_model, homeTeam, awayTeam, max_goals=60):
    home_goals_avg = foot_model.predict(pd.DataFrame(data={'team': homeTeam,
                                                            'opponent': awayTeam,'home':1},
                                                      index=[1])).values[0]
    away_goals_avg = foot_model.predict(pd.DataFrame(data={'team': awayTeam,
                                                            'opponent': homeTeam,'home':0},
                                                      index=[1])).values[0]
    team_pred = [[norm.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
    return(np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

df.reset_index(inplace=True)

ind_start = 100
pos_ct, ct = 0, 0
thres = 0.5

df_in = df.iloc[:df.shape[0]-9]
df_out = df.iloc[df.shape[0]-9:]

df_in.reset_index(inplace=True)
df_out.reset_index(inplace=True)

goal_model_data = pd.concat([df_in[['HomeTeam','AwayTeam','HomeGoals']].assign(home=1).rename(
            columns={'HomeTeam':'team', 'AwayTeam':'opponent','HomeGoals':'goals'}),
           df_in[['AwayTeam','HomeTeam','AwayGoals']].assign(home=0).rename(
            columns={'AwayTeam':'team', 'HomeTeam':'opponent','AwayGoals':'goals'})])

norm_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                        family=sm.families.Gaussian()).fit()

for j in range(9):
    match_array = simulate_match(norm_model, df_out.iloc[j]['HomeTeam'],
                                 df_out.iloc[j]['AwayTeam'], max_goals=60)

    probs = {}
    for row in range(match_array.shape[0]):
        for col in range(match_array.shape[1]):
            probs[(row, col)] = match_array[row, col]
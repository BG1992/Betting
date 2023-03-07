import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson,skellam
from scipy.optimize import minimize
from collections import defaultdict

epl_1718 = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\premier-league-2020-2021.csv')

poisson_pred = np.column_stack([[poisson.pmf(i, epl_1718.mean()[j]) for i in range(8)] for j in range(2)])

import statsmodels.api as sm
import statsmodels.formula.api as smf

def simulate_match_lower(foot_model, homeTeam, awayTeam, max_goals=10):
    home_pred = foot_model.get_prediction(pd.DataFrame(data={'team': homeTeam,
                                                            'opponent': awayTeam,'home':1},
                                                      index=[1]))
    home_goals_avg = home_pred.predicted_mean[0] - home_pred.se_mean[0]
    away_pred = foot_model.get_prediction(pd.DataFrame(data={'team': awayTeam,
                                                 'opponent': homeTeam, 'home': 0},
                                           index=[1]))
    away_goals_avg = away_pred.predicted_mean[0] - away_pred.se_mean[0]
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
    return(np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

def simulate_match_upper(foot_model, homeTeam, awayTeam, max_goals=10):
    home_pred = foot_model.get_prediction(pd.DataFrame(data={'team': homeTeam,
                                                             'opponent': awayTeam, 'home': 1},
                                                       index=[1]))
    home_goals_avg = home_pred.predicted_mean[0] + home_pred.se_mean[0]
    away_pred = foot_model.get_prediction(pd.DataFrame(data={'team': awayTeam,
                                                             'opponent': homeTeam, 'home': 0},
                                                       index=[1]))
    away_goals_avg = away_pred.predicted_mean[0] + away_pred.se_mean[0]
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals + 1)] for team_avg in
                 [home_goals_avg, away_goals_avg]]
    return (np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

epl_1718.reset_index(inplace=True)

ind_start = 100
capital = 100
thres = 1.2

for i in range(ind_start, epl_1718.shape[0]-9, 9):
    epl_in = epl_1718.iloc[:i]
    epl_out = epl_1718.iloc[i:i+9]

    epl_in.reset_index(inplace=True)
    epl_out.reset_index(inplace=True)

    goal_model_data = pd.concat([epl_in[['Gospodarze','Goście','Gospodarze Gole']].assign(home=1).rename(
                columns={'Gospodarze':'team', 'Goście':'opponent','Gospodarze Gole':'goals'}),
               epl_1718[['Goście','Gospodarze','Goście Gole']].assign(home=0).rename(
                columns={'Goście':'team', 'Gospodarze':'opponent','Goście Gole':'goals'})])

    poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                            family=sm.families.Poisson()).fit()

    for j in range(9):
        match_array_lower = simulate_match_lower(poisson_model, epl_out.iloc[j]['Gospodarze'],
                                     epl_out.iloc[j]['Goście'], max_goals=10)

        probs = {}
        for row in range(match_array_lower.shape[0]):
            for col in range(match_array_lower.shape[1]):
                probs[(row, col)] = match_array_lower[row, col]

        for g in (1.5, 2.5, 3.5, 4.5):
            prob = 0
            for k in probs:
                if sum(k) < g:
                    prob += probs[k]
            if prob*epl_out.iloc[j][str(g) + ' Under'] > thres:
                f = prob - (1-prob)/(epl_out.iloc[j][str(g) + ' Under']-1)
                #f = 1/100
                capital -= f*capital
                if epl_out.iloc[j]['Gospodarze Gole'] + epl_out.iloc[j]['Goście Gole'] < g:
                    capital += f*capital*epl_out.iloc[j][str(g) + ' Under']
                print(prob, epl_out.iloc[j][str(g) + ' Under'], str(g) + ' Under')
                print(epl_out.iloc[j]['Gospodarze'], epl_out.iloc[j]['Goście'],
                      epl_out.iloc[j]['Gospodarze Gole'], epl_out.iloc[j]['Goście Gole'], capital)
                print('********************')

            # elif (1-prob)*epl_out.iloc[j][str(g) + ' Over'] > thres:
            #     #f = (1-prob) - prob/(epl_out.iloc[j][str(g) + ' Over']-1)
            #     f = 1/100
            #     capital -= f*capital
            #     if epl_out.iloc[j]['Gospodarze Gole'] + epl_out.iloc[j]['Goście Gole'] > g:
            #         capital += f*capital*epl_out.iloc[j][str(g) + ' Over']
            #     print(1-prob, epl_out.iloc[j][str(g) + ' Over'], str(g) + ' Over')
            #     print(epl_out.iloc[j]['Gospodarze'], epl_out.iloc[j]['Goście'],
            #           epl_out.iloc[j]['Gospodarze Gole'], epl_out.iloc[j]['Goście Gole'], capital)
            #     print('********************')


print(capital)
#print(poisson_model.summary())


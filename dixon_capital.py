import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson,skellam
from scipy.optimize import minimize
from collections import defaultdict
import os

#epl_1718 = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\laliga-2020-2021.csv')

files = os.listdir(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history')

for file in files:

    epl_1718 = pd.read_csv(os.path.join(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history', file))
    epl_1718 = epl_1718[['HomeTeam','AwayTeam','FTHG','FTAG', 'Avg>2.5', 'Avg<2.5']]
    epl_1718 = epl_1718.rename(columns={'FTHG': 'Gospodarze Gole', 'FTAG': 'Goście Gole', 'HomeTeam': 'Gospodarze',
                                        'AwayTeam': 'Goście', 'Avg>2.5': '2.5 Over', 'Avg<2.5': '2.5 Under'})

    poisson_pred = np.column_stack([[poisson.pmf(i, epl_1718.mean()[j]) for i in range(8)] for j in range(2)])

    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    def simulate_match(foot_model, homeTeam, awayTeam, max_goals=10):
        home_goals_avg = foot_model.predict(pd.DataFrame(data={'team': homeTeam,
                                                                'opponent': awayTeam,'home':1},
                                                          index=[1])).values[0]
        away_goals_avg = foot_model.predict(pd.DataFrame(data={'team': awayTeam,
                                                                'opponent': homeTeam,'home':0},
                                                          index=[1])).values[0]
        team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
        return(np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

    epl_1718.reset_index(inplace=True)

    ind_start = 100
    capital = 0
    init_capital = 1000
    thres = 1.35
    sm_bets = 0
    ct_bets = 0

    def brier(poisson_model, epl_in):
        sm = 0
        ct = 0
        for j in range(epl_in.shape[0]):
            match_array = simulate_match(poisson_model, epl_in.iloc[j]['Gospodarze'],
                                         epl_in.iloc[j]['Goście'], max_goals=10)

            probs = {}
            for row in range(match_array.shape[0]):
                for col in range(match_array.shape[1]):
                    probs[(row, col)] = match_array[row, col]

            for g in (1.5, 2.5, 3.5, 4.5):
                prob = 0
                for k in probs:
                    if sum(k) < g:
                        prob += probs[k]
                if epl_in.iloc[j]['Gospodarze Gole'] + epl_in.iloc[j]['Goście Gole'] < g:
                    sm += (prob - 1)**2
                    sm += (1-prob)**2
                if epl_in.iloc[j]['Gospodarze Gole'] + epl_in.iloc[j]['Goście Gole'] > g:
                    sm += prob**2
                    sm += (1-prob - 1)**2
                ct += 2

        return sm/ct

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

        sm_brier = brier(poisson_model, epl_in)
        #print('brier:', sm_brier)
        for j in range(9):
            match_array = simulate_match(poisson_model, epl_out.iloc[j]['Gospodarze'],
                                         epl_out.iloc[j]['Goście'], max_goals=10)

            probs = {}
            for row in range(match_array.shape[0]):
                for col in range(match_array.shape[1]):
                    probs[(row, col)] = match_array[row, col]

            for g in (2.5,):
                prob = 0
                for k in probs:
                    if sum(k) < g:
                        prob += probs[k]

                if prob*epl_out.iloc[j][str(g) + ' Under'] > thres:
                    f = prob - (1-prob)/(epl_out.iloc[j][str(g) + ' Under']-1)
                    #f = 0.01
                    capital -= f*init_capital
                    if epl_out.iloc[j]['Gospodarze Gole'] + epl_out.iloc[j]['Goście Gole'] < g:
                        capital += f*init_capital*epl_out.iloc[j][str(g) + ' Under']
                    sm_bets += f*init_capital
                    # print(prob, f, epl_out.iloc[j][str(g) + ' Under'], str(g) + ' Under')
                    # print(epl_out.iloc[j]['Gospodarze'], epl_out.iloc[j]['Goście'],
                    #       epl_out.iloc[j]['Gospodarze Gole'], epl_out.iloc[j]['Goście Gole'], capital)
                    # print('********************')

                elif (1-prob)*epl_out.iloc[j][str(g) + ' Over'] > thres:
                    f = (1-prob) - prob/(epl_out.iloc[j][str(g) + ' Over']-1)
                    #f = 0.01
                    capital -= f*init_capital
                    if epl_out.iloc[j]['Gospodarze Gole'] + epl_out.iloc[j]['Goście Gole'] > g:
                        capital += f*init_capital*epl_out.iloc[j][str(g) + ' Over']
                    sm_bets += f*init_capital
                    # print(1-prob, f, epl_out.iloc[j][str(g) + ' Over'], str(g) + ' Over')
                    # print(epl_out.iloc[j]['Gospodarze'], epl_out.iloc[j]['Goście'],
                    #       epl_out.iloc[j]['Gospodarze Gole'], epl_out.iloc[j]['Goście Gole'], capital)
                    # print('********************')
                ct_bets += 1

    print(file, 'final', capital, sm_bets, ct_bets)
#print(poisson_model.summary())


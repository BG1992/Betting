import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson,skellam
from scipy.optimize import minimize
from collections import defaultdict

epl_1718 = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\D2020_2021.csv')
epl_1718 = epl_1718[['HomeTeam','AwayTeam','FTHG','FTAG']]
epl_1718 = epl_1718.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

# epl_1718 = pd.read_csv(r'C:\Users\Marzena\Documents\POL_matches.csv')
# epl_1718 = epl_1718[epl_1718['Season'] == '2018/2019']
# epl_1718 = epl_1718[['Home','Away','HG','AG']]
# epl_1718 = epl_1718.rename(columns={'HG': 'HomeGoals', 'AG': 'AwayGoals', 'Home': 'HomeTeam', 'Away': 'AwayTeam'})

#print(epl_1718.head())

poisson_pred = np.column_stack([[poisson.pmf(i, epl_1718.mean()[j]) for i in range(8)] for j in range(2)])

# fig, ax = plt.subplots(figsize=(9,4))
# # plot histogram of actual goals
# plt.hist(epl_1718[['HomeGoals', 'AwayGoals']].values, range(9),
#          alpha=0.7, label=['Home', 'Away'], density = True, color=["#FFA07A", "#20B2AA"])
#
# # add lines for the Poisson distributions
# pois1, = plt.plot([i-0.5 for i in range(1,9)], poisson_pred[:,0],
#                   linestyle='-', marker='o',label="Home", color = '#CD5C5C')
# pois2, = plt.plot([i-0.5 for i in range(1,9)], poisson_pred[:,1],
#                   linestyle='-', marker='o',label="Away", color = '#006400')
#
# leg=plt.legend(loc='upper right', fontsize=13, ncol=2)
# leg.set_title("Poisson           Actual        ", prop = {'size':'14', 'weight':'bold'})
#
# plt.xticks([i-0.5 for i in range(1,9)],[i for i in range(1,9)])
# plt.xlabel("Goals per Match",size=13)
# plt.ylabel("Proportion of Matches",size=13)
# plt.title("Number of Goals per Match",size=14,fontweight='bold')
# plt.ylim([-0.004, 0.4])
# plt.tight_layout()
# plt.show()

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
pos_ct, ct = 0, 0
thres = 0.5

for i in range(ind_start, epl_1718.shape[0]-9, 9):
    epl_in = epl_1718.iloc[:i]
    epl_out = epl_1718.iloc[i:i+9]

    epl_in.reset_index(inplace=True)
    epl_out.reset_index(inplace=True)

    goal_model_data = pd.concat([epl_in[['HomeTeam','AwayTeam','HomeGoals']].assign(home=1).rename(
                columns={'HomeTeam':'team', 'AwayTeam':'opponent','HomeGoals':'goals'}),
               epl_1718[['AwayTeam','HomeTeam','AwayGoals']].assign(home=0).rename(
                columns={'AwayTeam':'team', 'HomeTeam':'opponent','AwayGoals':'goals'})])

    poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                            family=sm.families.Poisson()).fit()

    for j in range(9):
        match_array = simulate_match(poisson_model, epl_out.iloc[j]['HomeTeam'],
                                     epl_out.iloc[j]['AwayTeam'], max_goals=10)

        probs = {}
        for row in range(match_array.shape[0]):
            for col in range(match_array.shape[1]):
                probs[(row, col)] = match_array[row, col]

        # home, draw, away = 0, 0, 0
        # for k in probs:
        #     if k[0] > k[1]: home += probs[k]
        #     elif k[0] == k[1]: draw += probs[k]
        #     else: away += probs[k]

        # if home > 0.5:
        #     if epl_out.iloc[j]['HomeGoals'] > epl_out.iloc[j]['AwayGoals']: pos_ct += 1
        #     ct += 1
        #     print((home, draw, away), epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #            epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

        # elif home + draw >= 0.75:
        #     if epl_out.iloc[j]['HomeGoals'] >= epl_out.iloc[j]['AwayGoals']: pos_ct += 1
        #     ct += 1
        #     print((home, draw, away), epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #            epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

        # elif away > 0.5:
        #     if epl_out.iloc[j]['HomeGoals'] < epl_out.iloc[j]['AwayGoals']: pos_ct += 1
        #     ct += 1
        #     print((home, draw, away), epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #            epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

        # elif away + draw >= 0.75:
        #     if epl_out.iloc[j]['HomeGoals'] <= epl_out.iloc[j]['AwayGoals']: pos_ct += 1
        #     ct += 1
        #     print((home, draw, away), epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #            epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

        # prob = 0
        # for k in probs:
        #     if sum(k) < 2.5: prob += probs[k]
        #
        # if prob > thres:
        #     if epl_out.iloc[j]['HomeGoals'] + epl_out.iloc[j]['AwayGoals'] < 2.5: pos_ct += 1
        #     ct += 1
        #     print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #           epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)
        #
        # if prob < 1-thres:
        #     if epl_out.iloc[j]['HomeGoals'] + epl_out.iloc[j]['AwayGoals'] > 2.5: pos_ct += 1
        #     ct += 1
        #     print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #           epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

        # prob = 0
        # for k in probs:
        #     if min(k) == 0: prob += probs[k]
        #
        # if prob > thres:
        #     if epl_out.iloc[j]['HomeGoals'] * epl_out.iloc[j]['AwayGoals'] == 0: pos_ct += 1
        #     ct += 1
        #     print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #           epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)
        #
        # if prob < 1-thres:
        #     if epl_out.iloc[j]['HomeGoals'] * epl_out.iloc[j]['AwayGoals'] != 0: pos_ct += 1
        #     ct += 1
        #     print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #           epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

        cts = defaultdict(int)
        for k in probs:
            cts[sum(k)] += probs[k]

        it = list(cts.items())
        it.sort(key= lambda x: -x[1])

        cts_best = []
        prob = 0
        for i in it[:2]:
            cts_best.append(i[0])
            prob += i[1]

        if prob > thres:
            if epl_out.iloc[j]['HomeGoals'] + epl_out.iloc[j]['AwayGoals'] in cts_best: pos_ct += 1
            ct += 1
            print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
                  epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], cts_best)
            print(pos_ct, ct, pos_ct/ct)
            print('*************************')

        # probs = []
        # for row in range(match_array.shape[0]):
        #     for col in range(match_array.shape[1]):
        #         probs.append(((row, col), match_array[row,col]))
        # probs.sort(key= lambda x: -x[1])
        # prob = probs[0][1] + probs[1][1]
        # pairs = [probs[0][0], probs[1][0]]
        # if prob > thres:
        #     if (epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals']) in pairs: pos_ct += 1
        #     ct += 1
        #     print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #           epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'])
        #     print(probs[:2])
        #     print(pos_ct, ct, pos_ct/ct)
        #     print('************')
        # if prob < 1-thres:
        #     if epl_out.iloc[j]['HomeGoals'] + epl_out.iloc[j]['AwayGoals'] in (1,2): pos_ct += 1
        #     ct += 1
        #     print(prob, epl_out.iloc[j]['HomeTeam'], epl_out.iloc[j]['AwayTeam'],
        #           epl_out.iloc[j]['HomeGoals'], epl_out.iloc[j]['AwayGoals'], pos_ct, ct, pos_ct/ct)

print(pos_ct, ct, pos_ct/ct, 1.05*ct/pos_ct)
#print(poisson_model.summary())


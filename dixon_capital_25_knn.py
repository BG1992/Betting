import pandas as pd
import numpy as np
from scipy.stats import poisson
import os
import csv
import statsmodels.api as sm
import statsmodels.formula.api as smf
from time import perf_counter
from collections import defaultdict
from statsmodels.stats.proportion import proportion_confint

def simulate_match(foot_model, homeTeam, awayTeam, max_goals=10):
    home_goals_avg = foot_model.predict(pd.DataFrame(data={'team': homeTeam,
                    'opponent': awayTeam,'home':1}, index=[1])).values[0]
    away_goals_avg = foot_model.predict(pd.DataFrame(data={'team': awayTeam,
                     'opponent': homeTeam,'home':0}, index=[1])).values[0]
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)]
                 for team_avg in [home_goals_avg, away_goals_avg]]
    return (np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

abbrevs = {'B':'Belgium', 'D': 'Germany', 'E': 'England', 'F': 'France',
           'I': 'Italy', 'N': 'Netherlands', 'P': 'Portugal', 'SC': 'Scotland', 'SP': 'Spain'}

files = os.listdir(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history')
# files = ('SC2019_2020.csv', 'SP2012_2013.csv', 'SP2013_2014.csv', 'SP2014_2015.csv', 'SP2015_2016.csv',
#          'SP2017_2018.csv', 'SP2019_2020.csv', 'SWE.csv', 'SWZ.csv', 'USA.csv')

probs_knn_dict = defaultdict(list)
with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_prob_estimation_summary.csv', newline='') as sm_file:
    reader = csv.reader(sm_file, delimiter=',')
    next(reader)
    for row in reader:
        if 'under' in row[2]: probs_knn_dict[row[0]].append((float(row[3]), float(row[4])))

for k in probs_knn_dict:
    probs_knn_dict[k].sort(key= lambda x: x[0])

def find_prob(key, p, delta=0.025, alpha=0.05):
    pos_ct, ct = 0, 0
    for i in range(len(probs_knn_dict[key])):
        if abs(p - probs_knn_dict[key][i][0]) < delta:
            pos_ct += probs_knn_dict[key][i][1]
            ct += 1
    if ct > 30: return proportion_confint(pos_ct, ct, alpha)
    else: return (0,1)

capital = 0
init_capital = 100
sm_bets = 0

for file in files:

    probs = []
    df = pd.read_csv(os.path.join(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history', file), encoding='latin1')
    if '_' in file:
        country = abbrevs[file.replace(file.replace('.csv', '')[-9:], '')[:-4]]
        season = file.replace('.csv', '')[-9:].replace('_', '/')
        if 'BbAv<2.5' in df.columns:
            df = df[['HomeTeam','AwayTeam','FTHG','FTAG', 'BbAv<2.5', 'BbAv>2.5']]
            df = df.rename(columns={'FTHG': 'Gospodarze Gole', 'FTAG': 'Goście Gole', 'HomeTeam': 'Gospodarze',
                                    'AwayTeam': 'Goście', 'BbAv<2.5': 'Avg25u', 'BbAv>2.5': 'Avg25o'})
        elif 'Avg<2.5' in df.columns:
            df = df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'Avg<2.5', 'Avg>2.5']]
            df = df.rename(columns={'FTHG': 'Gospodarze Gole', 'FTAG': 'Goście Gole', 'HomeTeam': 'Gospodarze',
                                    'AwayTeam': 'Goście', 'Avg<2.5': 'Avg25u', 'Avg>2.5': 'Avg25o'})

        df.reset_index(inplace=True)
        ind_start = 100

        for i in range(ind_start, df.shape[0]-9, 9):
            df_in = df.iloc[:i]
            df_out = df.iloc[i:i+9]

            df_in.reset_index(inplace=True)
            df_out.reset_index(inplace=True)

            goal_model_data = pd.concat([df_in[['Gospodarze','Goście','Gospodarze Gole']].assign(home=1).rename(
                        columns={'Gospodarze':'team', 'Goście':'opponent','Gospodarze Gole':'goals'}),
                       df[['Goście','Gospodarze','Goście Gole']].assign(home=0).rename(
                        columns={'Goście':'team', 'Gospodarze':'opponent','Goście Gole':'goals'})])

            poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                    family=sm.families.Poisson()).fit()

            for j in range(9):
                match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                             df_out.iloc[j]['Goście'], max_goals=10)
                prob = 0
                for h in range(3):
                    for a in range(3):
                        if h+a < 2.5: prob += match_array[h,a]

                conf_int = find_prob(country, prob)
                if conf_int[0]*df_out.iloc[j]['Avg25u'] > 1.02:
                    f = conf_int[0] - (1-conf_int[0])/(df_out.iloc[j]['Avg25u']-1)
                    capital -= f*init_capital/5
                    if df_out.iloc[j]['Gospodarze Gole'] + df_out.iloc[j]['Goście Gole'] < 2.5:
                        capital += f*init_capital*df_out.iloc[j]['Avg25u']/5
                    sm_bets += f*init_capital/5
                    # print(df_out.iloc[j]['Gospodarze'], df_out.iloc[j]['Goście'],
                    #       df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole'],
                    #       conf_int[0], df_out.iloc[j]['Avg25u'], '2.5 under', f, capital)

                if (1-conf_int[1])*df_out.iloc[j]['Avg25o'] > 1.02:
                    f = (1-conf_int[1]) - (1-(1-conf_int[1]))/(df_out.iloc[j]['Avg25o']-1)
                    capital -= f*init_capital/5
                    if df_out.iloc[j]['Gospodarze Gole'] + df_out.iloc[j]['Goście Gole'] > 2.5:
                        capital += f*init_capital*df_out.iloc[j]['Avg25o']/10
                    sm_bets += f*init_capital/5
                    # print(df_out.iloc[j]['Gospodarze'], df_out.iloc[j]['Goście'],
                    #       df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole'],
                    #       (1-conf_int[1]), df_out.iloc[j]['Avg25o'], '2.5 over', f, capital)

        print(country, season, capital, sm_bets)
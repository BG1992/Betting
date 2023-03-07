import pandas as pd
import numpy as np
from scipy.stats import poisson
import os
import csv
import statsmodels.api as sm
import statsmodels.formula.api as smf
from time import perf_counter

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

with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_prob_estimation_summary.csv', 'w', newline='') as sm_file:
    writer = csv.writer(sm_file)
    writer.writerow(['Country', 'Season', 'Bet', 'Prob_estimated', 'Outcome'])

st = perf_counter()
for file in files:

    print(file, round(perf_counter() - st, 2))
    probs = []
    df = pd.read_csv(os.path.join(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history', file), encoding='latin1')
    if '_' in file:
        country = abbrevs[file.replace(file.replace('.csv', '')[-9:], '')[:-4]]
        season = file.replace('.csv', '')[-9:].replace('_', '/')
        df = df[['HomeTeam','AwayTeam','FTHG','FTAG']]
        df = df.rename(columns={'FTHG': 'Gospodarze Gole', 'FTAG': 'Goście Gole', 'HomeTeam': 'Gospodarze',
                                'AwayTeam': 'Goście'})
        dfs = [df]
    else:
        country = df.iloc[0]['Country']
        df = df[['Season', 'Home','Away','HG','AG']]
        df = df.rename(columns={'HG': 'Gospodarze Gole', 'AG': 'Goście Gole', 'Home': 'Gospodarze',
                                'Away': 'Goście'})
        dfs = []
        for season in set(df['Season']):
            dfs.append(df[df['Season'] == season])

    for df in dfs:

        df.reset_index(inplace=True)
        ind_start = 100

        if '_' not in file: season = df.iloc[0]['Season']

        for i in range(ind_start, df.shape[0]-9, 9):
            df_in = df.iloc[:i]
            df_out = df.iloc[i:i+9]

            df_in.reset_index(inplace=True)
            df_out.reset_index(inplace=True)

            goal_model_data = pd.concat([df_in[['Gospodarze','Goście','Gospodarze Gole']].assign(home=1).rename(
                        columns={'Gospodarze':'team', 'Goście':'opponent','Gospodarze Gole':'goals'}),
                       df_in[['Goście','Gospodarze','Goście Gole']].assign(home=0).rename(
                        columns={'Goście':'team', 'Gospodarze':'opponent','Goście Gole':'goals'})])

            try:
                poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                        family=sm.families.Poisson()).fit()

                for j in range(9):
                    try:
                        match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                                     df_out.iloc[j]['Goście'], max_goals=10)

                        probs102_3 = [0,0,0] #1,x,2
                        probs102_2 = [0,0,0] #10,02,12
                        probs_bts = 0 #y
                        probs_goals_under = [0,0,0,0] #1.5,2.5,3.5,4.5
                        probs_goals_ct = [0]*9 #0-8
                        #probs_accurate_score = {}

                        for h in range(match_array.shape[0]):
                            for a in range(match_array.shape[1]):
                                #1x2 three-way
                                if h>a: probs102_3[0] += match_array[h,a]
                                elif h==a: probs102_3[1] += match_array[h,a]
                                else: probs102_3[2] += match_array[h,a]
                                #1x2 two-way
                                if h>=a: probs102_2[0] += match_array[h,a]
                                if h<=a: probs102_2[1] += match_array[h,a]
                                if h!=a: probs102_2[2] += match_array[h,a]
                                #bts
                                if h*a>0: probs_bts += match_array[h,a]
                                #goals under
                                if h+a < 1.5: probs_goals_under[0] += match_array[h,a]
                                if h+a < 2.5: probs_goals_under[1] += match_array[h,a]
                                if h+a < 3.5: probs_goals_under[2] += match_array[h,a]
                                if h+a < 4.5: probs_goals_under[3] += match_array[h,a]
                                #goals count
                                for k in range(9):
                                    if h+a == k: probs_goals_ct[k] += match_array[h,a]
                                #accurate score
                                #probs_accurate_score[(h, a)] = match_array[h,a]

                        probs.append([country, season, '1x2_3', probs102_3[0],
                                        1 if df_out.iloc[j]['Gospodarze Gole'] > df_out.iloc[j]['Goście Gole'] else 0])

                        probs.append([country, season, '1x2_3', probs102_3[1],
                                        1 if df_out.iloc[j]['Gospodarze Gole'] == df_out.iloc[j]['Goście Gole'] else 0])

                        probs.append([country, season, '1x2_3', probs102_3[2],
                                         1 if df_out.iloc[j]['Gospodarze Gole'] < df_out.iloc[j]['Goście Gole'] else 0])

                        probs.append([country, season, '1x2_2', probs102_2[0],
                                      1 if df_out.iloc[j]['Gospodarze Gole'] >= df_out.iloc[j]['Goście Gole'] else 0])

                        probs.append([country, season, '1x2_2', probs102_2[1],
                                      1 if df_out.iloc[j]['Gospodarze Gole'] <= df_out.iloc[j]['Goście Gole'] else 0])

                        probs.append([country, season, 'bts', probs_bts,
                                      1 if df_out.iloc[j]['Gospodarze Gole']*df_out.iloc[j]['Goście Gole'] != 0 else 0])

                        goals_under_tp = (1.5, 2.5, 3.5, 4.5)
                        for k in range(len(goals_under_tp)):
                            probs.append([country, season, str(goals_under_tp[k]) + ' under', probs_goals_under[k],
                                          1 if df_out.iloc[j]['Gospodarze Gole'] + df_out.iloc[j]['Goście Gole']
                                          < goals_under_tp[k] else 0])

                        for k in range(len(probs_goals_ct)):
                            probs.append([country, season, str(k) + ' exact', probs_goals_ct[k],
                                          1 if df_out.iloc[j]['Gospodarze Gole'] + df_out.iloc[j]['Goście Gole']
                                               == k else 0])
                    except: pass
            except: pass

    with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_prob_estimation_summary.csv', 'a', newline='') as sm_file:
        writer = csv.writer(sm_file)
        for row in probs:
            writer.writerow(row)
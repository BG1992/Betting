import pandas as pd
import numpy as np
from scipy.stats import poisson
import os
import csv
import statsmodels.api as sm
import statsmodels.formula.api as smf
from time import perf_counter
from collections import defaultdict
from random import shuffle
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
files = list(filter(lambda x: x != 'test', files))
# files = ('SC2019_2020.csv', 'SP2012_2013.csv', 'SP2013_2014.csv', 'SP2014_2015.csv', 'SP2015_2016.csv',
#          'SP2017_2018.csv', 'SP2019_2020.csv', 'SWE.csv', 'SWZ.csv', 'USA.csv')
rows = []
for file in files:

    pos_ct = 0
    ct = 0
    pos_ct_random = 0
    ct_random = 0
    df = pd.read_csv(os.path.join(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history', file), encoding='latin1')
    if '_' in file:
        country = abbrevs[file.replace(file.replace('.csv', '')[-9:], '')[:-4]]
        season = file.replace('.csv', '')[-9:].replace('_', '/')
        df = df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
        df = df.rename(columns={'FTHG': 'Gospodarze Gole', 'FTAG': 'Goście Gole', 'HomeTeam': 'Gospodarze',
                                'AwayTeam': 'Goście'})

        df.reset_index(inplace=True)
        ind_start = 40

        for i in range(ind_start, df.shape[0]-9, 9):
            df_in = df.iloc[:i]
            df_out = df.iloc[i:i+9]

            df_in.reset_index(inplace=True)
            df_out.reset_index(inplace=True)

            try:
                goal_model_data = pd.concat([df_in[['Gospodarze','Goście','Gospodarze Gole']].assign(home=1).rename(
                            columns={'Gospodarze':'team', 'Goście':'opponent','Gospodarze Gole':'goals'}),
                           df[['Goście','Gospodarze','Goście Gole']].assign(home=0).rename(
                            columns={'Goście':'team', 'Gospodarze':'opponent','Goście Gole':'goals'})])

                poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                        family=sm.families.Poisson()).fit()

                for j in range(9):
                    match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                                 df_out.iloc[j]['Goście'], max_goals=10)
                    probs = defaultdict(float)
                    for h in range(10):
                        for a in range(10):
                            if h>a:
                                probs['H'] += match_array[h,a]
                                probs['HD'] += match_array[h,a]
                                probs['HA'] += match_array[h,a]
                            elif h==a:
                                probs['D'] += match_array[h,a]
                                probs['HD'] += match_array[h,a]
                                probs['DA'] += match_array[h,a]
                            else:
                                probs['A'] += match_array[h,a]
                                probs['HA'] += match_array[h,a]
                                probs['DA'] += match_array[h,a]
                            for g in (0.5, 1.5, 2.5, 3.5, 4.5):
                                if h+a<g: probs['<' + str(g)] += match_array[h,a]
                                else: probs['>' + str(g)] += match_array[h,a]

                    score = (df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole'])
                    for p in probs:
                        if 'H' in p:
                            if score[0] > score[1]:
                                rows.append([p, i, probs[p], 1])
                            else:
                                rows.append([p, i, probs[p], 0])
                        elif 'D' in p:
                            if score[0] == score[1]:
                                rows.append([p, i, probs[p], 1])
                            else:
                                rows.append([p, i, probs[p], 0])
                        elif 'A' in p:
                            if score[0] < score[1]:
                                rows.append([p, i, probs[p], 1])
                            else:
                                rows.append([p, i, probs[p], 0])
                        else:
                            g = float(p[1:])
                            if p[0] == '<':
                                if sum(score) < g:
                                    rows.append([p, i, probs[p], 1])
                                else:
                                    rows.append([p, i, probs[p], 0])
                            elif p[0] == '>':
                                if sum(score) > g:
                                    rows.append([p, i, probs[p], 1])
                                else:
                                    rows.append([p, i, probs[p], 0])
            except: pass

    else:
        country = df.iloc[0]['Country']
        df = df[['Season', 'Date', 'Home', 'Away', 'HG', 'AG']]
        df = df.rename(columns={'HG': 'Gospodarze Gole', 'AG': 'Goście Gole', 'Home': 'Gospodarze',
                                'Away': 'Goście'})

        dfs = []
        for season in set(df['Season']):
            dfs.append(df[df['Season'] == season])

        for df in dfs:
            df.reset_index(inplace=True)
            ind_start = 40
            pos_ct, ct = 0, 0
            season = df.iloc[0]['Season']

            if '/' in str(season):
                for i in range(ind_start, df.shape[0]-9, 9):
                    df_in = df.iloc[:i]
                    df_out = df.iloc[i:i + 9]

                    df_in.reset_index(inplace=True)
                    df_out.reset_index(inplace=True)

                    try:
                        goal_model_data = pd.concat([df_in[['Gospodarze', 'Goście', 'Gospodarze Gole']].assign(home=1).rename(
                            columns={'Gospodarze': 'team', 'Goście': 'opponent', 'Gospodarze Gole': 'goals'}),
                            df_in[['Goście', 'Gospodarze', 'Goście Gole']].assign(home=0).rename(
                                columns={'Goście': 'team', 'Gospodarze': 'opponent', 'Goście Gole': 'goals'})])

                        poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                                family=sm.families.Poisson()).fit()

                        for j in range(9):
                            match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                                         df_out.iloc[j]['Goście'], max_goals=10)
                            probs = defaultdict(float)
                            for h in range(10):
                                for a in range(10):
                                    if h > a:
                                        probs['H'] += match_array[h, a]
                                        probs['HD'] += match_array[h, a]
                                        probs['HA'] += match_array[h, a]
                                    elif h == a:
                                        probs['D'] += match_array[h, a]
                                        probs['HD'] += match_array[h, a]
                                        probs['DA'] += match_array[h, a]
                                    else:
                                        probs['A'] += match_array[h, a]
                                        probs['HA'] += match_array[h, a]
                                        probs['DA'] += match_array[h, a]
                                    for g in (0.5, 1.5, 2.5, 3.5, 4.5):
                                        if h + a < g:
                                            probs['<' + str(g)] += match_array[h, a]
                                        else:
                                            probs['>' + str(g)] += match_array[h, a]
                                    if h*a == 0: probs['BTSN'] += match_array[h, a]
                                    if h*a != 0: probs['BTSY'] += match_array[h, a]

                            score = (df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole'])
                            for p in probs:
                                if 'H' in p:
                                    if score[0] > score[1]:
                                        rows.append([p, i, probs[p], 1])
                                    else:
                                        rows.append([p, i, probs[p], 0])
                                elif 'D' in p:
                                    if score[0] == score[1]:
                                        rows.append([p, i, probs[p], 1])
                                    else:
                                        rows.append([p, i, probs[p], 0])
                                elif 'A' in p:
                                    if score[0] < score[1]:
                                        rows.append([p, i, probs[p], 1])
                                    else:
                                        rows.append([p, i, probs[p], 0])
                                elif 'BTSN' in p:
                                    if score[0]*score[1] == 0:
                                        rows.append([p, i, probs[p], 1])
                                    else:
                                        rows.append([p, i, probs[p], 0])
                                elif 'BTSY' in p:
                                    if score[0]*score[1] != 0:
                                        rows.append([p, i, probs[p], 1])
                                    else:
                                        rows.append([p, i, probs[p], 0])
                                else:
                                    g = float(p[1:])
                                    if p[0] == '<':
                                        if sum(score) < g:
                                            rows.append([p, i, probs[p], 1])
                                        else:
                                            rows.append([p, i, probs[p], 0])
                                    elif p[0] == '>':
                                        if sum(score) > g:
                                            rows.append([p, i, probs[p], 1])
                                        else:
                                            rows.append([p, i, probs[p], 0])
                    except: pass

with open('dixon_safe_summary2.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    for row in rows:
        writer.writerow(row)
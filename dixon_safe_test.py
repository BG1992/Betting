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

np.set_printoptions(precision=3, suppress=True)

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

files = os.listdir(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history\test2')
#files = ['B2021_2022.csv']
# files = ('SC2019_2020.csv', 'SP2012_2013.csv', 'SP2013_2014.csv', 'SP2014_2015.csv', 'SP2015_2016.csv',
#          'SP2017_2018.csv', 'SP2019_2020.csv', 'SWE.csv', 'SWZ.csv', 'USA.csv')

probs_knn_dict = defaultdict(list)
with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_safe_summary2.csv', newline='') as sm_file:
    reader = csv.reader(sm_file, delimiter=';')
    next(reader)
    for row in reader:
        probs_knn_dict[row[0]].append((int(row[1]), float(row[2]), int(row[3])))

def find_prob(key, ind, p, delta=0.025, alpha=0.05):
    pos_ct, ct = 0, 0
    for i in range(len(probs_knn_dict[key])):
        if abs(ind - probs_knn_dict[key][i][0]) < 10 and abs(p - probs_knn_dict[key][i][1]) < delta:
            pos_ct += probs_knn_dict[key][i][2]
            ct += 1
    if ct > 30: return proportion_confint(pos_ct, ct, alpha)
    else: return (0,1)

for file in files:

    pos_ct = 0
    ct = 0
    df = pd.read_csv(os.path.join(r'C:\Users\Marzena\PycharmProjects\DS\dixon_history\test2',
                                  file), encoding='latin1')

    if '_' in file:
        country = abbrevs[file.replace(file.replace('.csv', '')[-9:], '')[:-4]]
        season = file.replace('.csv', '')[-9:].replace('_', '/')
        df = df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
        df = df.rename(columns={'FTHG': 'Gospodarze Gole', 'FTAG': 'Goście Gole', 'HomeTeam': 'Gospodarze',
                                'AwayTeam': 'Goście'})

        df.reset_index(inplace=True)

        for i in range(df.shape[0]):
            if pd.isna(df.iloc[i]['Gospodarze Gole']):
                ind_start = i
                break

        df_in = df.iloc[:ind_start]
        df_out = df.iloc[ind_start:]

        df_in.reset_index(inplace=True)
        df_out.reset_index(inplace=True)

        goal_model_data = pd.concat([df_in[['Gospodarze', 'Goście', 'Gospodarze Gole']].assign(home=1).rename(
            columns={'Gospodarze': 'team', 'Goście': 'opponent', 'Gospodarze Gole': 'goals'}),
            df_in[['Goście', 'Gospodarze', 'Goście Gole']].assign(home=0).rename(
                columns={'Goście': 'team', 'Gospodarze': 'opponent', 'Goście Gole': 'goals'})])

        poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                family=sm.families.Poisson()).fit()

        for j in range(df_out.shape[0]):
            match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                         df_out.iloc[j]['Goście'], max_goals=10)
            bet_probs = defaultdict(float)
            for h in range(10):
                for a in range(10):
                    if h > a: bet_probs['H'] += match_array[h,a]
                    elif h == a: bet_probs['D'] += match_array[h,a]
                    else: bet_probs['A'] += match_array[h,a]
                    for g in (0.5, 1.5, 2.5, 3.5, 4.5):
                        if h+a < g: bet_probs[str(g)] += match_array[h,a]
                    if h == 0 or a == 0:
                        bet_probs['BTSN'] += match_array[h, a]
                    else:
                        bet_probs['BTSY'] += match_array[h, a]

            bet_probs['HD'] = bet_probs['H'] + bet_probs['D']
            bet_probs['HA'] = bet_probs['H'] + bet_probs['A']
            bet_probs['DA'] = bet_probs['D'] + bet_probs['A']
            row = [df_out.iloc[j]['Gospodarze'] + ' - ' + df_out.iloc[j]['Goście']]
            for b in ('H', 'D', 'A', 'HD', 'DA', 'HA', '0.5', '1.5', '2.5', '3.5', '4.5', 'BTSY', 'BTSN'):
                if '.' in b:
                    prob_low = find_prob('<' + b, ind_start, bet_probs[b])[0]
                    row.append(round(prob_low, 4))

                    prob_low = find_prob('>' + b, ind_start, 1 - bet_probs[b])[0]
                    row.append(round(prob_low, 4))
                else:
                    prob_low = find_prob(b, ind_start, bet_probs[b])[0]
                    row.append(round(prob_low, 4))
            print(row)

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
            for i in range(df.shape[0]):
                if pd.isna(df.iloc[i]['Gospodarze Gole']):
                    ind_start = i
                    break
            season = df.iloc[0]['Season']

            if '/' in str(season):
                df_in = df.iloc[:ind_start]
                df_out = df.iloc[ind_start:]

                df_in.reset_index(inplace=True)
                df_out.reset_index(inplace=True)

                goal_model_data = pd.concat([df_in[['Gospodarze', 'Goście', 'Gospodarze Gole']].assign(home=1).rename(
                    columns={'Gospodarze': 'team', 'Goście': 'opponent', 'Gospodarze Gole': 'goals'}),
                    df_in[['Goście', 'Gospodarze', 'Goście Gole']].assign(home=0).rename(
                        columns={'Goście': 'team', 'Gospodarze': 'opponent', 'Goście Gole': 'goals'})])

                poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                        family=sm.families.Poisson()).fit()

                for j in range(df_out.shape[0]):
                    match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                                 df_out.iloc[j]['Goście'], max_goals=10)
                    bet_probs = defaultdict(float)
                    for h in range(10):
                        for a in range(10):
                            if h > a:
                                bet_probs['H'] += match_array[h, a]
                            elif h == a:
                                bet_probs['D'] += match_array[h, a]
                            else:
                                bet_probs['A'] += match_array[h, a]
                            for g in (0.5, 1.5, 2.5, 3.5, 4.5):
                                if h + a < g: bet_probs[str(g)] += match_array[h, a]
                            if h == 0 or a == 0:
                                bet_probs['BTSN'] += match_array[h,a]
                            else:
                                bet_probs['BTSY'] += match_array[h,a]

                    bet_probs['HD'] = bet_probs['H'] + bet_probs['D']
                    bet_probs['HA'] = bet_probs['H'] + bet_probs['A']
                    bet_probs['DA'] = bet_probs['D'] + bet_probs['A']
                    row = [df_out.iloc[j]['Gospodarze'] + ' - ' + df_out.iloc[j]['Goście']]
                    for b in ('H', 'D', 'A', 'HD', 'DA', 'HA', '0.5', '1.5', '2.5', '3.5', '4.5', 'BTSY', 'BTSN'):
                        if '.' in b:
                            prob_low = find_prob('<' + b, ind_start, bet_probs[b])[0]
                            row.append(round(prob_low, 4))

                            prob_low = find_prob('>' + b, ind_start, 1 - bet_probs[b])[0]
                            row.append(round(prob_low, 4))
                        else:
                            prob_low = find_prob(b, ind_start, bet_probs[b])[0]
                            row.append(round(prob_low, 4))
                    print(row)

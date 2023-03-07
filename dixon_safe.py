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

probs_knn_dict = defaultdict(list)
with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_prob_estimation_summary.csv', newline='') as sm_file:
    reader = csv.reader(sm_file, delimiter=',')
    next(reader)
    for row in reader:
        if 'under' in row[2]: probs_knn_dict[row[0]].append((float(row[3]), float(row[4])))

for k in probs_knn_dict:
    probs_knn_dict[k].sort(key= lambda x: x[0])

pos_all = 0
ct_all = 0
prob_thres = 0.75
avgs = []
avgs_random = []
main_p = 0
main_ct = 0

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

        for i in range(ind_start, 48, 9):
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
                    probs = []
                    for h in range(10):
                        for a in range(10):
                            if (h, a) == (df_out.iloc[j]['Gospodarze'],
                                                 df_out.iloc[j]['Goście']): main_p += match_array[h,a]
                            probs.append([(h,a), match_array[h,a]])
                    main_ct += 1
                    probs.sort(key= lambda x: -x[1])
                    scores = set()
                    cum_prob = 0
                    for p in probs:
                        if cum_prob + p[1] < prob_thres:
                            cum_prob += p[1]
                            scores.add(p[0])
                        else:
                            break
                    if (df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole']) in scores:
                        pos_ct += 1
                    ct += 1
                    shuffle(probs)
                    scores = set()
                    cum_prob = 0
                    for p in probs:
                        if cum_prob + p[1] < prob_thres:
                            cum_prob += p[1]
                            scores.add(p[0])
                        else:
                            break
                    if (df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole']) in scores:
                        pos_ct_random += 1
                        pos_all += 1
                    ct_random += 1
                    ct_all += 1
            except: pass

        if ct > 1:
            print(country, season, pos_ct/ct, pos_ct_random/ct_random)
            avgs.append(pos_ct/ct)
            avgs_random.append(pos_ct_random/ct_random)

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
                for i in range(ind_start, 48, 9):
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
                            probs = []
                            for h in range(10):
                                for a in range(10):
                                    probs.append([(h, a), match_array[h, a]])

                            probs.sort(key=lambda x: -x[1])
                            scores = set()
                            cum_prob = 0
                            for p in probs:
                                if cum_prob + p[1] < prob_thres:
                                    cum_prob += p[1]
                                    scores.add(p[0])
                                else:
                                    break
                            if (df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole']) in scores:
                                pos_ct += 1
                            ct += 1
                            shuffle(probs)
                            scores = set()
                            cum_prob = 0
                            for p in probs:
                                if cum_prob + p[1] < prob_thres:
                                    cum_prob += p[1]
                                    scores.add(p[0])
                                else:
                                    break
                            if (df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole']) in scores:
                                pos_ct_random += 1
                                pos_all += 1
                            ct_random += 1
                            ct_all += 1
                    except: pass

                if ct > 1:
                    print(country, season, pos_ct/ct, pos_ct_random/ct_random)
                    avgs.append(pos_ct / ct)
                    avgs_random.append(pos_ct_random/ct_random)

print(np.mean(avgs), np.std(avgs))
print(np.mean(avgs_random), np.std(avgs_random))
print(pos_all/ct_all)
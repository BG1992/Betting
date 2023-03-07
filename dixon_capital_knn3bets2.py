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
from functools import reduce
import datetime as dt
from itertools import combinations


def simulate_match(foot_model, homeTeam, awayTeam, max_goals=10):
    home_goals_avg = foot_model.predict(pd.DataFrame(data={'team': homeTeam,
                    'opponent': awayTeam,'home':1}, index=[1])).values[0]
    away_goals_avg = foot_model.predict(pd.DataFrame(data={'team': awayTeam,
                     'opponent': homeTeam,'home':0}, index=[1])).values[0]
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)]
                 for team_avg in [home_goals_avg, away_goals_avg]]
    return (np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

countries_dict = {'bundesliga': 'Germany', 'laliga': 'Spain', 'ligue-1': 'France', 'pko-bp-ekstraklasa': 'Poland',
             'premier-league': 'England', 'serie-a': 'Italy'}

files = os.listdir(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_ou')

probs_knn_dict = defaultdict(list)
with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_prob_estimation_summary.csv', newline='') as sm_file:
    reader = csv.reader(sm_file, delimiter=',')
    next(reader)
    for row in reader:
        probs_knn_dict[row[0]].append((float(row[3]), float(row[4])))

for k in probs_knn_dict:
    probs_knn_dict[k].sort(key= lambda x: x[0])

def find_prob(key, p, delta=0.01, alpha=0.01):
    pos_ct, ct = 0, 0
    for i in range(len(probs_knn_dict[key])):
        if abs(p - probs_knn_dict[key][i][0]) < delta:
            pos_ct += probs_knn_dict[key][i][1]
            ct += 1
    if ct > 30: return proportion_confint(pos_ct, ct, alpha)
    else: return (0,1)

capital = 100
init_capital = 100
sm_bets = 0
ct_bets = 0

dfs = []
for file in ['pko-bp-ekstraklasa-2020-2021.csv']: #files:

    years = (int(file.replace('.csv', '').split('-')[-2]), int(file.replace('.csv', '').split('-')[-1]))
    df = pd.read_csv(os.path.join(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_ou',file), encoding='utf-8')
    df['Kraj'] = countries_dict[file.replace('-2020-2021.csv', '')]
    df['Data2'] = pd.to_datetime(dt.datetime(2000, 12, 31).date())
    df.drop(columns=['Unnamed: 0'], inplace=True)
    last_m = int(df.iloc[0]['Data'][3:5])
    y = years[1]
    for i in range(df.shape[0]):
        d, m = int(df.iloc[i]['Data'][:2]), int(df.iloc[i]['Data'][3:5])
        if m > last_m:
            y = years[0]
        else:
            last_m = m
        df.loc[i, 'Data2'] = pd.to_datetime(dt.datetime(y, m, d).date())
    df['Data'] = df['Data2']
    df.drop(columns=['Data2'], inplace = True)
    df['Gospodarze Gole'] = pd.to_numeric(df['Gospodarze Gole'])
    df['Goście Gole'] = pd.to_numeric(df['Goście Gole'])

    dfs.append(df)

df = reduce(lambda left, right: pd.concat([left, right], ignore_index=True), dfs)
df.sort_values(by=['Data'], inplace=True)
df.reset_index(inplace=True, drop=True)

countries = set(df['Kraj'])
ind_start = 100
del dfs

dates = list(set(df['Data']))
dates.sort()

for dt in dates:
    bets_to_do = []
    init_capital = capital
    for country in countries:

        df_country = df[df['Kraj'] == country]
        df_in = df_country[df_country['Data'] < dt]
        df_out = df_country[df_country['Data'] == dt]

        if df_in.shape[0] >= 100:

            df_in.reset_index(inplace=True)
            df_out.reset_index(inplace=True)

            goal_model_data = pd.concat([df_in[['Gospodarze','Goście','Gospodarze Gole']].assign(home=1).rename(
                        columns={'Gospodarze':'team', 'Goście':'opponent','Gospodarze Gole':'goals'}),
                       df_in[['Goście','Gospodarze','Goście Gole']].assign(home=0).rename(
                        columns={'Goście':'team', 'Gospodarze':'opponent','Goście Gole':'goals'})])

            try:
                poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                        family=sm.families.Poisson()).fit()

                for j in range(df_out.shape[0]):
                    match_array = simulate_match(poisson_model, df_out.iloc[j]['Gospodarze'],
                                                 df_out.iloc[j]['Goście'], max_goals=10)

                    for g in (3.5,):

                        prob = 0
                        for h in range(match_array.shape[0]):
                            for a in range(match_array.shape[1]):
                                if h+a < g: prob += match_array[h,a]

                        conf_int = find_prob(country, prob)
                        if prob*df_out.iloc[j][str(g) + 'u_avg'] > 1.03 \
                                and df_out.iloc[j][str(g) + 'u_avg'] > 1.3 and \
                            df_out.iloc[j][str(g) + 'u_avg'] < 2:
                            bets_to_do.append((df_out.iloc[j]['Gospodarze'], df_out.iloc[j]['Goście'],
                                   df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole'],
                            str(g) + ' under', prob, df_out.iloc[j][str(g) + 'u_avg'],
                                               df_in.shape[0]/df_country.shape[0]))

                        conf_int = find_prob(country, 1-prob)
                        if (1-prob) * df_out.iloc[j][str(g) + 'o_avg'] > 1.03 \
                                and df_out.iloc[j][str(g) + 'o_avg'] > 1.3 and \
                            df_out.iloc[j][str(g) + 'o_avg'] < 2:
                            bets_to_do.append((df_out.iloc[j]['Gospodarze'], df_out.iloc[j]['Goście'],
                                   df_out.iloc[j]['Gospodarze Gole'], df_out.iloc[j]['Goście Gole'],
                               str(g) + ' over', 1-prob, df_out.iloc[j][str(g) + 'o_avg'],
                                               df_in.shape[0]/df_country.shape[0]))
            except: pass

            #print(dt, len(bets_to_do))

    if len(bets_to_do) >= 1:
        bets3 = []
        for comb in combinations(bets_to_do, 1):
            #if comb[0][:4] != comb[1][:4] and comb[0][:4] != comb[2][:4] and comb[1][:4] != comb[2][:4]:
            #   bets3.append([comb[0], comb[1], comb[2]])
            bets3.append(comb)

        for bet3 in bets3:
            p = 1
            r = 1
            win = True
            for bet in bet3:
                p *= bet[5]
                r *= bet[6]
                for g in (3.5,):
                    if bet[4] == str(g) + ' under':
                        if bet[2] + bet[3] > g: win = False
                    if bet[4] == str(g) + ' over':
                        if bet[2] + bet[3] < g: win = False
            p = 1.02/r
            f = (p - (1-p)/(r-1))
            #f = 1/100
            b = f*capital
            capital -= b
            if win: capital += b*r
            print(bet3[0][:4], p, round(r,2), bet3[0][4], win, f, capital, b)
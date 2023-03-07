import pandas as pd
from sklearn.linear_model import LogisticRegression
import scipy.optimize as sc
from random import uniform
from collections import defaultdict
import scipy.optimize as sc

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\pko-bp-ekstraklasa-2020-2021.csv')
matches = []
odds = {}
df = df.fillna(0)

for i in range(df.shape[0]-1,-1,-1):
    matches.append([df.iloc[i].loc['Gospodarze'], df.iloc[i].loc['Goście'],
                    df.iloc[i].loc['Gospodarze Gole'], df.iloc[i].loc['Goście Gole']])
    odds[i] = {}
    for g in ('0.5', '1.5', '2.5', '3.5', '4.5', '5.5', '6.5'):
        odds[i][g + ' Under'] = df.iloc[i].loc[g + ' Under']
        odds[i][g + ' Over'] = df.iloc[i].loc[g + ' Over']

teams_set = set()
matches = matches[::-1]
for m in matches:
    teams_set.add(m[0])
    teams_set.add(m[1])

all_pos_ct, all_ct = 0, 0
capital = 1000
N = 100
thres = 1.3
ind_start = 5*len(teams_set)//2

pos_ct, ct = 0, 0
for i in range(ind_start, len(matches)-len(teams_set)//2, len(teams_set)//2):
    teams_attack, teams_def, teams_overall_attack, teams_overall_def = defaultdict(list), \
                                               defaultdict(list), defaultdict(int), defaultdict(int)

    teams_attack_mean, teams_def_mean = defaultdict(float), defaultdict(float)
    for m in matches[:i]:
        teams_overall_attack[m[0]] += m[2]
        teams_overall_attack[m[1]] += m[3]
        teams_overall_def[m[0]] += m[3]
        teams_overall_def[m[1]] += m[2]

    for m in matches[:i]:
        teams_attack[m[0]].append([m[2], teams_overall_def[m[1]]])
        teams_attack[m[1]].append([m[3], teams_overall_def[m[0]]])
        teams_def[m[0]].append([m[3], teams_overall_attack[m[1]]])
        teams_def[m[1]].append([m[2], teams_overall_attack[m[0]]])

    for t in teams_attack:
        teams_attack[t] = pop_weights(teams_attack[t], 'attack')
    for t in teams_def:
        teams_def[t] = pop_weights(teams_def[t], 'def')

    for t in teams_attack:
        teams_attack_mean[t] = w_mean(teams_attack[t])

    for t in teams_def:
        teams_def_mean[t] = w_mean(teams_def[t])


    for m in matches[i:i+len(teams_set)//2]:
        ind = matches.index(m)
        probs = []
        goals = defaultdict(float)
        scores = [0,0,0]
        for g_home in range(8):
            p_home = calc_prob(teams_attack_mean[m[0]], teams_def_mean[m[1]], g_home)
            #print(g_home, p_home)
            for g_away in range(8):
                p_away = calc_prob(teams_attack_mean[m[1]], teams_def_mean[m[0]], g_away)
                probs.append([(g_home, g_away), p_home*p_away])
                goals[g_home + g_away] += p_home*p_away
                if g_home > g_away: scores[0] += p_home*p_away
                elif g_home == g_away: scores[1] += p_home*p_away
                else: scores[2] += p_home*p_away

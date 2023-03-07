import pandas as pd
from collections import defaultdict
from random import uniform
import numpy as np

def pop_weights(goals, mode):
    sm = sum(map(lambda x: x[1], goals))
    if mode == 'attack':
        for i in range(len(goals)):
            goals[i][1] = (sm-goals[i][1])
    sm = sum(map(lambda x: x[1], goals))
    for i in range(len(goals)):
        goals[i][1] /= sm
    return goals

def w_mean(goals):
    sm = 0
    for i in range(len(goals)):
        sm += goals[i][0]*goals[i][1]
    return sm

def w_std(goals):
    sm = 0
    wm = w_mean(goals)
    for i in range(len(goals)):
        sm += goals[i][1]*(goals[i][0] - wm)**2
    return pow(sm, 0.5)

paths = [
        r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\pko-bp-ekstraklasa-2018-2019.csv',
        r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\pko-bp-ekstraklasa-2019-2020.csv',
        r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\pko-bp-ekstraklasa-2020-2021.csv']

max_out = 0
max_C = 0
max_thres = 0
max_frac = 1

for k in range(100):

    C = uniform(0.2, 1.5)
    thres = uniform(1.3, 1.6)
    frac = uniform(0.001, 0.1)
    #out = 1
    capitals = []
    pos_ct = 0
    ct = 0

    for path in paths:
        df = pd.read_csv(path)
        matches = []
        odds = {}
        df = df.fillna(0)

        for i in range(df.shape[0]):
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
            #print(m)

        ind_start = 5*len(teams_set)//2
        capital = 1

        for i in range(ind_start, len(matches)-len(teams_set)//2, len(teams_set)//2):
            teams_attack, teams_def, teams_overall_attack, teams_overall_def = defaultdict(list), \
                                                       defaultdict(list), defaultdict(int), defaultdict(int)
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

            for m in matches[i:i+len(teams_set)//2]:
                ind = matches.index(m)
                mn = 0.5*(w_mean(teams_attack[m[0]]) + w_mean(teams_def[m[1]]))
                std = pow(0.5*(w_std(teams_attack[m[0]])**2 + w_std(teams_def[m[1]])**2), 0.5)
                left_under = mn + C*std
                mn = 0.5*(w_mean(teams_attack[m[1]]) + w_mean(teams_def[m[0]]))
                std = pow(0.5*(w_std(teams_attack[m[1]])**2 + w_std(teams_def[m[0]])**2), 0.5)
                right_under =  mn + C*std
                if str(int(left_under + right_under) + 0.5) + ' Under' in odds[ind]:
                    if odds[ind][str(int(left_under + right_under) + 0.5) + ' Under'] > thres:
                        if left_under + right_under > m[2] + m[3]:
                            capital += (0.95*odds[ind][str(int(left_under + right_under) + 0.5) + ' Under']-1)*capital*frac
                            pos_ct += 1
                        else:
                            capital -= capital*frac
                        ct += 1
        #out *= capital
        capitals.append(capital)

    out = np.mean(capitals) - 1.5*np.std(capitals)
    if out > max_out:
        max_out = out
        max_C = C
        max_thres = thres
        max_frac = frac
        print(k, max_out, capitals)
        print(max_C, max_thres, max_frac)
        print(pos_ct, ct, pos_ct/ct)
        print('******************')

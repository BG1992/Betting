import pandas as pd
from collections import defaultdict
from math import exp, factorial, log
from random import uniform
import scipy.optimize as sc

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\pko-bp-ekstraklasa-2018-2019.csv')
matches = []
odds = {}
df = df.fillna(0)

def calc_prob(x_mean, y_mean, n):
    return pow((x_mean+y_mean)/2, n)*exp(-(x_mean+y_mean)/2)/factorial(n)

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

for i in range(df.shape[0]):
    matches.append([df.iloc[i].loc['Gospodarze'], df.iloc[i].loc['Goście'],
                    df.iloc[i].loc['Gospodarze Gole'], df.iloc[i].loc['Goście Gole'], df.iloc[i].loc['3.5 Under']])

teams_set = set()
matches = matches[::-1]
for m in matches:
    teams_set.add(m[0])
    teams_set.add(m[1])
    #print(m)

ind_start = 12*len(teams_set)//2
goals_bnd = 4
prob_lower = 0.9

pos_ct, ct = 0, 0
for i in range(ind_start, len(matches)-len(teams_set)//2, len(teams_set)//2):
    lambdas, lambdas_inds = {}, {}
    curr_ind = 0
    for t in teams_set:
        lambdas_inds[(t, 'A')] = curr_ind
        curr_ind += 1

        lambdas_inds[(t, 'D')] = curr_ind
        curr_ind += 1

    curr_matches = matches[:i]

    for m in curr_matches:
        left_sm_m = x[lambdas_inds[(m[0], 'A')]] + x[lambdas_inds[(m[0], 'AH')]] + x[lambdas_inds[(m[1], 'D')]]
        sm += -left_sm_m+log(left_sm_m)*m[2]-log(factorial(m[2]))
        right_sm_m = x[lambdas_inds[(m[1], 'A')]] + x[lambdas_inds[(m[0], 'D')]] + x[lambdas_inds[(m[0], 'DH')]]
        sm += -right_sm_m+log(right_sm_m)*m[3]-log(factorial(m[3]))
        return -sm

    its = list(lambdas_inds.items())
    for it in its:
        lambdas[it[0]] = res.x[it[1]]

    for m in matches[i:i+len(teams_set)//2]:
        ind = matches.index(m)
        probs = []
        goals = defaultdict(float)
        for g_home in range(8):
            left_sm_m = (lambdas[(m[0], 'A')] + lambdas[(m[1], 'D')])/2
            p_home = exp(-left_sm_m)*pow(left_sm_m, g_home)/factorial(g_home)
            #print(g_home, p_home)
            for g_away in range(8):
                right_sm_m = (lambdas[(m[1], 'A')] + lambdas[(m[0], 'D')])/2
                p_away = exp(-right_sm_m)*pow(right_sm_m, g_away)/factorial(g_away)

                probs.append([(g_home, g_away), p_home*p_away])
                goals[g_home + g_away] += p_home*p_away

        goals_list = list(goals.items())
        goals_list.sort(key= lambda x: -x[1])
        p = goals_list[0][1] + goals_list[1][1]
        if p > 0.55:
            if goals_list[0][0] == m[2] + m[3] or goals_list[1][0] == m[2] + m[3]:
                pos_ct += 1
            ct += 1
            print(goals_list[0])
            print(goals_list[1])
            print(p)
            print(m)
            print(pos_ct, ct, pos_ct / ct)

        # p = 0
        # for j in range(goals_bnd):
        #     p += goals[j]
        # if p > prob_lower:
        #     if m[2]+m[3] < goals_bnd:
        #         pos_ct += 1
        #         print(m)
        #         print(p)
        #         ct += 1
        #         print(pos_ct, ct, pos_ct/ct)
        #     else:
        #         ct += 1
        #         print(m)
        #         print(p)
        #         print(pos_ct, ct, pos_ct / ct)

# for el in lambdas:
#     print(el, lambdas[el])

print('****************************************')
print(pos_ct, ct, pos_ct / ct, ct / pos_ct * 1.05)
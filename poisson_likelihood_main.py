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
                    df.iloc[i].loc['Gospodarze Gole'], df.iloc[i].loc['Goście Gole']])
    odds[df.shape[0]-1-i] = {}
    for g in ('0.5', '1.5', '2.5', '3.5', '4.5', '5.5', '6.5'):
        odds[df.shape[0]-1-i][g + ' Under'] = df.iloc[i].loc[g + ' Under']
        odds[df.shape[0]-1-i][g + ' Over'] = df.iloc[i].loc[g + ' Over']

teams_set = set()
matches = matches[::-1]
for m in matches:
    teams_set.add(m[0])
    teams_set.add(m[1])
    #print(m)

all_pos_ct, all_ct = 0, 0
C_under, C_over = 0.5, 0.5
ind_start = 8*len(teams_set)//2
pos_cter = defaultdict(int)
cter = defaultdict(int)
capital_under, capital_over = 1000, 1000
capital = 1000
N = 100
thres = 1.3

pos_ct, ct = 0, 0
for i in range(ind_start, len(matches)-len(teams_set)//2, len(teams_set)//2):
    lambdas, lambdas_inds = {}, {}
    curr_ind = 0
    for t in teams_set:
        #lambdas[(t, 'A')] = uniform(0, 4)
        lambdas_inds[(t, 'A')] = curr_ind
        curr_ind += 1

        #lambdas[(t, 'H')] = uniform(0, 2)
        lambdas_inds[(t, 'AH')] = curr_ind
        curr_ind += 1

        #lambdas[(t, 'D')] = uniform(0, 4)
        lambdas_inds[(t, 'D')] = curr_ind
        curr_ind += 1

        lambdas_inds[(t, 'DH')] = curr_ind
        curr_ind += 1

    curr_matches = matches[:i]

    def f(x):
        sm = 0
        for m in curr_matches:
            left_sm_m = x[lambdas_inds[(m[0], 'A')]] + x[lambdas_inds[(m[0], 'AH')]] + x[lambdas_inds[(m[1], 'D')]]
            sm += -left_sm_m+log(left_sm_m)*m[2]-log(factorial(m[2]))
            right_sm_m = x[lambdas_inds[(m[1], 'A')]] + x[lambdas_inds[(m[0], 'D')]] + x[lambdas_inds[(m[0], 'DH')]]
            sm += -right_sm_m+log(right_sm_m)*m[3]-log(factorial(m[3]))
            #print(sm)
        return -sm

    res = sc.minimize(f, x0=[uniform(0.01,4) for _ in range(len(lambdas_inds))], method='L-BFGS-B',
                      bounds=[(0.01,None) for _ in range(len(lambdas_inds))])

    its = list(lambdas_inds.items())
    for it in its:
        lambdas[it[0]] = res.x[it[1]]

    for m in matches[i:i+len(teams_set)//2]:
        ind = matches.index(m)
        probs = []
        goals = defaultdict(float)
        scores = [0,0,0]
        for g_home in range(8):
            left_sm_m = lambdas[(m[0], 'A')] + lambdas[(m[0], 'AH')] + lambdas[(m[1], 'D')]
            p_home = exp(-left_sm_m)*pow(left_sm_m, g_home)/factorial(g_home)
            #print(g_home, p_home)
            for g_away in range(8):
                right_sm_m = lambdas[(m[1], 'A')] + lambdas[(m[0], 'D')] + lambdas[(m[0], 'DH')]
                p_away = exp(-right_sm_m)*pow(right_sm_m, g_away)/factorial(g_away)

                probs.append([(g_home, g_away), p_home*p_away])
                goals[g_home + g_away] += p_home*p_away
                if g_home > g_away: scores[0] += p_home*p_away
                elif g_home == g_away: scores[1] += p_home*p_away
                else: scores[2] += p_home*p_away

        # probs.sort(key=lambda x: -x[1])
        # if probs[0][1]+probs[1][1] > 0.25:
        #     if probs[0][0] == (m[2], m[3]) or probs[1][0] == (m[2], m[3]): #or probs[2][0] == (m[2], m[3]):
        #         pos_ct += 1
        #         print(m)
        #         print(probs[0])
        #         #print(probs[1])
        #         #print(probs[2])
        #         ct += 1
        #         print(pos_ct, ct, pos_ct/ct, ct/pos_ct*1.05)
        #     else:
        #         ct += 1

        # goals_list = list(goals.items())
        # goals_list.sort(key= lambda x: -x[1])
        # if goals_list[0][1]+goals_list[1][1] > 0.53:
        #     if goals_list[0][0] == m[2]+m[3] or goals_list[1][0] == m[2]+m[3]:
        #         pos_ct += 1
        #         ct += 1
        #         print(m)
        #         print(goals_list[0])
        #         print(goals_list[1])
        #         print(pos_ct, ct, pos_ct / ct, ct / pos_ct * 1.05)
        #     else:
        #         ct += 1

        # print(m)
        # p = 0
        # g_max, odds_p_max, odds_max, tp = None, 0, 0, None
        # for g in range(6):
        #     p += goals[g]
        #     if odds[ind][str(g + 0.5) + ' Under'] > thres:
        #         if odds[ind][str(g + 0.5) + ' Under']*p > odds_p_max:
        #             g_max = g + 0.5
        #             odds_p_max = odds[ind][str(g + 0.5) + ' Under']*p
        #             odds_max = odds[ind][str(g + 0.5) + ' Under']
        #             tp = 'U'
        #     if odds[ind][str(g + 0.5) + ' Over'] > thres:
        #         if odds[ind][str(g + 0.5) + ' Over']*p > odds_p_max:
        #             g_max = g + 0.5
        #             odds_p_max = odds[ind][str(g + 0.5) + ' Over']*p
        #             odds_max = odds[ind][str(g + 0.5) + ' Over']
        #             tp = 'O'
        # print(m[2]+m[3], g_max, odds_p_max, odds_max, capital)
        # if odds_p_max > 1:
        #     if tp == 'U':
        #         if m[2]+m[3] < g_max+0.5:
        #             capital += (capital/100)*(0.95*odds_max - 1)
        #         else:
        #             capital -= capital/100
        #     else:
        #         if m[2]+m[3] > g_max+0.5:
        #             capital += (capital/100)*(0.95*odds_max - 1)
        #         else:
        #             capital -= capital/100


        #vals = list(goals.items())
        #vals.sort(key= lambda x: -x[1])

        # df = 0
        # for j in range(len(scores)):
        #     if scores[j] == max(scores):
        #         df += abs(1-scores[j])
        #     else:
        #         df += abs(scores[j])
        # if df < 5/6:
        #     if scores[0] == max(scores):
        #         if m[2] > m[3]: pos_ct += 1
        #     elif scores[1] == max(scores):
        #         if m[2] == m[3]: pos_ct += 1
        #     else:
        #         if m[2] < m[3]: pos_ct += 1
        #     ct += 1
        #     print(m)
        #     print(scores)
        #     print(pos_ct, ct, pos_ct/ct)
        #     print('**********************')

        p = 0
        for j in range(4):
            p += goals[j]
        if p > 0.9:
            if m[2]+m[3] < 3.5:
                pos_ct += 1
                print(m)
                # print(goals[0])
                # print(goals[1])
                # print(goals[2])
                # print(goals[3])
                print(p)
                ct += 1
                print(pos_ct, ct, pos_ct/ct)
            else:
                ct += 1
                print(m)
                print(p)
                print(pos_ct, ct, pos_ct / ct)


#print(capital)


for el in lambdas:
    print(el, lambdas[el])

print('****************************************')
print(pos_ct, ct, pos_ct / ct, ct / pos_ct * 1.05)
import pandas as pd
from collections import defaultdict
from math import exp, factorial

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_score_odds_seasons\bundesliga-2020-2021.csv')
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
    odds[df.shape[0]-1-i]['odds_1'] = df.iloc[i].loc['odds_1']
    odds[df.shape[0]-1-i]['odds_0'] = df.iloc[i].loc['odds_0']
    odds[df.shape[0]-1-i]['odds_2'] = df.iloc[i].loc['odds_2']

teams_set = set()
matches = matches[::-1]
for m in matches:
    teams_set.add(m[0])
    teams_set.add(m[1])
    #print(m)

all_pos_ct, all_ct = 0, 0
C_under, C_over = 0.5, 0.5
ind_start = 5*len(teams_set)//2
pos_cter = defaultdict(int)
cter = defaultdict(int)
capital_under, capital_over = 1000, 1000
capital = 1000
N = 100
thres = 1.3

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
        #probs.sort(key=lambda x: -x[1])

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
        #         if odds[ind][str(g + 0.5) + ' Over']*(1-p) > odds_p_max:
        #             g_max = g + 0.5
        #             odds_p_max = odds[ind][str(g + 0.5) + ' Over']*(1-p)
        #             odds_max = odds[ind][str(g + 0.5) + ' Over']
        #             tp = 'O'
        # print(m[2]+m[3], g_max, odds_p_max, odds_max, tp, capital)
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


        vals = list(goals.items())
        vals.sort(key= lambda x: -x[1])

        odds_probs = [scores[0]*odds[ind]['odds_1'], scores[1]*odds[ind]['odds_0'], scores[2]*odds[ind]['odds_2']]
        mp = 0
        prob = 0
        score_picked = None
        for i in range(len(odds_probs)):
            if scores[i] > prob:
                mp = odds_probs[i]
                if i == 0: score_picked = 'Home'
                elif i == 1: score_picked = 'Draw'
                elif i == 2: score_picked = 'Away'
                prob = scores[i]
        if mp > 1.5:
            if score_picked == 'Home':
                if m[2] > m[3]:
                    capital += (capital/100)*(0.95*odds[ind]['odds_1'] - 1)
                    pos_ct += 1
                else:
                    capital -= (capital/100)
            elif score_picked == 'Draw':
                if m[2] == m[3]:
                    capital += (capital/100)*(0.95*odds[ind]['odds_0'] - 1)
                    pos_ct += 1
                else:
                    capital -= (capital/100)
            elif score_picked == 'Away':
                if m[2] < m[3]:
                    capital += (capital/100)*(0.95*odds[ind]['odds_2'] - 1)
                    pos_ct += 1
                else:
                    capital -= (capital/100)
            ct += 1
            print(scores, score_picked)
            print([odds[ind]['odds_1'], odds[ind]['odds_0'], odds[ind]['odds_2']])
            print(odds_probs)
            print(pos_ct, ct, pos_ct/ct)
            print(m, capital)
            print('**********************')

print(capital)
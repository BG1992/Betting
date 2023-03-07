import pandas as pd
from collections import defaultdict

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_weighted_seasons\bundesliga-2020-2021.csv')
matches = []
odds = {}
df = df.fillna(0)

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

all_pos_ct, all_ct = 0, 0
C_under, C_over = 0.5, 0.5
ind_start = 5*len(teams_set)//2
pos_cter = defaultdict(int)
cter = defaultdict(int)
capital_under, capital_over = 1000, 1000
N = 100
thres = 1.3

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

    pos_ct, ct = 0, 0
    for m in matches[i:i+len(teams_set)//2]:
        ind = matches.index(m)
        mn = 0.5*(w_mean(teams_attack[m[0]]) + w_mean(teams_def[m[1]]))
        std = pow(0.5*(w_std(teams_attack[m[0]])**2 + w_std(teams_def[m[1]])**2), 0.5)
        left_under, left_over = mn + C_under*std, mn - C_over*std
        # if mn + C*std > m[2]:
        #     pos_ct += 1
        #     print(mn + C*std, m[2])
        # ct += 1
        mn = 0.5*(w_mean(teams_attack[m[1]]) + w_mean(teams_def[m[0]]))
        std = pow(0.5*(w_std(teams_attack[m[1]])**2 + w_std(teams_def[m[0]])**2), 0.5)
        right_under, right_over = mn + C_under*std, mn - C_over*std
        # if mn + C*std > m[3]:
        #     pos_ct += 1
        #     #print(mn + C*std, m[3])
        # ct += 1
        if odds[ind][str(int(left_under + right_under) + 0.5) + ' Under'] > thres:
            if left_under + right_under > m[2] + m[3]:
                all_pos_ct += 1
                capital_under += (0.95*odds[ind][str(int(left_under + right_under) + 0.5) + ' Under']-1)*capital_over/N
            else:
                capital_under -= capital_under/N
            all_ct += 1
        if odds[ind][str(int(left_over + right_over) + 0.5) + ' Over'] > thres:
            if left_over + right_over < m[2] + m[3]:
                all_pos_ct += 1
                capital_over += (0.95*odds[ind][str(int(left_over + right_over) + 0.5) + ' Over']-1)*capital_over/N
            else:
                capital_over -= capital_over/N
            all_ct += 1

    print(i, capital_under + capital_over, capital_under, capital_over, all_pos_ct, all_ct, all_pos_ct/all_ct)

print(all_pos_ct/all_ct, 1.05*all_ct/all_pos_ct)
print(capital_under, capital_over, capital_under + capital_over)

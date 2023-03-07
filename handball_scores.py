import csv
import os
import numpy as np
from collections import defaultdict

foldername = r'C:\Users\Marzena\PycharmProjects\DS\handball_scores'
files = os.listdir(foldername)

h = 0.5
a = 1-h
std_coef = 0.9

probs = {}
for f in files:
    if '2021-2022' not in f:
        rows = []
        teams = set()
        pos_ct_lower, pos_ct_upper = 0, 0
        ct_lower, ct_upper = 0, 0
        pos_ct_both_lower, pos_ct_both_upper = 0, 0
        ct_both_lower, ct_both_upper = 0, 0
        with open(os.path.join(foldername, f)) as g:
            reader = csv.reader(g, delimiter=';')
            for row in reader:
                if row[1] in ('Po karn.', 'Po dogr.'):
                    try: rows.append([row[2], row[3], int(row[6])+int(row[8]), int(row[7])+int(row[9])])
                    except: pass
                    teams.add(row[2])
                    teams.add(row[3])
                elif row[1] not in ('Walkower', 'Anulowane'):
                    rows.append([row[1], row[2], int(row[3]), int(row[4])])
                    teams.add(row[1])
                    teams.add(row[2])
        rows = rows[::-1]
        scores_achieved = defaultdict(list)
        scores_lost = defaultdict(list)
        dists = []
        dists2 = []
        for k in range(10*len(teams)//2):
            row = rows[k]
            scores_achieved[row[0]].append(row[2])
            scores_achieved[row[1]].append(row[3])
            scores_lost[row[0]].append(row[3])
            scores_lost[row[1]].append(row[2])
        for k in range(10*len(teams)//2, len(rows), len(teams)//2):
            new_scores_achieved = scores_achieved.copy()
            new_scores_lost = scores_lost.copy()
            for j in range(k, min(k+len(teams)//2, len(rows))):
                row = rows[j]
                if len(scores_achieved[row[0]]) >= 5 and len(scores_achieved[row[1]]) >= 5 \
                        and len(scores_lost[row[0]]) >= 5 and len(scores_lost[row[1]]) >= 5:
                    home_interval = (h*(np.mean(scores_achieved[row[0]]) - std_coef*np.std(scores_achieved[row[0]])) +
                                     a*(np.mean(scores_lost[row[1]]) - std_coef*np.std(scores_lost[row[1]])),
                                     h*(np.mean(scores_achieved[row[0]]) + std_coef*np.std(scores_achieved[row[0]])) +
                                     a*(np.mean(scores_lost[row[1]]) + std_coef*np.std(scores_lost[row[1]])))
                    away_interval = (h*(np.mean(scores_achieved[row[1]]) - std_coef*np.std(scores_achieved[row[1]])) +
                                     a*(np.mean(scores_lost[row[0]]) - std_coef*np.std(scores_lost[row[0]])),
                                     h*(np.mean(scores_achieved[row[1]]) + std_coef*np.std(scores_achieved[row[1]])) +
                                     a*(np.mean(scores_lost[row[0]]) + std_coef*np.std(scores_lost[row[0]])))
                    dists.append(home_interval[1] - home_interval[0])
                    dists.append(away_interval[1] - away_interval[0])
                    dists2.append(home_interval[1] + away_interval[1] - home_interval[0] - away_interval[0])

                    if row[2] > home_interval[0]: pos_ct_lower += 1
                    ct_lower += 1
                    if row[2] < home_interval[1]: pos_ct_upper += 1
                    ct_upper += 1
                    if row[3] > away_interval[0]: pos_ct_lower += 1
                    ct_lower += 1
                    if row[3] < away_interval[1]: pos_ct_upper += 1
                    ct_upper += 1
                    #print(row, (home_interval[0] + away_interval[0], home_interval[1] + away_interval[1]))
                    if row[2] + row[3] > home_interval[0] + away_interval[0]: pos_ct_both_lower += 1
                    ct_both_lower += 1
                    if row[2] + row[3] < home_interval[1] + away_interval[1]: pos_ct_both_upper += 1
                    ct_both_upper += 1

                new_scores_achieved[row[0]].append(row[2])
                new_scores_achieved[row[1]].append(row[3])
                new_scores_lost[row[0]].append(row[3])
                new_scores_lost[row[1]].append(row[2])

            scores_achieved = new_scores_achieved.copy()
            scores_lost = new_scores_lost.copy()
        probs[f] = (pos_ct_lower, ct_lower, pos_ct_upper, ct_upper,
                    pos_ct_both_lower, ct_both_lower, pos_ct_both_upper, ct_both_upper)
        print(f, pos_ct_lower, ct_lower, pos_ct_lower/ct_lower, pos_ct_upper, ct_upper, pos_ct_upper/ct_upper)

probs_lower, probs_upper = [], []
probs_both_lower, probs_both_upper = [], []
for p in probs:
    probs_lower.append(probs[p][0]/probs[p][1])
    probs_upper.append(probs[p][2]/probs[p][3])
    probs_both_lower.append(probs[p][4]/probs[p][5])
    probs_both_upper.append(probs[p][6]/probs[p][7])

print(np.mean(probs_lower), np.std(probs_lower))
print(np.mean(probs_upper), np.std(probs_upper))
print(np.mean(probs_both_lower), np.std(probs_both_lower))
print(np.mean(probs_both_upper), np.std(probs_both_upper))
print(np.mean(dists), np.std(dists))
print(np.mean(dists2), np.std(dists2))
import csv
import os
import numpy as np
from collections import defaultdict

foldername = r'C:\Users\Marzena\PycharmProjects\DS\handball_scores'
files = os.listdir(foldername)

h = 0.5
a = 1-h
std_coef = 0.65

probs = {}
for f in ['bundesliga-2007-2008.csv', 'bundesliga-2008-2009.csv', 'bundesliga-2009-2010.csv',
          'bundesliga-2010-2011.csv', 'bundesliga-2011-2012.csv', 'bundesliga-2012-2013.csv',
          'bundesliga-2013-2014.csv', 'bundesliga-2014-2015.csv', 'bundesliga-2015-2016.csv',
          'bundesliga-2016-2017.csv', 'bundesliga-2017-2018.csv', 'bundesliga-2018-2019.csv',
          'bundesliga-2019-2020.csv', 'bundesliga-2020-2021.csv', 'extraliga-2011-2012.csv',
          'extraliga-2012-2013.csv', 'extraliga-2013-2014.csv', 'extraliga-2014-2015.csv',
          'extraliga-2015-2016.csv', 'extraliga-2016-2017.csv', 'extraliga-2017-2018.csv',
          'extraliga-2018-2019.csv', 'extraliga-2019-2020.csv', 'extraliga-2020-2021.csv',
          'liga-asobal-2011-2012.csv', 'liga-asobal-2012-2013.csv', 'liga-asobal-2013-2014.csv',
          'liga-asobal-2014-2015.csv', 'liga-asobal-2015-2016.csv', 'liga-asobal-2016-2017.csv',
          'liga-asobal-2017-2018.csv', 'liga-asobal-2018-2019.csv', 'liga-asobal-2019-2020.csv',
          'liga-asobal-2020-2021.csv', 'liga-nationala-2012-2013.csv', 'liga-nationala-2013-2014.csv',
          'liga-nationala-2014-2015.csv', 'liga-nationala-2015-2016.csv', 'liga-nationala-2016-2017.csv',
          'liga-nationala-2017-2018.csv', 'liga-nationala-2018-2019.csv', 'liga-nationala-2019-2020.csv',
          'liga-nationala-2020-2021.csv']:
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
                    try: rows.append([row[2], row[3], int(row[8]), int(row[9])])
                    except: pass
                    teams.add(row[2])
                    teams.add(row[3])
                elif row[1] not in ('Walkower', 'Anulowane'):
                    try: rows.append([row[1], row[2], int(row[7]), int(row[8])])
                    except: pass
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
                    dists2.append(home_interval[1] + away_interval[1] - home_interval[0] - away_interval[0])

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
        probs[f] = (pos_ct_both_lower, ct_both_lower, pos_ct_both_upper, ct_both_upper)
        print(f, pos_ct_both_lower, ct_both_lower, pos_ct_both_lower/ct_both_lower,
              pos_ct_both_upper, ct_both_upper, pos_ct_both_upper/ct_both_upper)

probs_both_lower, probs_both_upper = [], []
for p in probs:
    probs_both_lower.append(probs[p][0]/probs[p][1])
    probs_both_upper.append(probs[p][2]/probs[p][3])

print(np.mean(probs_both_lower), np.std(probs_both_lower))
print(np.mean(probs_both_upper), np.std(probs_both_upper))
print(np.mean(dists2), np.std(dists2))
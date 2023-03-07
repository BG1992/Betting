import csv
from collections import defaultdict
from statsmodels.stats.proportion import proportion_confint
import numpy as np

probs = defaultdict(list)
with open(r'C:\Users\Marzena\PycharmProjects\DS\dixon_prob_estimation_summary.csv', newline='') as sm_file:
    reader = csv.reader(sm_file, delimiter=',')
    next(reader)
    for row in reader:
        probs[row[0]].append((float(row[3]), float(row[4])))
        # if 'exact' in row[2]: probs['exact'].append((float(row[3]), float(row[4])))
        # elif 'under' in row[2]: probs['under'].append((float(row[3]), float(row[4])))
        # else: probs[row[2]].append((float(row[3]), float(row[4])))

for k in probs:
    probs[k].sort(key= lambda x: x[0])

def find_prob(key, p, delta=0.025, alpha=0.05):
    pos_ct, ct = 0, 0
    for i in range(len(probs[key])):
        if abs(p - probs[key][i][0]) < delta:
            pos_ct += probs[key][i][1]
            ct += 1
    if ct > 20:
        return (pos_ct, ct, pos_ct/ct, proportion_confint(pos_ct, ct, alpha))

for key in probs:
    print(key)
    for p in np.arange(0,1,0.02):
        print(p, find_prob(key, p))
    print('**************')
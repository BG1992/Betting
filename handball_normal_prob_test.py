import csv
import numpy as np
from statsmodels.stats.proportion import proportion_confint

rows = []
with open('Handball_est.csv', newline='') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        if row[1] == 'False': rows.append((float(row[0]), 0))
        else: rows.append((float(row[0]), 1))

rows.sort(key=lambda x: x[0])

delta = 0.02
alpha = 0.05

for i in np.arange(0, 1, 0.02):
    pos_ct, ct = 0, 0
    for j in range(len(rows)):
        if abs(rows[j][0] - i) < delta:
            pos_ct += rows[j][1]
            ct += 1
    print(i, pos_ct, ct, pos_ct/ct, proportion_confint(pos_ct, ct, alpha))
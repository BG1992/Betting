import csv
import scipy.optimize as sc_opt
from math import factorial, log

matches = []
with open(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_seasons\ekstraklasa\ekstraklasa1920.csv') as f:
    reader = csv.reader(f)
    k = 0
    m = ()
    for row in reader:
        if k % 3 != 2:
            m += (row[0],)
        else:
            m += (int(row[0][0]),int(row[0][-1]))
            matches.append(m)
            m = ()
        k += 1

matches = list(reversed(matches))
train, test = matches[int(0.8*len(matches)):], matches[:int(0.8*len(matches))]

elos = {}
for m in matches:
    elos[m[0]] = 2000
    elos[m[1]] = 2000

K = 32
for m in train:
    E_left, E_right = 1/(1+pow(10, (elos[m[1]] - elos[m[0]])/400)), 1/(1+pow(10, (elos[m[0]] - elos[m[1]])/400))
    if m[2] > m[3]:
        elos[m[0]] += K*(1-E_left)
        elos[m[1]] += K*(0-E_right)
    elif m[2] == m[3]:
        elos[m[0]] += K*(0.5-E_left)
        elos[m[1]] += K*(0.5-E_right)
    else:
        elos[m[0]] += K*(0-E_left)
        elos[m[1]] += K*(1-E_right)

pos_ct, ct = 0, 0
thres = 70
for m in test:
    print(m + (elos[m[0]], elos[m[1]]))
    E_left, E_right = 1/(1+pow(10, (elos[m[1]] - elos[m[0]])/400)), 1/(1+pow(10, (elos[m[0]] - elos[m[1]])/400))
    if m[2] > m[3]:
        if elos[m[0]] - elos[m[1]] > thres: pos_ct += 1
        elos[m[0]] += K*(1-E_left)
        elos[m[1]] += K*(0-E_right)
    elif m[2] == m[3]:
        #if abs(elos[m[0]] - elos[m[1]]) < thres: pos_ct += 1
        elos[m[0]] += K*(0.5-E_left)
        elos[m[1]] += K*(0.5-E_right)
    else:
        if elos[m[0]] - elos[m[1]] < -thres: pos_ct += 1
        elos[m[0]] += K*(0-E_left)
        elos[m[1]] += K*(1-E_right)
    if abs(elos[m[0]] - elos[m[1]]) > thres: ct += 1

print(pos_ct, ct, pos_ct/ct)
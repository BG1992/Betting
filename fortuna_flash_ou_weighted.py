import csv
import statsmodels.stats.proportion as sm
import numpy as np
import fortuna_helper as fh

data = []
data_path = 'C://Users//Marzena//PycharmProjects//DS//flashscore_ous.csv'
with open(data_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    for row in reader:
        if row[2] == 'o':
            data.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[1])), 1])
            data.append([float(row[1]), fh.calc_equilibrium(float(row[0]), float(row[1])), 0])
        else:
            data.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[1])), 0])
            data.append([float(row[1]), fh.calc_equilibrium(float(row[0]), float(row[1])), 1])

# data = np.array(data)
# m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
# m1, d1 = np.mean(data[:,1]), np.std(data[:,1])
#
# for k in range(data.shape[0]):
#     data[k,0] -= m0
#     data[k,0] /= d0
#     data[k,1] -= m1
#     data[k,1] /= d1

def knn_sm_area(rate, a):
    #_rate = ((rate[0] - m0)/d0, (rate[1] - m1)/d1)
    positive = 0
    ct = 0
    sm_plus = 0
    sm_minus = 0
    for row in data:
        if abs(row[0] - rate[0]) <= 0.05 and abs(row[1] - rate[1]) <= 0.005:
            if row[2] == 1:
                positive += 1
                sm_plus += (rate[0]-1)
            else:
                sm_minus += 1
            ct += 1
    if ct < 10: return positive, ct, (0, 1), -100
    s = sm.proportion_confint(positive, ct, a)
    return positive, ct, s, (sm_plus*s[0] - sm_minus*(1-s[0]))/ct

alpha = 0.01
rates = [(1.65, 2.13), (1.42, 2.69), (1.6, 2.3)]
for r in rates:
    k = knn_sm_area((r[0], fh.calc_equilibrium(r[0], r[1])), alpha)
    print(r, k)

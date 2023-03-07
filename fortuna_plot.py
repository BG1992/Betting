import csv
import numpy as np
import fortuna_helper as fh
import matplotlib.pyplot as plt
import statsmodels.stats.proportion as sm

data = []
data_path = 'C://Users//Marzena//Documents//fortuna 09112020.csv'
with open(data_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        _score = fh.get_score(row[-1])
        data.append(fh.new_bet(float(row[0]), float(row[4]), bet='1', score=_score))
        data.append(fh.new_bet(float(row[1]), float(row[5]), bet='0', score=_score))
        data.append(fh.new_bet(float(row[2]), float(row[3]), bet='2', score=_score))
        if row[6] != '':
            data.append(fh.new_bet(float(row[6]), float(row[7]), bet='goals', score=_score, under=0.5))
        if row[8] != '':
            data.append(fh.new_bet(float(row[8]), float(row[9]), bet='goals', score=_score, under=1.5))
        if row[10] != '':
            data.append(fh.new_bet(float(row[10]), float(row[11]), bet='goals', score=_score, under=2.5))
        if row[12] != '':
            data.append(fh.new_bet(float(row[12]), float(row[13]), bet='goals', score=_score, under=3.5))
        if row[14] != '':
            data.append(fh.new_bet(float(row[14]), float(row[15]), bet='goals', score=_score, under=4.5))
        if row[16] != '':
            data.append(fh.new_bet(float(row[16]), float(row[17]), bet='goals', score=_score, under=5.5))
        if row[18] != '':
            data.append(fh.new_bet(float(row[18]), float(row[19]), bet='goals', score=_score, under=6.5))

data_test = []
data_test_path = 'C://Users//Marzena//Documents//fortuna 10112020 test.csv'
with open(data_test_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        if row[0] != row[4]: data_test.append([float(row[0]), float(row[4]), '1', row[-1]])
        if row[1] != row[5]: data_test.append([float(row[1]), float(row[5]), '0', row[-1]])
        if row[2] != row[3]: data_test.append([float(row[2]), float(row[3]), '2', row[-1]])
        for i in range(6, 19, 2):
            if row[i] != '' and row[i] != row[i+1]:
                data_test.append([float(row[i]), float(row[i+1]), 'goals ' + str(i//2 - 2.5), row[-1]])

data = np.array(data)

print(data.shape)
# print(sp.stats.shapiro(data[:,0]))
# print(sp.stats.shapiro(data[:,1]))

m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
m1, d1 = np.mean(data[:,1]), np.std(data[:,1])
rate = [1.5, 2.52]
_rate = ((min(rate) - m0)/d0, (fh.calc_equilibrium(rate[0], rate[1]) - m1)/d1)
print(_rate)

positive, ct = 0, 0
for k in range(data.shape[0]):
    data[k,0] -= m0
    data[k,0] /= d0
    data[k,1] -= m1
    data[k,1] /= d1
    if ((data[k,0] - _rate[0]) ** 2 + (data[k,1] - _rate[1]) ** 2) ** 0.5 <= 1:
        if ((data[k,0] - _rate[0]) ** 2 + (data[k,1] - _rate[1]) ** 2) ** 0.5 <= 0.4:
            if data[k,2] == 1: positive += 1
            ct += 1
        if data[k,2] == 0:
            plt.scatter(data[k,0], data[k,1], c='r', marker='+')
        else:
            plt.scatter(data[k,0], data[k,1], c='b', marker='x')

theta = np.linspace(0, 2*np.pi, 100)
r = 0.4
x1 = r*np.cos(theta)+_rate[0]
x2 = r*np.sin(theta)+_rate[1]
plt.scatter(x1, x2, c='b', s=0.1)
plt.scatter(_rate[0], _rate[1], c='k')
plt.grid(linestyle='--')
plt.xlim(_rate[0]-0.6, _rate[0]+0.6)
plt.ylim(_rate[1]-0.45, _rate[1]+0.45)
print(positive, ct, sm.proportion_confint(positive, ct), positive/ct)
plt.show()

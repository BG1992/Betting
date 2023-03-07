import csv
import statsmodels.stats.proportion as sm
import numpy as np
import fortuna_helper as fh
import os

data = []
data_path = 'C://Users//Marzena//Documents//fortuna 20112020.csv'
with open(data_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        _score = fh.get_score(row[-1])
        data.append(fh.new_bet2(float(row[0]), float(row[4]), bet='1', score=_score))
        data.append(fh.new_bet2(float(row[1]), float(row[5]), bet='0', score=_score))
        data.append(fh.new_bet2(float(row[2]), float(row[3]), bet='2', score=_score))
        data.append(fh.new_bet2(float(row[0]), float(row[4]), bet='02', score=_score))
        data.append(fh.new_bet2(float(row[1]), float(row[5]), bet='12', score=_score))
        data.append(fh.new_bet2(float(row[2]), float(row[3]), bet='10', score=_score))
        if row[6] != '':
            data.append(fh.new_bet2(float(row[6]), float(row[7]), bet='goals -', score=_score, under=0.5))
            data.append(fh.new_bet2(float(row[6]), float(row[7]), bet='goals +', score=_score, under=0.5))
        if row[8] != '':
            data.append(fh.new_bet2(float(row[8]), float(row[9]), bet='goals -', score=_score, under=1.5))
            data.append(fh.new_bet2(float(row[8]), float(row[9]), bet='goals +', score=_score, under=1.5))
        if row[10] != '':
            data.append(fh.new_bet2(float(row[10]), float(row[11]), bet='goals -', score=_score, under=2.5))
            data.append(fh.new_bet2(float(row[10]), float(row[11]), bet='goals +', score=_score, under=2.5))
        if row[12] != '':
            data.append(fh.new_bet2(float(row[12]), float(row[13]), bet='goals -', score=_score, under=3.5))
            data.append(fh.new_bet2(float(row[12]), float(row[13]), bet='goals +', score=_score, under=3.5))
        if row[14] != '':
            data.append(fh.new_bet2(float(row[14]), float(row[15]), bet='goals -', score=_score, under=4.5))
            data.append(fh.new_bet2(float(row[14]), float(row[15]), bet='goals +', score=_score, under=4.5))
        if row[16] != '':
            data.append(fh.new_bet2(float(row[16]), float(row[17]), bet='goals -', score=_score, under=5.5))
            data.append(fh.new_bet2(float(row[16]), float(row[17]), bet='goals +', score=_score, under=5.5))
        if row[18] != '':
            data.append(fh.new_bet2(float(row[18]), float(row[19]), bet='goals -', score=_score, under=6.5))
            data.append(fh.new_bet2(float(row[18]), float(row[19]), bet='goals +', score=_score, under=6.5))

data = np.array(data)
m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
m1, d1 = np.mean(data[:,1]), np.std(data[:,1])

for k in range(data.shape[0]):
    data[k,0] -= m0
    data[k,0] /= d0
    data[k,1] -= m1
    data[k,1] /= d1

def sort_radius(x):
    return (x[2][0] * (x[0][0] - 1) - (1 - x[2][0]))

def knn_radius(rate, radius, details):
    ct = 0
    q = []
    _rate = ((rate[0] - m0)/d0, (rate[1] - m1)/d1)
    for row in data:
        dist = ((row[0] - _rate[0])**2 + (row[1] - _rate[1])**2)**0.5
        q.append((dist, row[2], details))
    q.sort(key=lambda x: x[0])
    i = 0
    while q[i][0] <= radius:
        if q[i][1] == 1: ct += 1
        i += 1
    return ct, i

directory = 'C://Users//Marzena//Documents//'

main_ct = 0
main_positive = 0
main_score = 0
_alpha = 0.01
radius = 0.1
print('File;Positive;Ct;Ewk;p_lower;p_mid;p_upper;ev')
for data_test_path in os.listdir(directory):
    if 'test.csv' in data_test_path and '21112020' not in data_test_path:
        data_test = []
        with open(directory + data_test_path, newline='') as datafile:
            reader = csv.reader(datafile, delimiter=';')
            header = next(reader)
            for row in reader:
                data_test.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[4])), '1', row[-2], row[-1]])
                data_test.append([float(row[1]), fh.calc_equilibrium(float(row[1]), float(row[5])), '0', row[-2], row[-1]])
                data_test.append([float(row[2]), fh.calc_equilibrium(float(row[2]), float(row[3])), '2', row[-2], row[-1]])
                data_test.append([float(row[4]), fh.calc_equilibrium(float(row[0]), float(row[4])), '02', row[-2], row[-1]])
                data_test.append([float(row[5]), fh.calc_equilibrium(float(row[1]), float(row[5])), '12', row[-2], row[-1]])
                data_test.append([float(row[3]), fh.calc_equilibrium(float(row[2]), float(row[3])), '10', row[-2], row[-1]])
                for i in range(6, 19, 2):
                    if row[i] != '' and row[i] != row[i+1]:
                        data_test.append([float(row[i]), fh.calc_equilibrium(float(row[i]), float(row[i+1])),
                                          'goals -' + str(i//2 - 2.5), row[-2], row[-1]])
                        data_test.append([float(row[i+1]), fh.calc_equilibrium(float(row[i]), float(row[i+1])),
                                          'goals +' + str(i//2 - 2.5), row[-2], row[-1]])

        matches = {}
        radius_sorted = []
        for row in data_test:
            _knn3 = knn_radius((row[0], row[1]), radius, row[2])
            if _knn3[1] > 40 and row[0] > 1.35 and row[1] > -0.09:
                if row[-2] not in matches:
                    matches[row[-2]] = [row[:], _knn3, sm.proportion_confint(_knn3[0], _knn3[1], alpha=_alpha)][:]
                else:
                    p_new = sm.proportion_confint(_knn3[0], _knn3[1], alpha=_alpha)[0]
                    p_old = matches[row[-2]][2][0]
                    if p_new*(row[0]-1) - (1-p_new) > p_old*(matches[row[-2]][0][0]-1) - (1-p_old):
                        matches[row[-2]] = [row[:], _knn3, sm.proportion_confint(_knn3[0], _knn3[1], alpha=_alpha)][:]

        for row in matches:
            radius_sorted.append(matches[row])

        radius_sorted.sort(key= lambda x: -sort_radius(x))
        p_lower = 1
        p_mid = 1
        p_upper = 1
        ewk = 1
        positive = 0
        ct = 0

        for r in radius_sorted[:3]:
            #print(r, r[1][0]/r[1][1])
            p_lower *= r[2][0]
            p_mid *= r[1][0]/r[1][1]
            p_upper *= r[2][1]
            ewk *= r[0][0]
            positive += fh.check_bet(r[0][2], fh.get_score(r[0][-1]))
            ct += 1
        ev = round(p_lower*(ewk*0.88*1.14 - 1) - (1-p_lower), 4)
        print(str(data_test_path) + ';' + str(positive) + ';' + str(ct) + ';' +
              str(round((ewk-1)*(positive == ct) - 1*(positive != ct), 4)) + ';' +
              str(round(p_lower, 4)) + ';' + str(round(p_mid, 4)) + ';' +
              str(round(p_upper, 4)) + ';' + str(round(ev, 4)))
        # print('frac =', str(positive) + '/' + str(ct), ';ewk =', round((ewk-1)*(positive == ct) - 1*(positive != ct), 4),
        #       ';p_lower =', round(p_lower, 4), ';p_mid =', round(p_mid, 4), ';p_upper =', round(p_upper, 4),
        #       ';ev =', round(p_lower*(ewk*0.88*1.14 - 1) - (1-p_lower), 4))
        main_positive += int(positive==ct)
        main_ct += 1
        main_score += (ewk-1)*(positive == ct) - 1*(positive != ct)
    # print('alpha =', _alpha)
    # print('radius =', radius)
    # print('p_lower =', p_lower)
    # print('p_mid =', p_mid)
    # print('p_upper =', p_upper)
    # print('ewk =', ewk*0.88*1.14)
    # print('ev_lower =', p_lower*(ewk*0.88*1.14 - 1) - (1-p_lower))
    # print('ev_mid =', p_mid*(ewk*0.88*1.14 - 1) - (1-p_mid))
    # print('ev_upper =', p_upper*(ewk*0.88*1.14 - 1) - (1-p_upper))

# for row in radius_sorted:
#     print(row)

print('frac = ', str(main_positive) + '/' + str(main_ct), 'main_score =' + str(main_score),
      'radius =', str(radius), 'alpha =', str(_alpha))
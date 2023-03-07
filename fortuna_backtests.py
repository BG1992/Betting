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
# m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
# m1, d1 = np.mean(data[:,1]), np.std(data[:,1])

# for k in range(data.shape[0]):
#     data[k,0] -= m0
#     data[k,0] /= d0
#     data[k,1] -= m1
#     data[k,1] /= d1

def sort_matches(x):
    return x[1][-1]

def knn_sm_area(rate, a=0.01):
    #_rate = ((rate[0] - m0)/d0, (rate[1] - m1)/d1)
    positive = 0
    ct = 0
    sm_plus = 0
    sm_minus = 0
    for row in data:
        if abs(row[0] - rate[0]) <= 0.03 and abs(row[1] - rate[1]) <= 0.002:
            if row[2] == 1:
                positive += 1
                sm_plus += (rate[0]-1)
            else:
                sm_minus += 1
            ct += 1
    if ct < 15: return positive, ct, (0, 1), -100
    s = sm.proportion_confint(positive, ct, a)
    return positive, ct, s, (sm_plus*s[0] - sm_minus*(1-s[0]))/ct

directory = 'C://Users//Marzena//Documents//'

main_ct = 0
main_positive = 0
main_score = 0
_alpha = 0.01

print('File;Positive;Ct;Ewk;p_lower;p_mid;p_upper;ev')
for data_test_path in os.listdir(directory):
    if 'test.csv' in data_test_path and '22112020' not in data_test_path \
            and '25112020' not in data_test_path\
            and '28112020' not in data_test_path\
            and '29112020' not in data_test_path:
        data_test = []
        with open(directory + data_test_path, newline='') as datafile:
            reader = csv.reader(datafile, delimiter=';')
            header = next(reader)
            for row in reader:
                # data_test.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[4])), '1', row[-2], row[-1]])
                # data_test.append([float(row[1]), fh.calc_equilibrium(float(row[1]), float(row[5])), '0', row[-2], row[-1]])
                # data_test.append([float(row[2]), fh.calc_equilibrium(float(row[2]), float(row[3])), '2', row[-2], row[-1]])
                # data_test.append([float(row[4]), fh.calc_equilibrium(float(row[0]), float(row[4])), '02', row[-2], row[-1]])
                # data_test.append([float(row[5]), fh.calc_equilibrium(float(row[1]), float(row[5])), '12', row[-2], row[-1]])
                # data_test.append([float(row[3]), fh.calc_equilibrium(float(row[2]), float(row[3])), '10', row[-2], row[-1]])
                for i in range(6, 19, 2):
                    if row[i] != '' and row[i] != row[i+1]:
                        data_test.append([float(row[i]), fh.calc_equilibrium(float(row[i]), float(row[i+1])),
                                          'goals -' + str(i//2 - 2.5), row[-2], row[-1]])
                        data_test.append([float(row[i+1]), fh.calc_equilibrium(float(row[i]), float(row[i+1])),
                                          'goals +' + str(i//2 - 2.5), row[-2], row[-1]])

        matches = {}
        matches_sorted = []
        for row in data_test:
            if row[0] > 1.3:
                _knn3 = knn_sm_area((row[0], row[1]))
                if row[-1] not in matches:
                    matches[row[-1]] = [row[:], _knn3][:]
                else:
                    if _knn3[-1] > matches[row[-1]][-1][-1]:
                        matches[row[-1]] = [row[:], _knn3][:]

        for row in matches:
            matches_sorted.append(matches[row])

        matches_sorted.sort(key= lambda x: -sort_matches(x))
        p_lower = 1
        p_mid = 1
        p_upper = 1
        ewk = 1
        positive = 0
        ct = 0

        for r in matches_sorted[:3]:
            #print(r, r[1][0] / r[1][1])
            p_lower *= r[1][2][0]
            p_mid *= r[1][0] / r[1][1]
            p_upper *= r[1][2][1]
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

print('frac = ', str(main_positive) + '/' + str(main_ct), 'main_score =' + str(main_score),
        'alpha =', str(_alpha))
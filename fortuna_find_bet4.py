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

data_test = []
data_test_path = 'C://Users//Marzena//Documents//fortuna 29112020 test.csv'
with open(data_test_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        # data_test.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[4])), '1', row[-1]])
        # data_test.append([float(row[1]), fh.calc_equilibrium(float(row[1]), float(row[5])), '0', row[-1]])
        # data_test.append([float(row[2]), fh.calc_equilibrium(float(row[2]), float(row[3])), '2', row[-1]])
        # data_test.append([float(row[4]), fh.calc_equilibrium(float(row[0]), float(row[4])), '02', row[-1]])
        # data_test.append([float(row[5]), fh.calc_equilibrium(float(row[1]), float(row[5])), '12', row[-1]])
        # data_test.append([float(row[3]), fh.calc_equilibrium(float(row[2]), float(row[3])), '10', row[-1]])
        for i in range(6, 19, 2):
            if row[i] != '' and row[i] != row[i+1]:
                data_test.append([float(row[i]), fh.calc_equilibrium(float(row[i]), float(row[i+1])),
                                  'goals -' + str(i//2 - 2.5), row[-1]])
                data_test.append([float(row[i+1]), fh.calc_equilibrium(float(row[i]), float(row[i+1])),
                                  'goals +' + str(i//2 - 2.5), row[-1]])

data = np.array(data)

print(data.shape)

def sort_matches(x):
    return x[1][-1]

matches = {}
matches_sorted = []
_alpha = 0.01
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
for r in matches_sorted[:3]:
    print(r, r[1][0]/r[1][1])
    p_lower *= r[1][2][0]
    p_mid *= r[1][0]/r[1][1]
    p_upper *= r[1][2][1]
    ewk *= r[0][0]

print('alpha =', _alpha)
print('p_lower = ', p_lower)
print('p_mid = ', p_mid)
print('p_upper = ', p_upper)
print('ewk = ', ewk*0.88*1.14)
print('ev_lower = ', p_lower*(ewk*0.88*1.14 - 1) - (1-p_lower))
print('ev_mid = ', p_mid*(ewk*0.88*1.14 - 1) - (1-p_mid))
print('ev_upper = ', p_upper*(ewk*0.88*1.14 - 1) - (1-p_upper))

# for row in radius_sorted:
#     print(row)

# po uzyskaniu większej ilości rekordów dodać taki test:
# znajdź n-kąt (+ liczba betów) taki że stosunek
# pozytywnych wyników do wszystkich wyników daje prawdopodobieństwo, które:
# dla 70% dni z najwyższym ev,
# abs(średnie estymowane prawdopodobieństwo - stosunek dni wygranych do wszystkich dni z tych 70%)
# podzielić przez średnie ewk jest najmniejsze, przy estymowanym prawdopodobieństwie > 0.
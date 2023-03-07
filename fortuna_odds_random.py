import csv
import statsmodels.stats.proportion as sm
from statistics import mean, stdev
from random import uniform

def get_score(score):
    left = int(score[:score.index('--')])
    right = int(score[score.index('--')+2:])
    return [left, right]

def format_row(row):
    _row = []
    for el in row:
        if el == '':
            _row.append(0)
        else:
            _row.append(float(el))
    return _row

def calc_equilibrium(left, right):
    p = ((right-1)*0.88+1)/((left-1)*0.88+1+(right-1)*0.88+1)
    return (left-1)*0.88*p - (1-p)

data = []

with open('C://Users//Marzena//Documents//fortuna 04112020.csv', newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        score = get_score(row[-1])
        data.append([float(row[0]), float(row[4]), 'L' if score[0] > score[1] else 'R'])
        data.append([float(row[1]), float(row[5]), 'L' if score[0] == score[1] else 'R'])
        data.append([float(row[2]), float(row[3]), 'L' if score[0] < score[1] else 'R'])
        if row[6] != '': data.append([float(row[6]), float(row[7]), 'L' if sum(score) < 0.5 else 'R'])
        if row[8] != '': data.append([float(row[8]), float(row[9]), 'L' if sum(score) < 1.5 else 'R'])
        if row[10] != '': data.append([float(row[10]), float(row[11]), 'L' if sum(score) < 2.5 else 'R'])
        if row[12] != '': data.append([float(row[12]), float(row[13]), 'L' if sum(score) < 3.5 else 'R'])
        if row[14] != '': data.append([float(row[14]), float(row[15]), 'L' if sum(score) < 4.5 else 'R'])
        if row[16] != '': data.append([float(row[16]), float(row[17]), 'L' if sum(score) < 5.5 else 'R'])
        if row[18] != '': data.append([float(row[18]), float(row[19]), 'L' if sum(score) < 6.5 else 'R'])

max_minim = 0
max_ranges = []
max_equilibrium = []

sim = 0
while sim < 100000:
    minim_left = uniform(1.5, 2)
    minim_right = uniform(minim_left, 2)
    minim = [minim_left, minim_right]
    eq_left = uniform(-0.15, -0.05)
    eq_right = uniform(eq_left, -0.05)
    equilibrium = [eq_left, eq_right]
    rates = []
    positive = 0
    ct = 0

    ind = 0
    for row in data:
        if min(row[:2]) >= minim[0] and min(row[:2]) <= minim[1] and row[0] != row[1]:
            eq = calc_equilibrium(row[0], row[1])
            if eq >= equilibrium[0] and eq <= equilibrium[1]:
                if min(row[:2]) == row[0]:
                    if row[2] == 'L':
                        rates.append(row[0])
                        positive += 1
                        #print(ind, row)
                else:
                    if row[2] == 'R':
                        rates.append(row[1])
                        positive += 1
                        #print(ind, row)
                ct += 1
        ind += 1
    if ct > 50:
        if sm.proportion_confint(positive, ct)[0] > max_minim:
            max_minim = sm.proportion_confint(positive, ct)[0]
            max_ranges = minim[:]
            max_equilibrium = equilibrium[:]
            print(sim, max_minim, max_ranges, max_equilibrium, positive, ct, positive/ct, sm.proportion_confint(positive, ct))
        sim += 1
    if sim % 10000 == 0: print(sim)
    # print(positive, ct, positive/ct)
    # print(sm.proportion_confint(positive, ct))
    # print(mean(rates), stdev(rates))
    #
    # print(calc_equilibrium(1.89, 2.01))
    # print(calc_equilibrium(1.72, 2.25))
    # print(calc_equilibrium(1.32, 3.7))
    # print(calc_equilibrium(1.46, 3.0))

print(max_minim)
print(max_ranges)
print(max_equilibrium)
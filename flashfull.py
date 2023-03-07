import csv
from collections import defaultdict
from statistics import mean, stdev

def get_score(score):
    ind = score.index('-')
    return (int(score[:ind - 1]), int(score[ind + 2:]))
    #return int(score[:ind-1]) + int(score[ind+2:])

data = defaultdict(dict)
with open('flashfull.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    ct = 0
    for row in _reader:
        _score = get_score(row[2])
        if _score not in data[(row[0], row[1])]:
            data[(row[0], row[1])][_score] = 1
        else:
            data[(row[0], row[1])][_score] += 1

counts = []

for row in data:
    ct = 0
    for el in data[row]:
        if sum(el) < 2.5:
            ct += data[row][el]
    print(row, ct, sum(data[row].values()))
    counts.append(ct / sum(data[row].values()))

print(mean(counts), stdev(counts))
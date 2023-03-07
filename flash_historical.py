import csv

data = []
with open('flashscore_nodups.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    ct = 0
    for row in _reader:
        details = row[0].split('\n')
        for i in range(len(details)):
            if '-' in details[i]:
                break
        if len(details[i-1]) == 1 and len(details[i+1]) == 1:
            score = (int(details[i-1]), int(details[i+1]))
            if score[0] > score[1]: _score = 1
            elif score[0] == score[1]: _score = 0
            else: _score = 2
            ind = row[1].index('x')
            rate1 = float(row[1][ind+3:ind+7])
            ind = row[2].index('x')
            rate0 = float(row[2][ind+3:ind+7])
            ind = row[3].index('x')
            rate2 = float(row[3][ind+3:ind+7])
            data.append([rate1, rate0, rate2, _score])

with open('flashscore_matches.csv', 'a', newline='') as csvfile:
    _writer = csv.writer(csvfile, delimiter=';')
    for row in data:
        _writer.writerow(row)
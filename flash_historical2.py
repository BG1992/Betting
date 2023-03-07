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

            for bound in ['0.5', '1.5', '2.5', '3.5', '4.5', '5.5', '6.5']:
                if sum(score) < float(bound): _score = 'u'
                else: _score = 'o'
                for j in range(len(row)):
                    if 'eFortuna.pl odds_ou_' + bound in row[j]: break
                try:
                    under = float(row[j][row[j].index(bound)+4:row[j].index(bound)+8])
                    over = float(row[j+1][row[j+1].index(bound)+4:row[j+1].index(bound)+8])
                    data.append([under, over, _score])
                except: pass

with open('flashscore_ous.csv', 'a', newline='') as csvfile:
    _writer = csv.writer(csvfile, delimiter=';')
    for row in data:
        _writer.writerow(row)